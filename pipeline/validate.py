#!/usr/bin/env python3
"""
D4D Election Data Validation System
====================================
Comprehensive integrity checks for the Supabase election database.

Checks:
  1. Duplicate detection (results, turnout, races)
  2. Race type consistency — validates against unified classifier
  3. Expected coverage — precincts in GeoJSON vs. DB
  4. Precinct match rate — ≥90% threshold (HARD FAIL if below)
  5. Cross-election comparison — flag anomalies between cycles
  6. Orphan detection — results referencing non-existent races/precincts
  7. Vote sanity — negative votes, >100% turnout, missing data

Usage:
    python validate.py                   # Run all checks
    python validate.py --check dupes     # Run specific check
    python validate.py --election 2026_primary  # Scope to one election
    python validate.py --json            # Output JSON report
    python validate.py --fix-dupes       # Auto-remove duplicates (interactive)

Exit codes:
    0 = all checks pass
    1 = warnings only
    2 = failures (≥1 hard fail, e.g. match rate <90%)
"""

import argparse
import json
import sys
import hashlib
import os
from collections import defaultdict
from datetime import datetime

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

# Import unified classifier
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify_race import classify_race_type, VALID_RACE_TYPES

# ─── Configuration ───
DB_URL = "postgresql://postgres.nfjfqdffulhqhszhlymo:D4dHeatmap2026!Pg@aws-0-us-west-2.pooler.supabase.com:5432/postgres"
SUPA_URL = "https://nfjfqdffulhqhszhlymo.supabase.co"
SUPA_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5mamZxZGZmdWxocWhzemhseW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Mzk1MDMwOCwiZXhwIjoyMDg5NTI2MzA4fQ.zy7Bfl5cOZGF_CU2yiHn3sd24olsx_Hzc985Ov_t5Ys"

PRECINCT_MATCH_THRESHOLD = 0.90  # 90% — hard fail if below
GEOJSON_BASE = f"{SUPA_URL}/storage/v1/object/public/geojson"

# GeoJSON precinct counts (from storage)
CHICAGO_PRECINCTS_EXPECTED = 1291
SUBURBAN_PRECINCTS_EXPECTED = 1430


class ValidationResult:
    """Holds the result of a single validation check."""

    def __init__(self, name, status, message, details=None):
        self.name = name
        self.status = status  # 'pass', 'warn', 'fail'
        self.message = message
        self.details = details or []
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            'name': self.name,
            'status': self.status,
            'message': self.message,
            'details': self.details[:50],  # cap detail output
            'detail_count': len(self.details),
            'timestamp': self.timestamp,
        }

    def __str__(self):
        icon = {'pass': '✓', 'warn': '⚠', 'fail': '✗'}[self.status]
        color = {'pass': '\033[92m', 'warn': '\033[93m', 'fail': '\033[91m'}[self.status]
        reset = '\033[0m'
        s = f"{color}{icon} {self.name}: {self.message}{reset}"
        if self.details:
            for d in self.details[:10]:
                s += f"\n    → {d}"
            if len(self.details) > 10:
                s += f"\n    … and {len(self.details) - 10} more"
        return s


def get_connection():
    """Get a psycopg2 connection with statement timeout."""
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    cur = conn.cursor()
    cur.execute("SET statement_timeout = '120s';")
    return conn


# ═══════════════════════════════════════════════════════════════
# CHECK 1: DUPLICATE DETECTION
# ═══════════════════════════════════════════════════════════════

