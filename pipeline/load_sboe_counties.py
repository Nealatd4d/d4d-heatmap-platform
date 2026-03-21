#!/usr/bin/env python3
"""
SBOE CSV → Supabase loader for DuPage and DeKalb counties.

Processes precinct-level election results from Illinois State Board of Elections CSVs.
Follows the same pattern as load_sboe.py but adapted for multi-county loading.

DuPage precinct mapping:
  SBOE "Bloomingdale 001-0046" → GeoJSON "Bloomingdale 1" (3-digit seq = GeoJSON number)
  precinct_id = MD5("dupage_county|Bloomingdale 1")[:16]

DeKalb precinct mapping:
  SBOE "AFTON 1" → VTD "AFTON 1" (direct match)
  precinct_id = MD5("dekalb_county|AFTON 1")[:16]
"""

import csv
import hashlib
import io
import os
import re
import sys
import time
import psycopg2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify_race import classify_race_type
from normalize_race import normalize_race_name

csv.field_size_limit(1_000_000)

DB_URI = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres.nfjfqdffulhqhszhlymo:D4dHeatmap2026!Pg"
    "@aws-0-us-west-2.pooler.supabase.com:5432/postgres"
)

# ── Election mapping ────────────────────────────────────────
# Maps CSV filename codes to (election_id, election_name, election_date, election_type, year)
ELECTION_MAP = {
    "2018GE": ("2018_general", "2018 General Election", "2018-11-06", "general", 2018),
    "2018GP": ("2018_primary", "2018 Primary Election", "2018-03-20", "primary", 2018),
    "2020GE": ("2020_general", "2020 General Election", "2020-11-03", "general", 2020),
    "2020GP": ("2020_primary", "2020 Primary Election", "2020-03-17", "primary", 2020),
    "2021CE": ("2021_consolidated", "2021 Consolidated Election", "2021-04-06", "consolidated", 2021),
    "2022GE": ("2022_general", None, None, None, None),  # Already exists
    "2022GP": ("2022_primary", None, None, None, None),   # Already exists
    "2024GE": ("2024_general", None, None, None, None),   # Already exists
    "2024GP": ("2024_primary", None, None, None, None),   # Already exists
}

# ── Helpers ─────────────────────────────────────────────────
def safe_int(val):
    try:
        return int(val or 0)
    except (ValueError, TypeError):
        return 0

def make_id(*parts):
    raw = "|".join(str(p).strip().lower() for p in parts)
    return hashlib.md5(raw.encode()).hexdigest()[:16]

def normalize_dupage_precinct(sboe_name):
    """Convert DuPage SBOE name 'Bloomingdale 001-0046' to GeoJSON name 'Bloomingdale 1'."""
    m = re.match(r'^(.+?)\s+(\d{3})-(\d{4})$', sboe_name)
    if m:
        township = m.group(1)
        seq = int(m.group(2))
        return f"{township} {seq}"
    return sboe_name

def normalize_dekalb_precinct(sboe_name):
    """DeKalb SBOE names match VTD names directly (uppercase)."""
    return sboe_name.upper().strip()

# ── County configs ──────────────────────────────────────────
COUNTIES = {
    "dupage": {
        "jurisdiction_id": "dupage_county",
        "data_dir": None,  # Set at runtime
        "normalize_fn": normalize_dupage_precinct,
        "label_prefix": "SBOE DuPage",
    },
    "dekalb": {
        "jurisdiction_id": "dekalb_county",
        "data_dir": None,  # Set at runtime
        "normalize_fn": normalize_dekalb_precinct,
        "label_prefix": "SBOE DeKalb",
    },
    "lake": {
        "jurisdiction_id": "lake_county",
        "data_dir": None,  # Set at runtime
        "normalize_fn": lambda name: name,  # Lake SBOE names match GeoJSON directly
        "label_prefix": "SBOE Lake",
    },
}

