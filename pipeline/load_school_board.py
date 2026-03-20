#!/usr/bin/env python3
"""
Chicago School Board XLS → Supabase Postgres loader.
Parses BOE precinct-level XLS files (Districts 1-10) from chicagoelections.gov
and loads them into the unified Supabase schema using psycopg2 COPY.

Duplicate protection:
  - results table has UNIQUE (election_id, race_id, precinct_id, candidate_id)
  - Uses temp-table + INSERT ON CONFLICT to safely handle re-runs
  - ALWAYS refresh mv_race_precinct_results after loading

File format:
  Row 0: ['Total Votes', 'Candidate A', '%', 'Candidate B', '%', ...]
  Row 1: [total_votes_str, cand_a_votes, '%', cand_b_votes, '%', ...]
  Row 2: blank
  Row 3: ['Ward XX', '', ...]
  Row 4: ['Precinct', 'Total Voters', 'Candidate A', '%', 'Candidate B', '%', ...]
  Row 5+: [precinct_num (float), total_voters (float), cand_a_votes (float), '%', ...]
  ...
  'Total' row, blank, then next Ward block.
"""
import hashlib
import io
import os
import re
import sys
import time
import psycopg2

# Import unified race_type classifier
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify_race import classify_race_type

# ── Connection ──────────────────────────────────────────────
DB_URI = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres.nfjfqdffulhqhszhlymo:D4dHeatmap2026!Pg"
    "@aws-0-us-west-2.pooler.supabase.com:5432/postgres"
)

ELECTION_ID = "2024_general"
SOURCE_LABEL = "Chicago BOE 2024 General - School Board"
DATA_DIR = os.environ.get("DATA_DIR", "/home/user/workspace/downloads/school_board_2024")


# ── Helpers ─────────────────────────────────────────────────
def safe_int(val):
    """Safely convert a value to int, handling float strings like '1.0'."""
    if val is None or val == '':
        return 0
    try:
        # Handle floats (XLS cells often store ints as 1.0)
        return int(float(val))
    except (ValueError, TypeError):
        # Handle comma-formatted strings like '1,691'
        if isinstance(val, str):
            cleaned = val.replace(',', '').strip()
            if cleaned:
                try:
                    return int(float(cleaned))
                except (ValueError, TypeError):
                    return 0
        return 0


def make_id(*parts):
    raw = "|".join(str(p).strip().lower() for p in parts)
    return hashlib.md5(raw.encode()).hexdigest()[:16]


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


# ── XLS Parser ──────────────────────────────────────────────
def parse_school_board_xls(filepath, district_num):
    """Parse a Chicago BOE school board precinct results XLS file."""
    import xlrd

    wb = xlrd.open_workbook(filepath, ignore_workbook_corruption=True)
    sh = wb.sheet_by_index(0)

    # Extract candidate names from row 0
    # Format: ['Total Votes', 'Candidate A', '%', 'Candidate B', '%', ...]
    candidates = []
    candidate_cols = []  # column indices for vote counts
    for c in range(sh.ncols):
        v = sh.cell_value(0, c)
        if isinstance(v, str) and v.strip() and v.strip() not in ('Total Votes', '%', ''):
            candidates.append(v.strip())
            candidate_cols.append(c)

    contest_name = f"Board of Education - District {district_num}"
    district_type_id = "school_board"

    # Scan rows for ward headers and precinct data
    current_ward = None
    precincts = {}
    districts = {}
    races = {}
    cands = {}
    results = []
    turnout = []
    pd_set = set()

    # District
    did = make_id(district_type_id, district_num)
    districts[did] = (did, district_type_id, district_num,
                      f"School Board {district_num}")

    # Race
    rid = make_id(ELECTION_ID, contest_name)
    races[rid] = (rid, ELECTION_ID, did, contest_name, contest_name, district_type_id)

    # Candidates
    for cand_name in candidates:
        cid = make_id(cand_name, "")  # No party info in these files
        cands[cid] = (cid, cand_name, None)

    for r in range(sh.nrows):
        col0 = sh.cell_value(r, 0)

        # Check for Ward header: "Ward XX"
        if isinstance(col0, str):
            ward_match = re.match(r'Ward\s+(\d+)', col0, re.IGNORECASE)
            if ward_match:
                current_ward = int(ward_match.group(1))
                continue

            # Skip header rows, total rows, blank rows
            if col0.strip() in ('', 'Precinct', 'Total', 'Total Votes'):
                continue

        # Precinct data row: col0 is a float (precinct number)
        if isinstance(col0, (int, float)) and col0 > 0 and current_ward is not None:
            precinct_num = int(col0)
            total_voters = safe_int(sh.cell_value(r, 1))

            # Build precinct name matching Chicago format: "Ward XX Precinct YY"
            pname = f"Ward {current_ward} Precinct {precinct_num}"
            jid = "chicago"
            pid = make_id(jid, pname)

            if pid not in precincts:
                precincts[pid] = (pid, jid, pname, current_ward, precinct_num)

            pd_key = (pid, did)
            if pd_key not in pd_set:
                pd_set.add(pd_key)

            # Turnout: total voters is ballots cast for this race
            if total_voters > 0:
                turnout.append((ELECTION_ID, pid, 0, total_voters, 0,
                                SOURCE_LABEL, pname))

            # Extract vote counts for each candidate
            for i, (cand_name, col_idx) in enumerate(zip(candidates, candidate_cols)):
                votes = safe_int(sh.cell_value(r, col_idx))
                cid = make_id(cand_name, "")
                results.append((
                    ELECTION_ID, pid, rid, cid, votes,
                    SOURCE_LABEL, contest_name, pname, cand_name
                ))

    return precincts, districts, races, cands, results, turnout, pd_set, candidates