def check_duplicates(conn, election_id=None):
    """Find duplicate rows in results and turnout tables."""
    cur = conn.cursor()
    results = []

    # Results duplicates
    where = f"WHERE r.election_id = '{election_id}'" if election_id else ""
    cur.execute(f"""
        SELECT r.election_id, r.race_id, r.precinct_id, r.candidate_id, COUNT(*) as cnt
        FROM results r
        {where}
        GROUP BY r.election_id, r.race_id, r.precinct_id, r.candidate_id
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
        LIMIT 100;
    """)
    dupes = cur.fetchall()
    dupe_details = [
        f"election={d[0]} race={d[1]} precinct={d[2]} candidate={d[3]} count={d[4]}"
        for d in dupes
    ]
    total_dupe_rows = sum(d[4] - 1 for d in dupes)

    if dupes:
        results.append(ValidationResult(
            'Results Duplicates',
            'fail',
            f"Found {len(dupes)} duplicate groups ({total_dupe_rows} excess rows)",
            dupe_details
        ))
    else:
        results.append(ValidationResult(
            'Results Duplicates', 'pass', 'No duplicate result rows found'))

    # Turnout duplicates
    where_t = f"WHERE t.election_id = '{election_id}'" if election_id else ""
    cur.execute(f"""
        SELECT t.election_id, t.precinct_id, COUNT(*) as cnt
        FROM turnout t
        {where_t}
        GROUP BY t.election_id, t.precinct_id
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
        LIMIT 100;
    """)
    t_dupes = cur.fetchall()

    if t_dupes:
        t_details = [f"election={d[0]} precinct={d[1]} count={d[2]}" for d in t_dupes]
        results.append(ValidationResult(
            'Turnout Duplicates', 'fail',
            f"Found {len(t_dupes)} duplicate turnout entries",
            t_details
        ))
    else:
        results.append(ValidationResult(
            'Turnout Duplicates', 'pass', 'No duplicate turnout rows found'))

    # Race duplicates (same election + name)
    where_r = f"WHERE r.election_id = '{election_id}'" if election_id else ""
    cur.execute(f"""
        SELECT r.election_id, r.name, COUNT(*) as cnt
        FROM races r
        {where_r}
        GROUP BY r.election_id, r.name
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
        LIMIT 50;
    """)
    r_dupes = cur.fetchall()

    if r_dupes:
        r_details = [f"election={d[0]} name='{d[1]}' count={d[2]}" for d in r_dupes]
        results.append(ValidationResult(
            'Race Duplicates', 'warn',
            f"Found {len(r_dupes)} races with duplicate names",
            r_details
        ))
    else:
        results.append(ValidationResult(
            'Race Duplicates', 'pass', 'No duplicate race names found'))

    return results


# ═══════════════════════════════════════════════════════════════
# CHECK 2: RACE TYPE CONSISTENCY
# ═══════════════════════════════════════════════════════════════

def check_race_types(conn, election_id=None):
    """Validate race_types against unified classifier and DB constraint."""
    cur = conn.cursor()

    where = f"WHERE r.election_id = '{election_id}'" if election_id else ""
    cur.execute(f"""
        SELECT r.id, r.election_id, r.name, r.source_contest_name, r.race_type
        FROM races r
        {where}
        ORDER BY r.election_id, r.race_type;
    """)
    races = cur.fetchall()

    invalid_types = []
    misclassified = []
    unclassifiable = []

    for race_id, eid, name, source_name, current_type in races:
        # Check if current type is valid
        if current_type not in VALID_RACE_TYPES:
            invalid_types.append(
                f"race={race_id} type='{current_type}' name='{name}' (not in CHECK constraint)")

        # Run through unified classifier and compare
        contest_to_check = source_name or name or ''
        # Determine source based on election
        source_hint = 'auto'
        if eid and ('2023' in eid or 'municipal' in str(eid).lower()):
            source_hint = 'cook_clerk'
        elif eid and ('2025' in eid or 'consolidated' in str(eid).lower()):
            source_hint = 'suburban'

        classified_type, _ = classify_race_type(contest_to_check, source_hint)

        if classified_type != current_type and classified_type != 'other' and current_type != 'other':
            # Only flag if both are non-other and they disagree
            misclassified.append(
                f"race={race_id} current='{current_type}' classifier='{classified_type}' "
                f"name='{source_name or name}'")

    results = []

    if invalid_types:
        results.append(ValidationResult(
            'Invalid Race Types', 'fail',
            f"{len(invalid_types)} races have invalid race_type values",
            invalid_types
        ))
    else:
        results.append(ValidationResult(
            'Invalid Race Types', 'pass',
            f"All {len(races)} races have valid race_type values"))

    if misclassified:
        results.append(ValidationResult(
            'Race Type Mismatches', 'warn',
            f"{len(misclassified)} races differ from unified classifier",
            misclassified
        ))
    else:
        results.append(ValidationResult(
            'Race Type Consistency', 'pass',
            f"All {len(races)} races match unified classifier"))

    # Report distribution
    cur.execute(f"""
        SELECT race_type, COUNT(*) FROM races r {where}
        GROUP BY race_type ORDER BY COUNT(*) DESC;
    """)
    dist = cur.fetchall()
    dist_details = [f"{t}: {c}" for t, c in dist]
    results.append(ValidationResult(
        'Race Type Distribution', 'pass',
        f"{len(dist)} distinct race types across {sum(c for _, c in dist)} races",
        dist_details
    ))

    return results


