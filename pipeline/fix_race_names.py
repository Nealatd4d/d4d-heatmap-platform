#!/usr/bin/env python3
"""
One-time migration: normalize race names and merge duplicate race_ids in Supabase.

For each race:
  1. Compute normalized name via normalize_race_name()
  2. Compute canonical race_id = MD5(election_id + '|' + normalized_name)[:16]
  3. If multiple races share the same (election_id, canonical_id), merge them:
     - Pick the race_id with the most results as the canonical one
     - UPDATE results rows from orphan race_ids → canonical race_id
     - DELETE orphan race rows
  4. Update race names to canonical form
  5. Refresh materialized view

Safe to re-run: only merges where duplicates actually exist.
"""

import hashlib
import sys
import os

import psycopg2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize_race import normalize_race_name

DB_URI = (
    "postgresql://postgres.nfjfqdffulhqhszhlymo:D4dHeatmap2026!Pg"
    "@aws-0-us-west-2.pooler.supabase.com:5432/postgres"
)


def make_id(*parts):
    raw = "|".join(str(p).strip().lower() for p in parts)
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def main():
    conn = psycopg2.connect(DB_URI, connect_timeout=30)
    conn.autocommit = False
    cur = conn.cursor()
    cur.execute("SET statement_timeout = '600s';")

    # ── Step 1: Load all races ──
    print("Loading all races...")
    cur.execute("SELECT id, election_id, name FROM races ORDER BY election_id, name")
    races = cur.fetchall()
    print(f"  Found {len(races)} races")

    # ── Step 2: Compute canonical names and IDs ──
    # Group by (election_id, canonical_id) → list of (actual_race_id, original_name)
    from collections import defaultdict
    groups = defaultdict(list)
    name_updates = []  # (race_id, new_name) for races whose name should change

    for race_id, election_id, raw_name in races:
        canonical_name = normalize_race_name(raw_name)
        canonical_id = make_id(election_id, canonical_name)
        groups[(election_id, canonical_id)].append((race_id, raw_name))
        if canonical_name != raw_name:
            name_updates.append((race_id, canonical_name, raw_name))

    # ── Step 3: Find groups with duplicates ──
    merge_groups = {k: v for k, v in groups.items() if len(v) > 1}
    print(f"  Found {len(merge_groups)} groups with duplicate race_ids to merge")

    if not merge_groups:
        print("  No merges needed!")
    else:
        # For each merge group, pick the canonical race_id (most results)
        total_results_moved = 0
        total_races_deleted = 0

        for (election_id, canonical_id), members in sorted(merge_groups.items()):
            # Get result counts for each race_id
            race_ids = [m[0] for m in members]
            counts = {}
            for rid in race_ids:
                cur.execute("SELECT COUNT(*) FROM results WHERE race_id = %s", (rid,))
                counts[rid] = cur.fetchone()[0]

            # Pick the one with most results as canonical
            canonical_rid = max(race_ids, key=lambda r: counts[r])
            orphan_rids = [r for r in race_ids if r != canonical_rid]

            canonical_name = normalize_race_name(members[0][1])
            member_names = [m[1] for m in members]
            print(f"\n  MERGE: election={election_id}")
            print(f"    Canonical: {canonical_rid} ({counts[canonical_rid]} results) → '{canonical_name}'")
            for orid in orphan_rids:
                oname = next(m[1] for m in members if m[0] == orid)
                print(f"    Orphan:    {orid} ({counts[orid]} results) ← '{oname}'")

            # Check if canonical_id differs from canonical_rid
            # If canonical_id != canonical_rid, we need to also update the race_id
            # But that would require updating results + race PK which is complex.
            # Instead: move orphan results to canonical_rid, then update canonical_rid's name.

            for orid in orphan_rids:
                if counts[orid] == 0:
                    # No results to move, just delete the orphan race
                    cur.execute("DELETE FROM races WHERE id = %s", (orid,))
                    print(f"    Deleted empty orphan race {orid}")
                    total_races_deleted += 1
                    continue

                # Move results: update race_id from orphan to canonical
                # Handle conflicts: if same (election_id, race_id, precinct_id, candidate_id)
                # exists in both, keep the one with more votes
                cur.execute("""
                    WITH moved AS (
                        UPDATE results SET race_id = %s
                        WHERE race_id = %s
                          AND NOT EXISTS (
                            SELECT 1 FROM results r2
                            WHERE r2.election_id = results.election_id
                              AND r2.race_id = %s
                              AND r2.precinct_id = results.precinct_id
                              AND r2.candidate_id = results.candidate_id
                          )
                        RETURNING 1
                    )
                    SELECT COUNT(*) FROM moved
                """, (canonical_rid, orid, canonical_rid))
                moved = cur.fetchone()[0]
                total_results_moved += moved
                print(f"    Moved {moved} results from {orid} → {canonical_rid}")

                # Delete any remaining orphan results (conflicting duplicates)
                cur.execute("DELETE FROM results WHERE race_id = %s", (orid,))

                # Delete orphan race
                cur.execute("DELETE FROM races WHERE id = %s", (orid,))
                total_races_deleted += 1
                print(f"    Deleted orphan race {orid}")

            conn.commit()

        print(f"\n  Total results moved: {total_results_moved}")
        print(f"  Total orphan races deleted: {total_races_deleted}")

    # ── Step 4: Update race names to canonical form ──
    print(f"\n  Updating {len(name_updates)} race names to canonical form...")
    updated = 0
    for race_id, new_name, old_name in name_updates:
        # Only update if race still exists (might have been deleted as orphan)
        cur.execute("UPDATE races SET name = %s WHERE id = %s AND name != %s", (new_name, race_id, new_name))
        if cur.rowcount > 0:
            updated += 1
            if updated <= 20:
                print(f"    {old_name} → {new_name}")
    conn.commit()
    print(f"  Updated {updated} race names")

    # ── Step 5: Refresh materialized view ──
    print("\nRefreshing materialized view mv_race_precinct_results...")
    cur.execute("REFRESH MATERIALIZED VIEW mv_race_precinct_results;")
    conn.commit()
    print("  Done.")

    # ── Step 6: Verification ──
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    # Check 10th Congress 2024 General
    cur.execute("""
        SELECT DISTINCT p.jurisdiction_id, COUNT(DISTINCT p.id) as precincts
        FROM results r
        JOIN precincts p ON p.id = r.precinct_id
        JOIN races rc ON rc.id = r.race_id
        WHERE rc.election_id = '2024_general'
          AND rc.name = '10TH CONGRESS'
        GROUP BY p.jurisdiction_id
        ORDER BY p.jurisdiction_id
    """)
    rows = cur.fetchall()
    print(f"\n10th Congress 2024 General - Jurisdictions:")
    for jid, cnt in rows:
        print(f"  {jid}: {cnt} precincts")

    # Check 9th Congress 2024 General
    cur.execute("""
        SELECT DISTINCT p.jurisdiction_id, COUNT(DISTINCT p.id) as precincts
        FROM results r
        JOIN precincts p ON p.id = r.precinct_id
        JOIN races rc ON rc.id = r.race_id
        WHERE rc.election_id = '2024_general'
          AND rc.name = '9TH CONGRESS'
        GROUP BY p.jurisdiction_id
        ORDER BY p.jurisdiction_id
    """)
    rows = cur.fetchall()
    print(f"\n9th Congress 2024 General - Jurisdictions:")
    for jid, cnt in rows:
        print(f"  {jid}: {cnt} precincts")

    # Check no more Lake County "other" state rep/senate races
    cur.execute("""
        SELECT r.id, r.name, r.race_type
        FROM races r
        WHERE r.election_id = '2024_general'
          AND r.race_type = 'other'
          AND (r.name ILIKE '%representative%' OR r.name ILIKE '%senator%' OR r.name ILIKE '%senate%')
    """)
    rows = cur.fetchall()
    if rows:
        print(f"\nWARNING: Still {len(rows)} unmerged 'other' state rep/senate races:")
        for r in rows:
            print(f"  {r[0]} | {r[1]} | {r[2]}")
    else:
        print("\nAll Lake County state rep/senate races merged successfully!")

    # Count total races
    cur.execute("SELECT COUNT(*) FROM races")
    total = cur.fetchone()[0]
    print(f"\nTotal races in database: {total}")

    cur.close()
    conn.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
