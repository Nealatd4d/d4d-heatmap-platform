#!/usr/bin/env python3
"""
Load CBOE 2026 Primary Chicago precinct data into Supabase.

Reads from /tmp/cboe_parsed/contest_{election_id}_{contest_id}.json files
produced by download_cboe_ajax.py.

ID formulas (matching existing loaders):
  race_id:      MD5(f"{election_id}|{race_name}")[:16]
  candidate_id: MD5(f"{race_id}|{candidate_name}")[:16]
  precinct_id:  MD5(f"chicago|{source_precinct_name}".lower())[:16]
"""

import hashlib
import json
import os
import re
import sys
import psycopg2
from psycopg2.extras import execute_values

DB_DSN = "postgresql://postgres.nfjfqdffulhqhszhlymo:D4dHeatmap2026!Pg@aws-0-us-west-2.pooler.supabase.com:5432/postgres"
ELECTION_ID = "2026_primary"
SOURCE_FILE = "cboe_2026_ajax"
PARSED_DIR = "/tmp/cboe_parsed"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify_race import classify_race_type


def make_precinct_id(ward, precinct):
    """Chicago precinct ID: MD5("chicago|ward XX precinct YY".lower())[:16]"""
    source_name = f"Ward {ward:02d} Precinct {precinct:02d}"
    raw = f"chicago|{source_name}".lower()
    return hashlib.md5(raw.encode()).hexdigest()[:16], source_name


def make_race_id(election_id, race_name):
    """Race ID: MD5(f"{election_id}|{race_name}")[:16]"""
    return hashlib.md5(f"{election_id}|{race_name}".encode()).hexdigest()[:16]


def make_candidate_id(race_id, candidate_name):
    """Candidate ID: MD5(f"{race_id}|{candidate_name}")[:16]"""
    return hashlib.md5(f"{race_id}|{candidate_name}".encode()).hexdigest()[:16]


def extract_district(race_name):
    m = re.search(r'(\d+)\w*\s+District', race_name)
    if m:
        return m.group(1)
    m = re.search(r'(\d+)\w*\s+Subcircuit', race_name)
    if m:
        return m.group(1)
    return None