# ═══════════════════════════════════════════════════════════════
# CHECK 3: EXPECTED COVERAGE
# ═══════════════════════════════════════════════════════════════

def check_coverage(conn, election_id=None):
    """Check that elections have expected precinct coverage."""
    cur = conn.cursor()
    results = []

    # Batch query: get all counts in one shot for performance
    cur.execute("""
        SELECT election_id,
               COUNT(DISTINCT precinct_id) as result_precincts,
               COUNT(*) as result_count
        FROM results
        GROUP BY election_id;
    """)
    result_stats = {r[0]: {'precincts': r[1], 'rows': r[2]} for r in cur.fetchall()}

    cur.execute("""
        SELECT election_id, COUNT(DISTINCT precinct_id)
        FROM turnout GROUP BY election_id;
    """)
    turnout_stats = {r[0]: r[1] for r in cur.fetchall()}

    cur.execute("SELECT election_id, COUNT(*) FROM races GROUP BY election_id;")
    race_stats = {r[0]: r[1] for r in cur.fetchall()}

    # Get all elections
    if election_id:
        cur.execute("SELECT id, name, type FROM elections WHERE id = %s;", (election_id,))
    else:
        cur.execute("SELECT id, name, type FROM elections ORDER BY id;")
    elections = cur.fetchall()

    for eid, ename, etype in elections:
        result_precincts = result_stats.get(eid, {}).get('precincts', 0)
        turnout_precincts = turnout_stats.get(eid, 0)
        race_count = race_stats.get(eid, 0)
        result_count = result_stats.get(eid, {}).get('rows', 0)

        # Determine expected coverage based on election type
        if 'municipal' in eid.lower() or 'runoff' in eid.lower() or '2023' in eid:
            expected = CHICAGO_PRECINCTS_EXPECTED
            scope = 'Chicago-only'
        elif '2025' in eid or 'consolidated' in eid.lower():
            expected = SUBURBAN_PRECINCTS_EXPECTED
            scope = 'Suburban-only'
        elif '2026' in eid:
            expected = SUBURBAN_PRECINCTS_EXPECTED  # Currently suburban data
            scope = 'Suburban'
        else:
            expected = CHICAGO_PRECINCTS_EXPECTED + SUBURBAN_PRECINCTS_EXPECTED
            scope = 'County-wide'

        coverage_pct = (result_precincts / expected * 100) if expected > 0 else 0
        status = 'pass' if coverage_pct >= 80 else ('warn' if coverage_pct >= 50 else 'fail')

        details = [
            f"Races: {race_count}",
            f"Result rows: {result_count:,}",
            f"Result precincts: {result_precincts}",
            f"Turnout precincts: {turnout_precincts}",
            f"Expected ({scope}): {expected}",
            f"Coverage: {coverage_pct:.1f}%",
        ]

        results.append(ValidationResult(
            f'Coverage: {ename}', status,
            f"{result_precincts}/{expected} precincts ({coverage_pct:.1f}% — {scope})",
            details
        ))

    return results


# ═══════════════════════════════════════════════════════════════
# CHECK 4: PRECINCT MATCH RATE (≥90% THRESHOLD)
# ═══════════════════════════════════════════════════════════════

