#!/usr/bin/env python3
"""
Fast SBOE CSV → Supabase Postgres loader using COPY.
Processes all 4 SBOE election files and loads via psycopg2 copy_expert().

Duplicate protection:
  - results table has UNIQUE (election_id, race_id, precinct_id, candidate_id)
  - turnout table has UNIQUE (election_id, precinct_id)
  - This loader uses temp-table + INSERT ON CONFLICT to safely handle re-runs
  - ALWAYS refresh mv_race_precinct_results after loading
"
import csv
import hashlib
import io
import os
import re
import sys
import time
import psycopg2

csv.field_size_limit(1_000_000)

# ── Connection ──────────────────────────────────────────────
DB_URI = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres.nfjfqdffulhqhszhlymo:D4dHeatmap2026!Pg"
    "@aws-0-us-west-2.pooler.supabase.com:5432/postgres"
)

# ── Helpers ─────────────────────────────────────────────────
def safe_int(val):
    """Safely convert a value to int, returning 0 on failure."""
    try:
        return int(val or 0)
    except (ValueError, TypeError):
        return 0


def make_id(*parts):
    raw = "|".join(str(p).strip().lower() for p in parts)
    return hashlib.md5(raw.encode()).hexdigest()[:16]

def classify_contest(c):
    """Map SBOE contest name → (district_type_id, district_number)."""
    c = c.strip().upper()
    if not c:
        return None

    if 'PRESIDENT' in c and ('UNITED STATES' in c or 'PRESIDENT AND' in c or c == 'PRESIDENT'):
        return ('president', 0)
    if 'U.S. SENATOR' in c or 'UNITED STATES SENATOR' in c:
        return ('us_senate', 0)
    # Check for "GOVERNOR AND LIEUTENANT GOVERNOR" BEFORE the lt_governor check
    if 'GOVERNOR AND LIEUTENANT GOVERNOR' in c:
        return ('governor', 0)
    if re.match(r'^GOVERNOR\b', c) and 'LT' not in c and 'LIEUTENANT' not in c:
        return ('governor', 0)
    if 'LIEUTENANT GOVERNOR' in c or 'LT. GOVERNOR' in c:
        return ('lt_governor', 0)
    if 'ATTORNEY GENERAL' in c: return ('attorney_general', 0)
    if 'SECRETARY OF STATE' in c: return ('secretary_of_state', 0)
    if 'COMPTROLLER' in c: return ('comptroller', 0)
    if 'TREASURER' in c and 'CITY' not in c: return ('treasurer_state', 0)

    m = re.match(r'(\d+)\w*\s+CONGRESS', c)
    if m: return ('congress', int(m.group(1)))
    m = re.match(r'(\d+)\w*\s+SENATE', c)
    if m: return ('state_senate', int(m.group(1)))
    m = re.match(r'(\d+)\w*\s+REPRESENTATIVE', c)
    if m: return ('state_rep', int(m.group(1)))

    if 'SUPREME' in c:
        m = re.match(r'(\d+)\w*\s+SUPREME', c)
        return ('supreme_court', int(m.group(1)) if m else 1)
    if 'APPELLATE' in c:
        m = re.match(r'(\d+)\w*\s+APPELLATE', c)
        return ('appellate_court', int(m.group(1)) if m else 1)
    if 'SUBCIRCUIT' in c or 'SUB-CIRCUIT' in c:
        m = re.search(r'(\d+)\w*\s+SUB', c)
        if m: return ('subcircuit', int(m.group(1)))
        m = re.search(r'(\d+)', c)
        if m: return ('subcircuit', int(m.group(1)))
    if 'CIRCUIT' in c and 'SUB' not in c:
        return ('circuit_court', 0)

    if 'BOARD PRESIDENT' in c or 'COUNTY PRESIDENT' in c:
        return ('cook_president', 0)
    m = re.search(r'(\d+)\w*\s+(COUNTY\s+)?COMMISSIONER', c)
    if m: return ('cook_commissioner', int(m.group(1)))
    if 'WATER RECLAMATION' in c or 'MWRD' in c: return ('mwrd', 0)

    if 'STATE CENTRAL' in c or 'COMMITTEEMAN' in c or 'COMMITTEEWOMAN' in c:
        m = re.search(r'(\d+)', c)
        return ('state_central_comm', int(m.group(1)) if m else 0)
    if 'DELEGATE' in c:
        m = re.search(r'(\d+)', c)
        return ('delegate', int(m.group(1)) if m else 0)

    # Ballot questions / referenda / anything else
    return ('referendum', 0)


def parse_precinct(name):
    m = re.match(r'Ward\s+(\d+)\s+Precinct\s+(\d+)', name, re.IGNORECASE)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r'(\d+)\s*$', name)
    if m:
        return None, int(m.group(1))
    return None, None


# ── Phase 1: Scan all CSVs and collect dimensions ──────────
def scan_sboe(filepath, election_id, label):
    """Single-pass scan: collect precincts, districts, races, candidates, results, turnout."""
    precincts = {}
    districts = {}
    races = {}
    candidates = {}
    results = []
    turnout = []
    pd_set = set()

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        n = 0
        for row in reader:
            n += 1
            contest = row.get('ContestName', '').strip()
            pname = row.get('PrecinctName', '').strip()
            cand = row.get('CandidateName', '').strip()
            party = row.get('PartyName', '').strip()
            votes = safe_int(row.get('VoteCount', 0))
            reg = safe_int(row.get('Registration', 0))
            juris = row.get('JurisName', '').strip()

            jid = 'chicago' if 'CHICAGO' in juris.upper() else 'cook_suburban'
            pid = make_id(jid, pname)
            ward, pnum = parse_precinct(pname)

            if pid not in precincts and pname:
                precincts[pid] = (pid, jid, pname, ward, pnum)

            # Turnout row
            if not contest:
                if reg > 0:
                    tpct = round(votes / reg * 100, 2) if reg > 0 else 0
                    turnout.append((election_id, pid, reg, votes, tpct, label, pname))
                continue

            cls = classify_contest(contest)
            if cls is None:
                continue
            dt_id, dt_num = cls

            did = make_id(dt_id, dt_num)
            if did not in districts:
                dname = f"{dt_id.replace('_', ' ').title()} {dt_num}" if dt_num else dt_id.replace('_', ' ').title()
                districts[did] = (did, dt_id, dt_num, dname)

            rid = make_id(election_id, contest)
            if rid not in races:
                races[rid] = (rid, election_id, did, contest, contest, dt_id)

            pd_key = (pid, did)
            if pd_key not in pd_set:
                pd_set.add(pd_key)

            if not cand:
                continue

            cid = make_id(cand, party)
            if cid not in candidates:
                candidates[cid] = (cid, cand, party)

            results.append((election_id, pid, rid, cid, votes, label, contest, pname, cand))

    print(f"  {label}: {n:,} rows → {len(results):,} results, {len(turnout):,} turnout, {len(races)} races")
    return precincts, districts, races, candidates, results, turnout, pd_set


def copy_tuples(cur, table, columns, rows):
    """Use COPY FROM STDIN to bulk-load a list of tuples."""
    if not rows:
        return 0
    buf = io.StringIO()
    for row in rows:
        line = '\t'.join('' if v is None else str(v) for v in row)
        buf.write(line + '\n')
    buf.seek(0)
    cols = ', '.join(columns)
    cur.copy_expert(f"COPY {table} ({cols}) FROM STDIN WITH (FORMAT text, NULL '')", buf)
    return len(rows)


# ── Main ────────────────────────────────────────────────────
def main():
    DATA_DIR = os.environ.get('DATA_DIR', '/home/user/workspace')

    sboe_files = [
        (f"{DATA_DIR}/chicago_cook_2022GP.csv", "2022_primary", "SBOE 2022 Primary - Chicago"),
        (f"{DATA_DIR}/chicago_cook_2022GE.csv", "2022_general", "SBOE 2022 General - Chicago"),
        (f"{DATA_DIR}/chicago_cook_2024GP.csv", "2024_primary", "SBOE 2024 Primary - Chicago"),
        (f"{DATA_DIR}/chicago_cook_2024GE.csv", "2024_general", "SBOE 2024 General - Chicago"),
    ]

    # ── Scan all files ──
    print("=" * 60)
    print("SCANNING SBOE CSVs")
    print("=" * 60)
    t0 = time.time()

    all_p, all_d, all_r, all_c = {}, {}, {}, {}
    all_results, all_turnout = [], []
    all_pd = set()

    for path, eid, label in sboe_files:
        p, d, r, c, res, to, pd = scan_sboe(path, eid, label)
        all_p.update(p)
        all_d.update(d)
        all_r.update(r)
        all_c.update(c)
        all_results.extend(res)
        all_turnout.extend(to)
        all_pd.update(pd)

    scan_time = time.time() - t0
    print(f"\nScan complete in {scan_time:.1f}s")
    print(f"  Precincts: {len(all_p):,}")
    print(f"  Districts: {len(all_d):,}")
    print(f"  Races:     {len(all_r):,}")
    print(f"  Candidates:{len(all_c):,}")
    print(f"  Results:   {len(all_results):,}")
    print(f"  Turnout:   {len(all_turnout):,}")
    print(f"  PD maps:   {len(all_pd):,}")

    # ── Connect to Postgres ──
    print(f"\nConnecting to Supabase Postgres...")
    conn = psycopg2.connect(DB_URI, connect_timeout=30)
    conn.autocommit = False
    cur = conn.cursor()

    # ── Idempotent: Delete existing data for these election_ids before reload ──
    election_ids = ('2022_primary', '2022_general', '2024_primary', '2024_general')
    ids_placeholder = ', '.join(f"'{eid}'" for eid in election_ids)
    print(f"\nClearing existing results and turnout for elections: {election_ids}")
    cur.execute(f"DELETE FROM results WHERE election_id IN ({ids_placeholder});")
    deleted_results = cur.rowcount
    cur.execute(f"DELETE FROM turnout WHERE election_id IN ({ids_placeholder});")
    deleted_turnout = cur.rowcount
    conn.commit()
    print(f"  Deleted {deleted_results:,} results, {deleted_turnout:,} turnout rows")

    cur.close()
    conn.close()
    # Reconnect fresh after cleanup
    conn = psycopg2.connect(DB_URI, connect_timeout=30)
    conn.autocommit = False
    cur = conn.cursor()

    # Disable triggers for speed
    cur.execute("SET statement_timeout = 0;")

    # ── Load reference tables (upsert via temp table pattern) ──
    print("\n" + "=" * 60)
    print("LOADING VIA COPY")
    print("=" * 60)

    # Districts
    print(f"\n--- Districts ({len(all_d)}) ---")
    cur.execute("CREATE TEMP TABLE tmp_districts (LIKE districts INCLUDING ALL) ON COMMIT DROP;")
    n = copy_tuples(cur, "tmp_districts", ["id", "district_type_id", "number", "name"], list(all_d.values()))
    cur.execute("""
        INSERT INTO districts (id, district_type_id, number, name)
        SELECT id, district_type_id, number, name FROM tmp_districts
        ON CONFLICT (id) DO UPDATE SET
            district_type_id = EXCLUDED.district_type_id,
            number = EXCLUDED.number,
            name = EXCLUDED.name;
    """)
    conn.commit()
    print(f"  Loaded {n}")

    # Precincts
    print(f"\n--- Precincts ({len(all_p)}) ---")
    cur.execute("CREATE TEMP TABLE tmp_precincts (LIKE precincts INCLUDING ALL) ON COMMIT DROP;")
    n = copy_tuples(cur, "tmp_precincts",
                    ["id", "jurisdiction_id", "source_precinct_name", "ward", "precinct_number"],
                    list(all_p.values()))
    cur.execute("""
        INSERT INTO precincts (id, jurisdiction_id, source_precinct_name, ward, precinct_number)
        SELECT id, jurisdiction_id, source_precinct_name, ward, precinct_number FROM tmp_precincts
        ON CONFLICT (id) DO UPDATE SET
            jurisdiction_id = EXCLUDED.jurisdiction_id,
            source_precinct_name = EXCLUDED.source_precinct_name,
            ward = EXCLUDED.ward,
            precinct_number = EXCLUDED.precinct_number;
    """)
    conn.commit()
    print(f"  Loaded {n}")

    # Races
    print(f"\n--- Races ({len(all_r)}) ---")
    cur.execute("CREATE TEMP TABLE tmp_races (LIKE races INCLUDING ALL) ON COMMIT DROP;")
    n = copy_tuples(cur, "tmp_races",
                    ["id", "election_id", "district_id", "name", "source_contest_name", "race_type"],
                    list(all_r.values()))
    cur.execute("""
        INSERT INTO races (id, election_id, district_id, name, source_contest_name, race_type)
        SELECT id, election_id, district_id, name, source_contest_name, race_type FROM tmp_races
        ON CONFLICT (id) DO UPDATE SET
            election_id = EXCLUDED.election_id,
            district_id = EXCLUDED.district_id,
            name = EXCLUDED.name,
            source_contest_name = EXCLUDED.source_contest_name,
            race_type = EXCLUDED.race_type;
    """)
    conn.commit()
    print(f"  Loaded {n}")

    # Candidates
    print(f"\n--- Candidates ({len(all_c)}) ---")
    cur.execute("CREATE TEMP TABLE tmp_cands (LIKE candidates INCLUDING ALL) ON COMMIT DROP;")
    n = copy_tuples(cur, "tmp_cands", ["id", "name", "party"], list(all_c.values()))
    cur.execute("""
        INSERT INTO candidates (id, name, party)
        SELECT id, name, party FROM tmp_cands
        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, party = EXCLUDED.party;
    """)
    conn.commit()
    print(f"  Loaded {n}")

    # Precinct-District mappings
    pd_rows = [(pid, did, "SBOE") for (pid, did) in all_pd]
    print(f"\n--- Precinct-Districts ({len(pd_rows)}) ---")
    cur.execute("CREATE TEMP TABLE tmp_pd (precinct_id text, district_id text, source_file text) ON COMMIT DROP;")
    n = copy_tuples(cur, "tmp_pd", ["precinct_id", "district_id", "source_file"], pd_rows)
    cur.execute("""
        INSERT INTO precinct_districts (precinct_id, district_id, source_file)
        SELECT precinct_id, district_id, source_file FROM tmp_pd
        ON CONFLICT (precinct_id, district_id) DO NOTHING;
    """)
    conn.commit()
    print(f"  Loaded {n}")

    # Results (the big one) — use temp table + ON CONFLICT to prevent duplicates
    print(f"\n--- Results ({len(all_results):,}) ---")
    t1 = time.time()
    CHUNK = 200_000
    loaded = 0
    for i in range(0, len(all_results), CHUNK):
        chunk = all_results[i:i+CHUNK]
        cur.execute("""CREATE TEMP TABLE tmp_results (
            election_id text, precinct_id text, race_id text, candidate_id text,
            votes integer, source_file text, source_contest_name text,
            source_precinct_name text, source_candidate_name text
        ) ON COMMIT DROP;""")
        n = copy_tuples(cur, "tmp_results",
                        ["election_id", "precinct_id", "race_id", "candidate_id", "votes",
                         "source_file", "source_contest_name", "source_precinct_name",
                         "source_candidate_name"],
                        chunk)
        cur.execute("""
            INSERT INTO results (election_id, precinct_id, race_id, candidate_id, votes,
                                 source_file, source_contest_name, source_precinct_name,
                                 source_candidate_name)
            SELECT election_id, precinct_id, race_id, candidate_id, votes,
                   source_file, source_contest_name, source_precinct_name,
                   source_candidate_name
            FROM tmp_results
            ON CONFLICT (election_id, race_id, precinct_id, candidate_id)
            DO UPDATE SET votes = EXCLUDED.votes,
                          source_file = EXCLUDED.source_file,
                          source_contest_name = EXCLUDED.source_contest_name,
                          source_precinct_name = EXCLUDED.source_precinct_name,
                          source_candidate_name = EXCLUDED.source_candidate_name;
        """)
        conn.commit()
        loaded += n
        elapsed = time.time() - t1
        print(f"  Chunk {i//CHUNK + 1}: {loaded:,} / {len(all_results):,}  ({elapsed:.1f}s)")

    t2 = time.time()
    print(f"  Total loaded: {loaded:,} in {t2-t1:.1f}s")

    # Turnout — use temp table + ON CONFLICT to prevent duplicates
    print(f"\n--- Turnout ({len(all_turnout):,}) ---")
    t1 = time.time()
    cur.execute("""CREATE TEMP TABLE tmp_turnout (
        election_id text, precinct_id text, registered_voters integer,
        ballots_cast integer, turnout_pct numeric, source_file text,
        source_precinct_name text
    ) ON COMMIT DROP;""")
    n = copy_tuples(cur, "tmp_turnout",
                    ["election_id", "precinct_id", "registered_voters", "ballots_cast",
                     "turnout_pct", "source_file", "source_precinct_name"],
                    all_turnout)
    cur.execute("""
        INSERT INTO turnout (election_id, precinct_id, registered_voters, ballots_cast,
                             turnout_pct, source_file, source_precinct_name)
        SELECT election_id, precinct_id, registered_voters, ballots_cast,
               turnout_pct, source_file, source_precinct_name
        FROM tmp_turnout
        ON CONFLICT (election_id, precinct_id)
        DO UPDATE SET registered_voters = EXCLUDED.registered_voters,
                      ballots_cast = EXCLUDED.ballots_cast,
                      turnout_pct = EXCLUDED.turnout_pct,
                      source_file = EXCLUDED.source_file,
                      source_precinct_name = EXCLUDED.source_precinct_name;
    """)
    conn.commit()
    print(f"  Loaded {n:,} in {time.time()-t1:.1f}s")

    # Refresh materialized view
    print("\nRefreshing materialized view...")
    cur.execute("REFRESH MATERIALIZED VIEW mv_race_precinct_results;")
    conn.commit()

    # ANALYZE
    print("Running ANALYZE...")
    cur.execute("ANALYZE;")
    conn.commit()

    cur.close()
    conn.close()

    total_time = time.time() - t0
    print(f"\n{'='*60}")
    print(f"ALL DONE in {total_time:.1f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