# ── Scan CSVs ───────────────────────────────────────────────
def scan_county_csv(filepath, election_id, jurisdiction_id, normalize_fn, label):
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
            pname_raw = row.get('PrecinctName', '').strip()
            cand = row.get('CandidateName', '').strip()
            party = row.get('PartyName', '').strip()
            votes = safe_int(row.get('VoteCount', 0))
            reg = safe_int(row.get('Registration', 0))

            if not pname_raw:
                continue

            # Skip special precincts
            if pname_raw.startswith('FEDERAL') or pname_raw == 'PRESIDENTIAL':
                continue

            # Normalize precinct name to match GeoJSON
            pname = normalize_fn(pname_raw)
            pid = make_id(jurisdiction_id, pname)

            if pid not in precincts:
                # Extract ward/precinct number
                m_num = re.search(r'(\d+)\s*$', pname)
                pnum = int(m_num.group(1)) if m_num else None
                precincts[pid] = (pid, jurisdiction_id, pname, None, pnum)

            # Turnout row (empty contest)
            if not contest:
                if reg > 0:
                    tpct = round(votes / reg * 100, 2) if reg > 0 else 0
                    turnout.append((election_id, pid, reg, votes, tpct, label, pname))
                continue

            # Classify race
            dt_id, dt_num = classify_race_type(contest, source='sboe')

            did = make_id(dt_id, dt_num)
            if did not in districts:
                dname = f"{dt_id.replace('_', ' ').title()} {dt_num}" if dt_num else dt_id.replace('_', ' ').title()
                districts[did] = (did, dt_id, dt_num, dname)

            # Normalize race name for cross-county consistency
            normalized_contest = normalize_race_name(contest)

            # Race ID: same contest in same election = same race (shared across counties)
            rid = make_id(election_id, normalized_contest)
            if rid not in races:
                races[rid] = (rid, election_id, did, normalized_contest, contest, dt_id)

            pd_key = (pid, did)
            if pd_key not in pd_set:
                pd_set.add(pd_key)

            if not cand:
                continue

            cid = make_id(cand, party)
            if cid not in candidates:
                candidates[cid] = (cid, cand, party)

            results.append((election_id, pid, rid, cid, votes, label, contest, pname, cand))

    print(f"  {label}: {n:,} rows → {len(results):,} results, {len(turnout):,} turnout, {len(races)} races, {len(precincts)} precincts")
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
    BASE_DIR = os.environ.get('SBOE_DATA_DIR', '/home/user/workspace/sboe_data')
    
    # ── Discover CSV files ──
    all_files = []
    for county_key, config in COUNTIES.items():
        data_dir = os.path.join(BASE_DIR, county_key)
        if not os.path.isdir(data_dir):
            print(f"Skipping {county_key} — no data directory at {data_dir}")
            continue
        for fn in sorted(os.listdir(data_dir)):
            if not fn.endswith('.csv'):
                continue
            code = fn.replace('.csv', '')
            if code not in ELECTION_MAP:
                print(f"  Unknown election code: {code} — skipping")
                continue
            eid, ename, edate, etype, eyear = ELECTION_MAP[code]
            filepath = os.path.join(data_dir, fn)
            # Check file isn't tiny (error page)
            if os.path.getsize(filepath) < 1000:
                print(f"  Skipping {county_key}/{fn} — too small ({os.path.getsize(filepath)} bytes)")
                continue
            label = f"{config['label_prefix']} {code}"
            all_files.append((filepath, eid, config['jurisdiction_id'], config['normalize_fn'], label))
    
    if not all_files:
        print("No valid CSV files found!")
        return

    # ── Scan all files ──
    print("=" * 60)
    print("SCANNING SBOE COUNTY CSVs")
    print("=" * 60)
    t0 = time.time()

    all_p, all_d, all_r, all_c = {}, {}, {}, {}
    all_results, all_turnout = [], []
    all_pd = set()

    for filepath, eid, jid, norm_fn, label in all_files:
        p, d, r, c, res, to, pd = scan_county_csv(filepath, eid, jid, norm_fn, label)
        all_p.update(p)
        all_d.update(d)
        all_r.update(r)
        all_c.update(c)
        all_results.extend(res)
        all_turnout.extend(to)
        all_pd.update(pd)

    scan_time = time.time() - t0
    print(f"\nScan complete in {scan_time:.1f}s")
    print(f"  Precincts:  {len(all_p):,}")
    print(f"  Districts:  {len(all_d):,}")
    print(f"  Races:      {len(all_r):,}")
    print(f"  Candidates: {len(all_c):,}")
    print(f"  Results:    {len(all_results):,}")
    print(f"  Turnout:    {len(all_turnout):,}")
    print(f"  PD maps:    {len(all_pd):,}")

    # ── Connect to Postgres ──
    print(f"\nConnecting to Supabase Postgres...")
    conn = psycopg2.connect(DB_URI, connect_timeout=30)
    conn.autocommit = False
    cur = conn.cursor()
    cur.execute("SET statement_timeout = 0;")

    # ── Ensure elections exist ──
    print("\n--- Ensuring elections exist ---")
    for code, (eid, ename, edate, etype, eyear) in ELECTION_MAP.items():
        if ename is None:
            continue  # Already exists
        cur.execute("SELECT id FROM elections WHERE id = %s", (eid,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO elections (id, name, date, type, year) VALUES (%s, %s, %s, %s, %s)",
                (eid, ename, edate, etype, eyear)
            )
            print(f"  Created election: {eid} ({ename})")
        else:
            print(f"  Election exists: {eid}")
    conn.commit()

    # ── Ensure dekalb_county jurisdiction exists ──
    cur.execute("SELECT id FROM jurisdictions WHERE id = 'dekalb_county'")
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO jurisdictions (id, name, type, county) VALUES (%s, %s, %s, %s)",
            ('dekalb_county', 'DeKalb County', 'county', 'DeKalb')
        )
        print("  Created jurisdiction: dekalb_county")
    else:
        print("  Jurisdiction exists: dekalb_county")
    conn.commit()

    # ── Load reference tables ──
    print("\n" + "=" * 60)
    print("LOADING VIA COPY")
    print("=" * 60)

    # District types — ensure all needed types exist
    print(f"\n--- District types ---")
    dt_needed = set()
    for did, dt_id, dt_num, dname in all_d.values():
        dt_needed.add(dt_id)
    
    for dt_id in dt_needed:
        cur.execute("SELECT id FROM district_types WHERE id = %s", (dt_id,))
        if cur.fetchone() is None:
            # Determine category
            cat = 'other'
            if dt_id in ('president', 'us_senate', 'governor', 'lt_governor', 
                         'attorney_general', 'secretary_of_state', 'comptroller', 
                         'treasurer_state'): cat = 'statewide'
            elif dt_id in ('congress', 'state_senate', 'state_rep'): cat = 'legislative'
            elif dt_id in ('supreme_court', 'appellate_court', 'circuit_court', 
                          'subcircuit', 'judge'): cat = 'judicial'
            elif dt_id in ('cook_commissioner', 'cook_president', 'cook_assessor',
                          'cook_clerk', 'cook_treasurer', 'cook_sheriff', 'board_of_review'): cat = 'county'
            elif dt_id in ('mayor', 'aldermanic_ward', 'city_clerk', 'city_treasurer',
                          'municipal', 'municipal_ward', 'township_office',
                          'township_committeeperson'): cat = 'municipal'
            elif dt_id in ('school_board', 'school_district'): cat = 'school'
            elif dt_id in ('park_district', 'library', 'fire_district', 'mwrd',
                          'water_reclamation', 'referendum'): cat = 'special'
            elif dt_id in ('state_central_comm', 'delegate'): cat = 'statewide'
            
            dname = dt_id.replace('_', ' ').title()
            cur.execute(
                "INSERT INTO district_types (id, name, category) VALUES (%s, %s, %s)",
                (dt_id, dname, cat)
            )
            print(f"  Created district_type: {dt_id} ({cat})")
    conn.commit()

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

    # Deduplicate results — keep max votes for any (election, precinct, race, candidate) combo
    print(f"\n--- Deduplicating results ---")
    dedup = {}
    for row in all_results:
        key = (row[0], row[1], row[2], row[3])  # election_id, precinct_id, race_id, candidate_id
        if key not in dedup or row[4] > dedup[key][4]:
            dedup[key] = row
    all_results = list(dedup.values())
    print(f"  After dedup: {len(all_results):,} results")

    # Results
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

    # Deduplicate turnout
    dedup_to = {}
    for row in all_turnout:
        key = (row[0], row[1])  # election_id, precinct_id
        if key not in dedup_to or row[2] > dedup_to[key][2]:  # keep higher registration
            dedup_to[key] = row
    all_turnout = list(dedup_to.values())

    # Turnout
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

    # ── Summary ──
    cur.execute("SELECT COUNT(*) FROM results;")
    total_results = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM precincts;")
    total_precincts = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM races;")
    total_races = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM turnout;")
    total_turnout = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM elections;")
    total_elections = cur.fetchone()[0]

    cur.close()
    conn.close()

    total_time = time.time() - t0
    print(f"\n{'='*60}")
    print(f"ALL DONE in {total_time:.1f}s")
    print(f"{'='*60}")
    print(f"  Total elections:  {total_elections}")
    print(f"  Total precincts:  {total_precincts:,}")
    print(f"  Total races:      {total_races:,}")
    print(f"  Total results:    {total_results:,}")
    print(f"  Total turnout:    {total_turnout:,}")


if __name__ == "__main__":
    main()