def check_precinct_match_rate(conn, election_id=None):
    """
    Critical check: what percentage of precincts in DB results
    match precincts in our GeoJSON (by precinct_id)?
    Threshold: ≥90%. HARD FAIL if below.
    """
    cur = conn.cursor()
    results = []

    # Get all precinct IDs from the precincts table (these match GeoJSON)
    cur.execute("SELECT id FROM precincts;")
    geo_pids = set(r[0] for r in cur.fetchall())
    total_geo = len(geo_pids)

    if election_id:
        cur.execute("""
            SELECT id, name FROM elections WHERE id = %s;
        """, (election_id,))
    else:
        cur.execute("SELECT id, name FROM elections ORDER BY id;")
    elections = cur.fetchall()

    for eid, ename in elections:
        # Distinct precinct_ids in results for this election
        cur.execute("""
            SELECT DISTINCT precinct_id FROM results WHERE election_id = %s;
        """, (eid,))
        result_pids = set(r[0] for r in cur.fetchall())

        if not result_pids:
            results.append(ValidationResult(
                f'Precinct Match: {ename}', 'warn',
                'No result precincts found'))
            continue

        # How many result precincts match our GeoJSON precincts?
        matched = result_pids & geo_pids
        unmatched = result_pids - geo_pids

        match_rate = len(matched) / len(result_pids) if result_pids else 0
        status = 'pass' if match_rate >= PRECINCT_MATCH_THRESHOLD else 'fail'

        details = [
            f"Result precincts: {len(result_pids)}",
            f"GeoJSON precincts: {total_geo}",
            f"Matched: {len(matched)}",
            f"Unmatched in results: {len(unmatched)}",
        ]

        if unmatched and len(unmatched) <= 20:
            # Show unmatched PIDs for debugging
            for pid in sorted(unmatched)[:20]:
                # Try to find the source_precinct_name
                cur.execute("""
                    SELECT DISTINCT source_precinct_name FROM results
                    WHERE election_id = %s AND precinct_id = %s LIMIT 1;
                """, (eid, pid))
                row = cur.fetchone()
                src_name = row[0] if row else '?'
                details.append(f"  Unmatched: {pid[:12]}… → '{src_name}'")

        results.append(ValidationResult(
            f'Precinct Match: {ename}', status,
            f"{match_rate:.1%} ({len(matched)}/{len(result_pids)}) — "
            f"threshold {PRECINCT_MATCH_THRESHOLD:.0%}",
            details
        ))

    return results


# ═══════════════════════════════════════════════════════════════
# CHECK 5: CROSS-ELECTION COMPARISON
# ═══════════════════════════════════════════════════════════════

def check_cross_election(conn, election_id=None):
    """Flag anomalies when comparing the same race across elections."""
    cur = conn.cursor()
    results = []

    # Compare race counts per race_type across elections (lightweight)
    cur.execute("""
        SELECT e.name, r.race_type, COUNT(*) as race_count
        FROM races r
        JOIN elections e ON r.election_id = e.id
        GROUP BY e.name, r.race_type
        ORDER BY r.race_type, e.name;
    """)
    rows = cur.fetchall()

    # Group by race_type
    by_type = defaultdict(list)
    for ename, rtype, rcount in rows:
        by_type[rtype].append((ename, rcount))

    anomalies = []
    for rtype, entries in by_type.items():
        if len(entries) < 2:
            continue
        # Check if race counts vary wildly (>3x difference)
        rcounts = [e[1] for e in entries]
        if max(rcounts) > 0 and min(rcounts) > 0:
            ratio = max(rcounts) / min(rcounts)
            if ratio > 5:
                anomalies.append(
                    f"{rtype}: race count varies {min(rcounts)}–{max(rcounts)} "
                    f"(ratio {ratio:.1f}x) across elections")

    if anomalies:
        results.append(ValidationResult(
            'Cross-Election Anomalies', 'warn',
            f"{len(anomalies)} race types show large precinct count variance",
            anomalies
        ))
    else:
        results.append(ValidationResult(
            'Cross-Election Consistency', 'pass',
            'No major anomalies between elections'))

    return results


# ═══════════════════════════════════════════════════════════════
# CHECK 6: ORPHAN DETECTION
# ═══════════════════════════════════════════════════════════════