def load_all():
    conn = psycopg2.connect(DB_DSN)
    conn.autocommit = False
    cur = conn.cursor()

    print("=" * 60)
    print("CBOE 2026 Primary Loader")
    print("=" * 60)

    # Verify election
    cur.execute("SELECT id, name FROM elections WHERE id = %s", (ELECTION_ID,))
    row = cur.fetchone()
    print(f"Election: {row[0]} - {row[1]}")

    # Get existing races
    cur.execute("SELECT id, name FROM races WHERE election_id = %s", (ELECTION_ID,))
    existing_races = {r[1]: r[0] for r in cur.fetchall()}
    print(f"Existing races: {len(existing_races)}")

    # Get existing precinct IDs
    cur.execute("SELECT id FROM precincts WHERE jurisdiction_id = 'chicago'")
    chicago_precincts = set(r[0] for r in cur.fetchall())
    print(f"Chicago precincts in DB: {len(chicago_precincts)}")

    # Scan parsed files
    contest_files = sorted([
        f for f in os.listdir(PARSED_DIR)
        if f.startswith('contest_') and f.endswith('.json')
    ])
    print(f"Contest files: {len(contest_files)}")

    turnout_file = os.path.join(PARSED_DIR, 'turnout_76.json')
    has_turnout = os.path.exists(turnout_file)

    stats = {
        'races_created': 0, 'candidates_created': 0,
        'results_inserted': 0, 'results_skipped': 0,
        'turnout_inserted': 0, 'precincts_created': 0,
    }

    # First pass: ensure all referenced precincts exist
    print("\n--- Ensuring Chicago precincts exist ---")
    all_precinct_ids = set()
    for cf in contest_files:
        with open(os.path.join(PARSED_DIR, cf)) as f:
            data = json.load(f)
        for r in data.get('results', []):
            w, p = int(r['ward']), int(r['precinct'])
            pid, pname = make_precinct_id(w, p)
            if pid not in chicago_precincts and pid not in all_precinct_ids:
                all_precinct_ids.add(pid)
                cur.execute("""
                    INSERT INTO precincts (id, jurisdiction_id, source_precinct_name, ward, precinct_number)
                    VALUES (%s, 'chicago', %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (pid, pname, w, p))
                stats['precincts_created'] += 1

    if has_turnout:
        with open(turnout_file) as f:
            turnout_data = json.load(f)['results']
        for t in turnout_data:
            w, p = int(t['ward']), int(t['precinct'])
            pid, pname = make_precinct_id(w, p)
            if pid not in chicago_precincts and pid not in all_precinct_ids:
                all_precinct_ids.add(pid)
                cur.execute("""
                    INSERT INTO precincts (id, jurisdiction_id, source_precinct_name, ward, precinct_number)
                    VALUES (%s, 'chicago', %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (pid, pname, w, p))
                stats['precincts_created'] += 1

    conn.commit()
    print(f"  Created {stats['precincts_created']} new precincts")

    # Process each contest
    print("\n--- Loading Contests ---")
    for cf in contest_files:
        with open(os.path.join(PARSED_DIR, cf)) as f:
            data = json.load(f)

        contest_name = data.get('contest_name', '')
        results = data.get('results', [])
        if not results or data.get('empty'):
            continue

        record_type = data.get('record_type', 'results')
        if record_type == 'turnout':
            continue

        party = 'DEM' if '- DEM' in contest_name else ('REP' if '- REP' in contest_name else 'NON')
        race_name = contest_name

        # Find or create race
        if race_name in existing_races:
            race_id = existing_races[race_name]
        else:
            race_id = make_race_id(ELECTION_ID, race_name)
            result = classify_race_type(race_name, 'cboe')
            if isinstance(result, tuple):
                race_type = result[0]
            else:
                race_type = result

            cur.execute("""
                INSERT INTO races (id, election_id, name, source_contest_name, race_type)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (race_id, ELECTION_ID, race_name, race_name, race_type))
            existing_races[race_name] = race_id
            stats['races_created'] += 1

        # Build result rows
        # Use temp table + bulk copy for speed
        result_tuples = []
        cand_set = set()
        for r in results:
            cand_name = r['candidate'].strip()
            w, p = int(r['ward']), int(r['precinct'])
            votes = int(r['votes'])
            pid, pname = make_precinct_id(w, p)
            cid = make_candidate_id(race_id, cand_name)

            # Ensure candidate exists
            if (cid, cand_name) not in cand_set:
                cand_set.add((cid, cand_name))
                cur.execute("""
                    INSERT INTO candidates (id, name, party)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (cid, cand_name, party))

            result_tuples.append((
                ELECTION_ID, pid, race_id, cid, votes,
                SOURCE_FILE, contest_name, pname, cand_name
            ))

        # Bulk insert results
        if result_tuples:
            try:
                execute_values(cur, """
                    INSERT INTO results
                        (election_id, precinct_id, race_id, candidate_id, votes,
                         source_file, source_contest_name, source_precinct_name, source_candidate_name)
                    VALUES %s
                    ON CONFLICT (election_id, race_id, precinct_id, candidate_id) DO NOTHING
                """, result_tuples, page_size=500)
                conn.commit()
                stats['results_inserted'] += len(result_tuples)
            except Exception as e:
                conn.rollback()
                print(f"  ERROR {race_name}: {e}")
                # One-by-one fallback
                ok = 0
                for t in result_tuples:
                    try:
                        cur.execute("""
                            INSERT INTO results
                                (election_id, precinct_id, race_id, candidate_id, votes,
                                 source_file, source_contest_name, source_precinct_name, source_candidate_name)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            ON CONFLICT (election_id, race_id, precinct_id, candidate_id) DO NOTHING
                        """, t)
                        conn.commit()
                        ok += 1
                    except Exception as e2:
                        conn.rollback()
                        stats['results_skipped'] += 1
                stats['results_inserted'] += ok

        precincts = len(set((r['ward'], r['precinct']) for r in results))
        cands = len(set(r['candidate'] for r in results))
        print(f"  [{party}] {race_name}: {precincts}P x {cands}C = {len(result_tuples)} rows")

    # Process turnout
    if has_turnout:
        print("\n--- Loading Turnout ---")
        turnout_tuples = []
        for t in turnout_data:
            w, p = int(t['ward']), int(t['precinct'])
            pid, pname = make_precinct_id(w, p)
            reg = t['registered_voters']
            cast = t['ballots_cast']
            tpct = round(cast / reg * 100, 2) if reg > 0 else 0
            turnout_tuples.append((ELECTION_ID, pid, reg, cast, tpct, SOURCE_FILE, pname))

        try:
            execute_values(cur, """
                INSERT INTO turnout
                    (election_id, precinct_id, registered_voters, ballots_cast, turnout_pct,
                     source_file, source_precinct_name)
                VALUES %s
                ON CONFLICT (election_id, precinct_id) DO NOTHING
            """, turnout_tuples)
            conn.commit()
            stats['turnout_inserted'] = len(turnout_tuples)
            print(f"  Inserted {stats['turnout_inserted']} turnout records")
        except Exception as e:
            conn.rollback()
            print(f"  Turnout error: {e}")
            ok = 0
            for t in turnout_tuples:
                try:
                    cur.execute("""
                        INSERT INTO turnout
                            (election_id, precinct_id, registered_voters, ballots_cast, turnout_pct,
                             source_file, source_precinct_name)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (election_id, precinct_id) DO NOTHING
                    """, t)
                    conn.commit()
                    ok += 1
                except:
                    conn.rollback()
            stats['turnout_inserted'] = ok
            print(f"  Inserted {ok} turnout records (one-by-one)")

    # Final counts
    print(f"\n{'='*60}")
    print("SUMMARY")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    cur.execute("""
        SELECT
            COUNT(DISTINCT precinct_id) as chicago_precincts,
            COUNT(DISTINCT race_id) as races,
            COUNT(*) as results
        FROM results
        WHERE election_id = %s AND source_file = %s
    """, (ELECTION_ID, SOURCE_FILE))
    row = cur.fetchone()
    print(f"\n  CBOE Chicago precincts: {row[0]}")
    print(f"  CBOE races: {row[1]}")
    print(f"  CBOE results: {row[2]}")

    cur.execute("""
        SELECT COUNT(DISTINCT precinct_id), COUNT(DISTINCT race_id), COUNT(*)
        FROM results WHERE election_id = %s
    """, (ELECTION_ID,))
    row = cur.fetchone()
    print(f"\n  Total 2026 precincts: {row[0]}")
    print(f"  Total 2026 races: {row[1]}")
    print(f"  Total 2026 results: {row[2]}")

    cur.execute("SELECT COUNT(*) FROM turnout WHERE election_id = %s", (ELECTION_ID,))
    print(f"  Total 2026 turnout: {cur.fetchone()[0]}")

    # Refresh MV
    print(f"\n{'='*60}")
    print("Refreshing materialized view...")
    try:
        cur.execute("REFRESH MATERIALIZED VIEW mv_race_precinct_results")
        conn.commit()
        print("  Done!")
    except Exception as e:
        conn.rollback()
        print(f"  Error: {e}")

    cur.close()
    conn.close()
    print("COMPLETE!")


if __name__ == '__main__':
    load_all()