# ── Main ────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("SCHOOL BOARD XLS → SUPABASE LOADER")
    print("=" * 60)
    t0 = time.time()

    all_p, all_d, all_r, all_c = {}, {}, {}, {}
    all_results, all_turnout = [], []
    all_pd = set()

    # Process all available district files
    for dist in range(1, 11):
        fname = f"BOE_District{dist}_precinct_results.xls"
        fpath = os.path.join(DATA_DIR, fname)
        if not os.path.exists(fpath):
            print(f"  District {dist}: MISSING ({fname})")
            continue

        p, d, r, c, res, to, pd_s, cands = parse_school_board_xls(fpath, dist)
        print(f"  District {dist}: {len(res):,} results, {len(to):,} turnout, "
              f"{len(cands)} candidates: {', '.join(cands)}")

        all_p.update(p)
        all_d.update(d)
        all_r.update(r)
        all_c.update(c)
        all_results.extend(res)
        all_turnout.extend(to)
        all_pd.update(pd_s)

    scan_time = time.time() - t0
    print(f"\nScan complete in {scan_time:.1f}s")
    print(f"  Precincts: {len(all_p):,}")
    print(f"  Districts: {len(all_d):,}")
    print(f"  Races:     {len(all_r):,}")
    print(f"  Candidates:{len(all_c):,}")
    print(f"  Results:   {len(all_results):,}")
    print(f"  Turnout:   {len(all_turnout):,}")
    print(f"  PD maps:   {len(all_pd):,}")

    if not all_results:
        print("\nERROR: No results parsed! Check the XLS files.")
        sys.exit(1)

    # ── Connect to Postgres ──
    print(f"\nConnecting to Supabase Postgres...")
    conn = psycopg2.connect(DB_URI, connect_timeout=30)
    conn.autocommit = False
    cur = conn.cursor()

    # ── Idempotent: Delete existing school board data ──
    print(f"\nClearing existing school board results...")
    cur.execute("""
        DELETE FROM results 
        WHERE source_file = %s;
    """, (SOURCE_LABEL,))
    deleted_results = cur.rowcount
    cur.execute("""
        DELETE FROM turnout 
        WHERE source_file = %s;
    """, (SOURCE_LABEL,))
    deleted_turnout = cur.rowcount
    conn.commit()
    print(f"  Deleted {deleted_results:,} results, {deleted_turnout:,} turnout rows")

    # Reconnect fresh
    cur.close()
    conn.close()
    conn = psycopg2.connect(DB_URI, connect_timeout=30)
    conn.autocommit = False
    cur = conn.cursor()
    cur.execute("SET statement_timeout = 0;")

    # ── Load reference tables ──
    print("\n" + "=" * 60)
    print("LOADING VIA COPY")
    print("=" * 60)

    # Districts
    print(f"\n--- Districts ({len(all_d)}) ---")
    cur.execute("CREATE TEMP TABLE tmp_districts (LIKE districts INCLUDING ALL) ON COMMIT DROP;")
    n = copy_tuples(cur, "tmp_districts", ["id", "district_type_id", "number", "name"],
                    list(all_d.values()))
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
    pd_rows = [(pid, did, SOURCE_LABEL) for (pid, did) in all_pd]
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

    # Results — use temp table + ON CONFLICT to prevent duplicates
    print(f"\n--- Results ({len(all_results):,}) ---")
    t1 = time.time()
    cur.execute("""CREATE TEMP TABLE tmp_results (
        election_id text, precinct_id text, race_id text, candidate_id text,
        votes integer, source_file text, source_contest_name text,
        source_precinct_name text, source_candidate_name text
    ) ON COMMIT DROP;""")
    n = copy_tuples(cur, "tmp_results",
                    ["election_id", "precinct_id", "race_id", "candidate_id", "votes",
                     "source_file", "source_contest_name", "source_precinct_name",
                     "source_candidate_name"],
                    all_results)
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
    t2 = time.time()
    print(f"  Loaded {n:,} in {t2-t1:.1f}s")

    # Turnout (school board doesn't have registration data, only ballots cast)
    print(f"\n--- Turnout ({len(all_turnout):,}) ---")
    # Skip school board turnout since we don't have registration data
    # The turnout for these precincts already exists from the SBOE general election data
    print(f"  Skipped (no registration data in BOE files; using SBOE turnout)")

    # Refresh materialized view
    print("\nRefreshing materialized view...")
    cur.execute("REFRESH MATERIALIZED VIEW mv_race_precinct_results;")
    conn.commit()

    # ANALYZE
    print("Running ANALYZE...")
    cur.execute("ANALYZE;")
    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*) FROM results WHERE source_file = %s;", (SOURCE_LABEL,))
    final_count = cur.fetchone()[0]
    print(f"\nVerification: {final_count:,} school board results in database")

    cur.execute("""
        SELECT r.name, COUNT(res.id) as result_count
        FROM races r
        JOIN results res ON res.race_id = r.id
        WHERE r.race_type = 'school_board'
        GROUP BY r.name
        ORDER BY r.name;
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]:,} results")

    cur.close()
    conn.close()

    total_time = time.time() - t0
    print(f"\n{'='*60}")
    print(f"ALL DONE in {total_time:.1f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