def check_orphans(conn, election_id=None):
    """Find results referencing non-existent races, precincts, or candidates."""
    cur = conn.cursor()
    results_list = []
    where = f"AND res.election_id = '{election_id}'" if election_id else ""

    # Results with no matching race
    cur.execute(f"""
        SELECT COUNT(*) FROM results res
        WHERE NOT EXISTS (SELECT 1 FROM races r WHERE r.id = res.race_id)
        {where};
    """)
    orphan_races = cur.fetchone()[0]

    # Results with no matching precinct
    cur.execute(f"""
        SELECT COUNT(*) FROM results res
        WHERE NOT EXISTS (SELECT 1 FROM precincts p WHERE p.id = res.precinct_id)
        {where};
    """)
    orphan_precincts = cur.fetchone()[0]

    # Results with no matching candidate
    cur.execute(f"""
        SELECT COUNT(*) FROM results res
        WHERE NOT EXISTS (SELECT 1 FROM candidates c WHERE c.id = res.candidate_id)
        {where};
    """)
    orphan_candidates = cur.fetchone()[0]

    details = []
    status = 'pass'
    if orphan_races > 0:
        details.append(f"Results with missing race: {orphan_races:,}")
        status = 'fail'
    if orphan_precincts > 0:
        details.append(f"Results with missing precinct: {orphan_precincts:,}")
        status = 'warn'  # Precincts may not be in our GeoJSON yet
    if orphan_candidates > 0:
        details.append(f"Results with missing candidate: {orphan_candidates:,}")
        status = 'fail'

    total = orphan_races + orphan_precincts + orphan_candidates
    if total == 0:
        results_list.append(ValidationResult(
            'Orphan Check', 'pass', 'No orphaned result rows found'))
    else:
        results_list.append(ValidationResult(
            'Orphan Check', status,
            f"{total:,} orphaned references found", details))

    return results_list


# ═══════════════════════════════════════════════════════════════
# CHECK 7: VOTE SANITY
# ═══════════════════════════════════════════════════════════════

def check_vote_sanity(conn, election_id=None):
    """Check for negative votes, impossible turnout, etc."""
    cur = conn.cursor()
    results = []
    where = f"WHERE election_id = '{election_id}'" if election_id else ""

    # Negative votes
    cur.execute(f"SELECT COUNT(*) FROM results {where} AND votes < 0;" if where
                else "SELECT COUNT(*) FROM results WHERE votes < 0;")
    neg_votes = cur.fetchone()[0]

    # Turnout > 100%
    cur.execute(f"""
        SELECT COUNT(*) FROM turnout
        {where + ' AND' if where else 'WHERE'} turnout_pct > 100;
    """)
    over_turnout = cur.fetchone()[0]

    # Turnout with 0 registered voters but >0 ballots
    cur.execute(f"""
        SELECT COUNT(*) FROM turnout
        {where + ' AND' if where else 'WHERE'}
        registered_voters = 0 AND ballots_cast > 0;
    """)
    zero_reg = cur.fetchone()[0]

    # Races with no results
    cur.execute(f"""
        SELECT COUNT(*) FROM races r
        WHERE NOT EXISTS (SELECT 1 FROM results res WHERE res.race_id = r.id)
        {' AND r.election_id = ' + repr(election_id) if election_id else ''};
    """)
    empty_races = cur.fetchone()[0]

    details = []
    status = 'pass'

    if neg_votes > 0:
        details.append(f"Negative vote counts: {neg_votes}")
        status = 'fail'
    if over_turnout > 0:
        details.append(f"Turnout > 100%: {over_turnout}")
        status = 'warn'
    if zero_reg > 0:
        details.append(f"Zero registered / nonzero ballots: {zero_reg}")
        status = 'warn'
    if empty_races > 0:
        details.append(f"Races with no results: {empty_races}")
        if empty_races > 10:
            status = 'warn'

    if not details:
        results.append(ValidationResult(
            'Vote Sanity', 'pass', 'All vote and turnout values look clean'))
    else:
        results.append(ValidationResult(
            'Vote Sanity', status,
            f"Found {len(details)} issue(s)", details))

    return results


# ═══════════════════════════════════════════════════════════════
# FIX: AUTO-REMOVE DUPLICATES
# ═══════════════════════════════════════════════════════════════

def fix_duplicates(conn, election_id=None, dry_run=True):
    """Remove duplicate result rows, keeping the newest (highest id)."""
    cur = conn.cursor()

    where = f"AND election_id = '{election_id}'" if election_id else ""
    cur.execute(f"""
        WITH dupes AS (
            SELECT id, ROW_NUMBER() OVER (
                PARTITION BY race_id, precinct_id, candidate_id
                ORDER BY id DESC
            ) as rn
            FROM results
            WHERE 1=1 {where}
        )
        SELECT COUNT(*) FROM dupes WHERE rn > 1;
    """)
    dupe_count = cur.fetchone()[0]

    if dupe_count == 0:
        print("  No duplicates to fix.")
        return 0

    if dry_run:
        print(f"  Would remove {dupe_count} duplicate result rows.")
        return dupe_count

    cur.execute(f"""
        WITH dupes AS (
            SELECT id, ROW_NUMBER() OVER (
                PARTITION BY race_id, precinct_id, candidate_id
                ORDER BY id DESC
            ) as rn
            FROM results
            WHERE 1=1 {where}
        )
        DELETE FROM results WHERE id IN (SELECT id FROM dupes WHERE rn > 1);
    """)
    conn.commit()
    print(f"  Removed {dupe_count} duplicate result rows.")
    return dupe_count


# ═══════════════════════════════════════════════════════════════
# SUMMARY & REPORT
# ═══════════════════════════════════════════════════════════════

def generate_summary(all_results):
    """Generate a summary from all validation results."""
    passes = sum(1 for r in all_results if r.status == 'pass')
    warns = sum(1 for r in all_results if r.status == 'warn')
    fails = sum(1 for r in all_results if r.status == 'fail')

    overall = 'PASS' if fails == 0 and warns == 0 else ('WARN' if fails == 0 else 'FAIL')
    return {
        'overall': overall,
        'checks_run': len(all_results),
        'passes': passes,
        'warnings': warns,
        'failures': fails,
        'timestamp': datetime.utcnow().isoformat(),
    }


def print_report(all_results, as_json=False):
    """Print validation report."""
    summary = generate_summary(all_results)

    if as_json:
        report = {
            'summary': summary,
            'results': [r.to_dict() for r in all_results],
        }
        print(json.dumps(report, indent=2))
        return summary

    print("\n" + "═" * 60)
    print("  D4D ELECTION DATA VALIDATION REPORT")
    print(f"  {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("═" * 60)

    for r in all_results:
        print(f"\n{r}")

    print("\n" + "─" * 60)
    color = {
        'PASS': '\033[92m', 'WARN': '\033[93m', 'FAIL': '\033[91m'
    }[summary['overall']]
    reset = '\033[0m'
    print(f"  Overall: {color}{summary['overall']}{reset}  "
          f"({summary['passes']} pass, {summary['warnings']} warn, {summary['failures']} fail)")
    print("─" * 60 + "\n")

    return summary


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='D4D Election Data Validation')
    parser.add_argument('--check', choices=[
        'dupes', 'types', 'coverage', 'match', 'cross', 'orphans', 'sanity', 'all'
    ], default='all', help='Which check to run')
    parser.add_argument('--election', help='Scope to a specific election_id')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--fix-dupes', action='store_true', help='Auto-remove duplicate results')
    parser.add_argument('--dry-run', action='store_true', help='Show what --fix-dupes would do')
    args = parser.parse_args()

    conn = get_connection()

    if args.fix_dupes:
        fix_duplicates(conn, args.election, dry_run=args.dry_run)
        conn.close()
        return

    all_results = []
    checks = {
        'dupes': lambda: check_duplicates(conn, args.election),
        'types': lambda: check_race_types(conn, args.election),
        'coverage': lambda: check_coverage(conn, args.election),
        'match': lambda: check_precinct_match_rate(conn, args.election),
        'cross': lambda: check_cross_election(conn, args.election),
        'orphans': lambda: check_orphans(conn, args.election),
        'sanity': lambda: check_vote_sanity(conn, args.election),
    }

    if args.check == 'all':
        for name, fn in checks.items():
            try:
                all_results.extend(fn())
            except Exception as e:
                all_results.append(ValidationResult(
                    name, 'fail', f'Check crashed: {e}'))
    else:
        try:
            all_results.extend(checks[args.check]())
        except Exception as e:
            all_results.append(ValidationResult(
                args.check, 'fail', f'Check crashed: {e}'))

    summary = print_report(all_results, as_json=args.json)

    conn.close()

    # Exit code based on results
    if summary['failures'] > 0:
        sys.exit(2)
    elif summary['warnings'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
