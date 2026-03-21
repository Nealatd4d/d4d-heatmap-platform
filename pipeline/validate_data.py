#!/usr/bin/env python3
"""
D4D Data Validation Suite
=========================
Post-load quality checks for silent data issues.

Checks:
  1. Orphaned references — results pointing to nonexistent races/precincts/candidates/elections
  2. Cross-county coverage — multi-jurisdiction races missing expected counties
  3. Materialized view freshness — MV vs source table row counts
  4. Race name normalization — duplicate races that should be merged
  5. Data quality — impossible turnout, vote sums, negatives, zero-vote precincts
  6. GeoJSON coverage — DB precincts matched against GeoJSON features
  7. Election completeness — missing turnout, low result counts

Usage:
    python validate_data.py                        # Run all checks
    python validate_data.py --election 2026_primary # Scope to one election
    python validate_data.py --fix                   # Auto-fix (refresh MV)

Exit codes:
    0 = all pass
    1 = warnings only
    2 = failures
"""

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

try:
    import requests
except ImportError:
    requests = None

# Import normalize_race_name from sibling module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize_race import normalize_race_name

# ─── Configuration ───
DB_URL = "postgresql://postgres.nfjfqdffulhqhszhlymo:D4dHeatmap2026!Pg@aws-0-us-west-2.pooler.supabase.com:5432/postgres"
SUPA_URL = "https://nfjfqdffulhqhszhlymo.supabase.co"
SUPA_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5mamZxZGZmdWxocWhzemhseW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Mzk1MDMwOCwiZXhwIjoyMDg5NTI2MzA4fQ.zy7Bfl5cOZGF_CU2yiHn3sd24olsx_Hzc985Ov_t5Ys"
GEOJSON_BASE = f"{SUPA_URL}/storage/v1/object/public/geojson"

GEOJSON_FILES = {
    "chicago": "precincts_chicago.geojson",
    "suburban": "precincts_suburban.geojson",
    "lake": "precincts_lake.geojson",
    "dupage": "precincts_dupage.geojson",
    "dekalb": "precincts_dekalb.geojson",
}

# Known multi-county congressional districts in our coverage area
# Maps canonical race name → set of expected jurisdictions (from precinct table)
MULTI_COUNTY_DISTRICTS = {
    "10TH CONGRESS": {"lake_county", "cook_suburban"},
    "6TH CONGRESS": {"cook_suburban", "dupage_county"},
    "14TH CONGRESS": {"dekalb_county", "lake_county"},
    "8TH CONGRESS": {"cook_suburban", "dupage_county"},
    "11TH CONGRESS": {"cook_suburban"},
}

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


class CheckResult:
    """Result of a single validation check."""

    def __init__(self, name, status, message, details=None):
        self.name = name
        self.status = status  # 'pass', 'warn', 'fail'
        self.message = message
        self.details = details or []

    def status_label(self):
        return {"pass": f"{GREEN}[PASS]{RESET}",
                "warn": f"{YELLOW}[WARN]{RESET}",
                "fail": f"{RED}[FAIL]{RESET}"}[self.status]

    def __str__(self):
        s = f"{self.status_label()} {self.name}: {self.message}"
        if self.details:
            for d in self.details[:15]:
                s += f"\n       {d}"
            if len(self.details) > 15:
                s += f"\n       ... and {len(self.details) - 15} more"
        return s

    def to_markdown(self):
        icon = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}[self.status]
        lines = [f"### [{icon}] {self.name}", f"{self.message}", ""]
        if self.details:
            for d in self.details[:50]:
                lines.append(f"- {d}")
            if len(self.details) > 50:
                lines.append(f"- ... and {len(self.details) - 50} more")
            lines.append("")
        return "\n".join(lines)


def get_connection():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    cur = conn.cursor()
    cur.execute("SET statement_timeout = '120s';")
    return conn


# ═══════════════════════════════════════════════════════════════
# CHECK 1: ORPHANED REFERENCES
# ═══════════════════════════════════════════════════════════════

def check_orphaned_references(conn, election_id=None):
    """Results/turnout rows referencing nonexistent parent records."""
    cur = conn.cursor()
    where = f"AND r.election_id = %s" if election_id else ""
    params = (election_id,) if election_id else ()

    checks = [
        ("race_id not in races",
         f"SELECT COUNT(*) FROM results r WHERE NOT EXISTS "
         f"(SELECT 1 FROM races ra WHERE ra.id = r.race_id) {where}"),
        ("precinct_id not in precincts",
         f"SELECT COUNT(*) FROM results r WHERE NOT EXISTS "
         f"(SELECT 1 FROM precincts p WHERE p.id = r.precinct_id) {where}"),
        ("candidate_id not in candidates",
         f"SELECT COUNT(*) FROM results r WHERE NOT EXISTS "
         f"(SELECT 1 FROM candidates c WHERE c.id = r.candidate_id) {where}"),
        ("election_id not in elections",
         f"SELECT COUNT(*) FROM results r WHERE NOT EXISTS "
         f"(SELECT 1 FROM elections e WHERE e.id = r.election_id) {where}"),
    ]

    # Turnout orphan — different table
    t_where = f"AND t.election_id = %s" if election_id else ""
    checks.append(
        ("turnout precinct_id not in precincts",
         f"SELECT COUNT(*) FROM turnout t WHERE NOT EXISTS "
         f"(SELECT 1 FROM precincts p WHERE p.id = t.precinct_id) {t_where}")
    )

    total = 0
    details = []
    for label, sql in checks:
        cur.execute(sql, params)
        count = cur.fetchone()[0]
        if count > 0:
            details.append(f"{label}: {count:,}")
        total += count

    if total == 0:
        return CheckResult("Orphaned references", "pass", "0 issues")
    elif total < 100:
        return CheckResult("Orphaned references", "warn",
                           f"{total:,} orphaned references", details)
    else:
        return CheckResult("Orphaned references", "fail",
                           f"{total:,} orphaned references", details)


# ═══════════════════════════════════════════════════════════════
# CHECK 2: CROSS-COUNTY COVERAGE
# ═══════════════════════════════════════════════════════════════

def check_cross_county_coverage(conn, election_id=None):
    """Verify multi-jurisdiction races have precincts from expected counties."""
    cur = conn.cursor()

    # Get all races that are congress/state_rep/state_senate
    where = "AND ra.election_id = %s" if election_id else ""
    params = (election_id,) if election_id else ()

    cur.execute(f"""
        SELECT ra.id, ra.election_id, ra.name, ra.race_type
        FROM races ra
        WHERE ra.race_type IN ('congress', 'state_rep', 'state_senate')
        {where}
        ORDER BY ra.election_id, ra.name;
    """, params)
    races = cur.fetchall()

    if not races:
        return CheckResult("Cross-county coverage", "pass",
                           "No multi-jurisdiction races found to check")

    issues = []
    for race_id, eid, name, rtype in races:
        canonical = normalize_race_name(name) if name else name

        # Get jurisdictions present for this race's precincts
        cur.execute("""
            SELECT DISTINCT p.jurisdiction_id
            FROM results r
            JOIN precincts p ON p.id = r.precinct_id
            WHERE r.race_id = %s AND r.election_id = %s;
        """, (race_id, eid))
        found_jurisdictions = set(row[0] for row in cur.fetchall() if row[0])

        if not found_jurisdictions:
            continue

        # Check against known multi-county map
        if canonical in MULTI_COUNTY_DISTRICTS:
            expected = MULTI_COUNTY_DISTRICTS[canonical]
            missing = expected - found_jurisdictions
            if missing and len(found_jurisdictions) == 1:
                issues.append(
                    f"{eid} / {canonical}: only has {found_jurisdictions}, "
                    f"missing {missing}")

    if not issues:
        return CheckResult("Cross-county coverage", "pass",
                           f"All {len(races)} multi-jurisdiction races checked")
    return CheckResult("Cross-county coverage", "warn",
                       f"{len(issues)} races with incomplete jurisdiction coverage",
                       issues)


# ═══════════════════════════════════════════════════════════════
# CHECK 3: MATERIALIZED VIEW FRESHNESS
# ═══════════════════════════════════════════════════════════════

def check_mv_freshness(conn, election_id=None):
    """Compare result counts: results table vs mv_race_precinct_results."""
    cur = conn.cursor()

    # Check if MV exists
    cur.execute("""
        SELECT EXISTS (
            SELECT 1 FROM pg_matviews
            WHERE matviewname = 'mv_race_precinct_results'
        );
    """)
    if not cur.fetchone()[0]:
        return CheckResult("Materialized view", "warn",
                           "mv_race_precinct_results does not exist")

    where = "WHERE election_id = %s" if election_id else ""
    params = (election_id,) if election_id else ()

    cur.execute(f"SELECT election_id, COUNT(*) FROM results {where} GROUP BY election_id;", params)
    source_counts = dict(cur.fetchall())

    cur.execute(f"SELECT election_id, COUNT(*) FROM mv_race_precinct_results {where} GROUP BY election_id;", params)
    mv_counts = dict(cur.fetchall())

    stale = []
    for eid in sorted(set(source_counts) | set(mv_counts)):
        src = source_counts.get(eid, 0)
        mv = mv_counts.get(eid, 0)
        if src != mv:
            stale.append(f"{eid}: results={src:,} vs MV={mv:,} (diff={src - mv:+,})")

    if not stale:
        return CheckResult("Materialized view", "pass",
                           f"fresh ({len(source_counts)} elections in sync)")
    return CheckResult("Materialized view", "fail",
                       f"{len(stale)} stale elections", stale)


def fix_mv(conn):
    """Refresh the materialized view."""
    cur = conn.cursor()
    print("  Refreshing mv_race_precinct_results...")
    cur.execute("REFRESH MATERIALIZED VIEW mv_race_precinct_results;")
    conn.commit()
    print("  Done.")


# ═══════════════════════════════════════════════════════════════
# CHECK 4: RACE NAME NORMALIZATION (duplicate detection)
# ═══════════════════════════════════════════════════════════════

def check_race_normalization(conn, election_id=None):
    """Find races in the same election that normalize to the same name but have different IDs."""
    cur = conn.cursor()

    where = "WHERE ra.election_id = %s" if election_id else ""
    params = (election_id,) if election_id else ()

    cur.execute(f"""
        SELECT ra.id, ra.election_id, ra.name
        FROM races ra
        {where}
        ORDER BY ra.election_id, ra.name;
    """, params)
    races = cur.fetchall()

    # Group by (election_id, normalized_name)
    groups = defaultdict(list)
    for race_id, eid, name in races:
        canonical = normalize_race_name(name) if name else name
        groups[(eid, canonical)].append((race_id, name))

    duplicates = []
    for (eid, canonical), members in sorted(groups.items()):
        if len(members) > 1:
            names = [f"  {rid[:12]}… → '{n}'" for rid, n in members]
            duplicates.append(
                f"{eid} / '{canonical}' has {len(members)} race IDs:")
            duplicates.extend(names)

    if not duplicates:
        return CheckResult("Race normalization", "pass",
                           f"0 duplicate groups across {len(races)} races")
    dup_count = sum(1 for (_, _), m in groups.items() if len(m) > 1)
    return CheckResult("Race normalization", "warn",
                       f"{dup_count} duplicate groups (races that should be merged)",
                       duplicates)


# ═══════════════════════════════════════════════════════════════
# CHECK 5: DATA QUALITY
# ═══════════════════════════════════════════════════════════════

def check_data_quality(conn, election_id=None):
    """Turnout >100%, vote sum issues, low result counts, zero-vote precincts, negatives."""
    cur = conn.cursor()
    where_r = "AND election_id = %s" if election_id else ""
    where_t = "AND election_id = %s" if election_id else ""
    params = (election_id,) if election_id else ()

    details = []
    worst_status = "pass"

    def escalate(status):
        nonlocal worst_status
        rank = {"pass": 0, "warn": 1, "fail": 2}
        if rank[status] > rank[worst_status]:
            worst_status = status

    # 1. Turnout > 100%
    cur.execute(f"""
        SELECT COUNT(*), election_id, precinct_id, turnout_pct
        FROM turnout
        WHERE turnout_pct > 100 {where_t}
        GROUP BY election_id, precinct_id, turnout_pct
        ORDER BY turnout_pct DESC
        LIMIT 20;
    """ if not election_id else f"""
        SELECT 1, election_id, precinct_id, turnout_pct
        FROM turnout
        WHERE turnout_pct > 100 AND election_id = %s
        ORDER BY turnout_pct DESC
        LIMIT 20;
    """, params)
    over_turnout = cur.fetchall()
    if over_turnout:
        cur.execute(f"SELECT COUNT(*) FROM turnout WHERE turnout_pct > 100 {where_t};", params)
        total_over = cur.fetchone()[0]
        samples = [f"{r[1]}/{r[2][:12]}… = {r[3]:.1f}%" for r in over_turnout[:5]]
        details.append(f"Turnout > 100%: {total_over} precincts")
        details.extend([f"  {s}" for s in samples])
        escalate("warn")

    # 2. Vote percentage sum != ~100% per precinct per race
    cur.execute(f"""
        SELECT r.election_id, r.race_id, r.precinct_id,
               SUM(r.votes) as total_votes,
               SUM(r.vote_percentage) as pct_sum
        FROM results r
        WHERE r.votes > 0 {where_r}
        GROUP BY r.election_id, r.race_id, r.precinct_id
        HAVING ABS(SUM(r.vote_percentage) - 100) > 5
           AND SUM(r.vote_percentage) > 0
        LIMIT 20;
    """, params)
    bad_pct = cur.fetchall()
    if bad_pct:
        cur.execute(f"""
            SELECT COUNT(*) FROM (
                SELECT r.race_id, r.precinct_id
                FROM results r
                WHERE r.votes > 0 {where_r}
                GROUP BY r.election_id, r.race_id, r.precinct_id
                HAVING ABS(SUM(r.vote_percentage) - 100) > 5
                   AND SUM(r.vote_percentage) > 0
            ) sub;
        """, params)
        total_bad = cur.fetchone()[0]
        samples = [f"{r[0]}/{r[1][:12]}…/{r[2][:12]}… sum={r[4]:.1f}%"
                   for r in bad_pct[:5]]
        details.append(f"Vote % not summing to ~100%: {total_bad} race/precinct combos")
        details.extend([f"  {s}" for s in samples])
        escalate("warn")

    # 3. Elections with < 50 results
    cur.execute(f"""
        SELECT e.id, e.name, COUNT(r.id) as cnt
        FROM elections e
        LEFT JOIN results r ON r.election_id = e.id
        GROUP BY e.id, e.name
        HAVING COUNT(r.id) < 50;
    """)
    low_results = cur.fetchall()
    if low_results:
        for eid, ename, cnt in low_results:
            details.append(f"Low result count: {ename} ({eid}) = {cnt} results")
        escalate("warn")

    # 4. Zero-vote precincts (all candidates = 0 in a race)
    cur.execute(f"""
        SELECT r.election_id, r.race_id, r.precinct_id, SUM(r.votes) as total
        FROM results r
        WHERE 1=1 {where_r}
        GROUP BY r.election_id, r.race_id, r.precinct_id
        HAVING SUM(r.votes) = 0
        LIMIT 20;
    """, params)
    zero_precincts = cur.fetchall()
    if zero_precincts:
        cur.execute(f"""
            SELECT COUNT(*) FROM (
                SELECT r.race_id, r.precinct_id
                FROM results r
                WHERE 1=1 {where_r}
                GROUP BY r.election_id, r.race_id, r.precinct_id
                HAVING SUM(r.votes) = 0
            ) sub;
        """, params)
        total_zero = cur.fetchone()[0]
        details.append(f"Zero-vote precincts (all candidates = 0): {total_zero}")
        escalate("warn")

    # 5. Negative vote counts
    cur.execute(f"SELECT COUNT(*) FROM results WHERE votes < 0 {where_r};", params)
    neg_count = cur.fetchone()[0]
    if neg_count > 0:
        details.append(f"Negative vote counts: {neg_count}")
        escalate("fail")

    if not details:
        return CheckResult("Data quality", "pass", "All checks clean")
    return CheckResult("Data quality", worst_status,
                       f"{len(details)} issue(s) found", details)


# ═══════════════════════════════════════════════════════════════
# CHECK 6: GEOJSON COVERAGE
# ═══════════════════════════════════════════════════════════════

def _md5_16(*parts):
    """Compute 16-char MD5 hash matching the pipeline's make_id convention."""
    raw = "|".join(str(p).strip().lower() for p in parts)
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def _extract_geojson_precinct_ids(features, label):
    """Extract precinct IDs from GeoJSON features, computing MD5 where needed.

    Different GeoJSON files use different property conventions:
    - Lake/DuPage/DeKalb: have 'precinct_id' already set
    - Chicago: has 'ward' + 'precinct' → compute md5("chicago|Ward {w} Precinct {p}")
    - Suburban: has 'precinctid' → compute md5("cook_suburban|{precinctid}")
    """
    ids = set()
    for feat in features:
        props = feat.get("properties", {})

        # Try explicit precinct_id first (lake, dupage, dekalb)
        pid = props.get("precinct_id")
        if pid:
            ids.add(pid)
            continue

        # Chicago: compute from ward + precinct
        if label == "chicago":
            ward = props.get("ward")
            precinct = props.get("precinct")
            if ward is not None and precinct is not None:
                name = f"Ward {ward} Precinct {precinct}"
                pid = _md5_16("chicago", name)
                ids.add(pid)
            continue

        # Suburban: compute from precinctid
        if label == "suburban":
            precinctid = props.get("precinctid")
            if precinctid:
                pid = _md5_16("cook_suburban", precinctid)
                ids.add(pid)
            continue

    return ids


def check_geojson_coverage(conn, election_id=None):
    """Match DB precinct_ids against GeoJSON features from Supabase Storage."""
    if requests is None:
        return CheckResult("GeoJSON coverage", "warn",
                           "requests library not installed — skipping")

    cur = conn.cursor()

    # Get all precincts grouped by jurisdiction
    cur.execute("SELECT id, jurisdiction_id FROM precincts;")
    db_precincts = cur.fetchall()
    by_jurisdiction = defaultdict(set)
    all_db_ids = set()
    for pid, jurisdiction in db_precincts:
        by_jurisdiction[jurisdiction or "unknown"].add(pid)
        all_db_ids.add(pid)

    total_matched = 0
    details = []
    geojson_ids_all = set()

    jurisdiction_map = {
        "chicago": "cook_chicago",
        "suburban": "cook_suburban",
        "lake": "lake_county",
        "dupage": "dupage_county",
        "dekalb": "dekalb_county",
    }

    for label, filename in GEOJSON_FILES.items():
        url = f"{GEOJSON_BASE}/{filename}"
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                details.append(f"{label}: HTTP {resp.status_code} fetching {filename}")
                continue
            geo = resp.json()
        except Exception as e:
            details.append(f"{label}: error fetching — {e}")
            continue

        features = geo.get("features", [])
        geojson_ids = _extract_geojson_precinct_ids(features, label)
        geojson_ids_all |= geojson_ids

        # Match against DB
        matched = geojson_ids & all_db_ids

        # Find DB precincts for this jurisdiction that aren't in GeoJSON
        jname = jurisdiction_map.get(label, label)
        jur_precincts = by_jurisdiction.get(jname, set())
        unmatched_db = jur_precincts - geojson_ids

        total_in_geo = len(geojson_ids)
        match_pct = (len(matched) / total_in_geo * 100) if total_in_geo else 0

        details.append(
            f"{label}: {len(matched)}/{total_in_geo} GeoJSON features matched "
            f"({match_pct:.1f}%), {len(unmatched_db)} DB precincts unmatched")

        total_matched += len(matched)

        if unmatched_db and len(unmatched_db) <= 10:
            for pid in sorted(unmatched_db)[:10]:
                cur.execute(
                    "SELECT source_precinct_name FROM precincts WHERE id = %s;",
                    (pid,))
                row = cur.fetchone()
                name = row[0] if row else "?"
                details.append(f"  unmatched DB: {pid[:16]}… ({name})")

    overall_rate = (total_matched / len(geojson_ids_all) * 100) if geojson_ids_all else 0

    if overall_rate >= 90:
        status = "pass"
    elif overall_rate >= 70:
        status = "warn"
    else:
        status = "fail"

    return CheckResult("GeoJSON coverage", status,
                       f"{overall_rate:.1f}% match rate "
                       f"({total_matched}/{len(geojson_ids_all)} features)",
                       details)


# ═══════════════════════════════════════════════════════════════
# CHECK 7: ELECTION COMPLETENESS
# ═══════════════════════════════════════════════════════════════

def check_election_completeness(conn, election_id=None):
    """Per-election summary: race count, result count, precinct count, turnout status."""
    cur = conn.cursor()

    if election_id:
        cur.execute("SELECT id, name FROM elections WHERE id = %s;", (election_id,))
    else:
        cur.execute("SELECT id, name FROM elections ORDER BY id;")
    elections = cur.fetchall()

    if not elections:
        return CheckResult("Election completeness", "warn", "No elections found")

    # Batch queries
    cur.execute("SELECT election_id, COUNT(*) FROM races GROUP BY election_id;")
    race_counts = dict(cur.fetchall())

    cur.execute("SELECT election_id, COUNT(*) FROM results GROUP BY election_id;")
    result_counts = dict(cur.fetchall())

    cur.execute("SELECT election_id, COUNT(DISTINCT precinct_id) FROM results GROUP BY election_id;")
    precinct_counts = dict(cur.fetchall())

    cur.execute("SELECT election_id, COUNT(*) FROM turnout GROUP BY election_id;")
    turnout_counts = dict(cur.fetchall())

    details = []
    missing_turnout = []
    worst_status = "pass"

    for eid, ename in elections:
        rc = race_counts.get(eid, 0)
        res = result_counts.get(eid, 0)
        pc = precinct_counts.get(eid, 0)
        tc = turnout_counts.get(eid, 0)

        details.append(f"{ename}: {rc} races, {res:,} results, "
                       f"{pc} precincts, {tc:,} turnout rows")

        if tc == 0 and res > 0:
            missing_turnout.append(ename)

    if missing_turnout:
        details.append("")
        for m in missing_turnout:
            details.append(f"MISSING TURNOUT: {m}")
        worst_status = "fail"

    msg = f"{len(elections)} elections"
    if missing_turnout:
        msg += f", {len(missing_turnout)} missing turnout"

    return CheckResult("Election completeness", worst_status, msg, details)


# ═══════════════════════════════════════════════════════════════
# REPORT GENERATION
# ═══════════════════════════════════════════════════════════════

def save_markdown_report(results, path):
    """Save detailed results as a markdown report."""
    lines = [
        "# D4D Data Validation Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## Summary",
        "",
    ]

    passes = sum(1 for r in results if r.status == "pass")
    warns = sum(1 for r in results if r.status == "warn")
    fails = sum(1 for r in results if r.status == "fail")

    lines.append(f"| Status | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| PASS   | {passes}  |")
    lines.append(f"| WARN   | {warns}  |")
    lines.append(f"| FAIL   | {fails}  |")
    lines.append("")
    lines.append("---")
    lines.append("")

    for r in results:
        lines.append(r.to_markdown())

    content = "\n".join(lines)
    with open(path, "w") as f:
        f.write(content)
    return path


def run_all_checks(conn, election_id=None):
    """Run all validation checks and return list of CheckResults."""
    checks = [
        ("Orphaned references", lambda: check_orphaned_references(conn, election_id)),
        ("Cross-county coverage", lambda: check_cross_county_coverage(conn, election_id)),
        ("Materialized view", lambda: check_mv_freshness(conn, election_id)),
        ("Race normalization", lambda: check_race_normalization(conn, election_id)),
        ("Data quality", lambda: check_data_quality(conn, election_id)),
        ("GeoJSON coverage", lambda: check_geojson_coverage(conn, election_id)),
        ("Election completeness", lambda: check_election_completeness(conn, election_id)),
    ]

    results = []
    for name, fn in checks:
        try:
            result = fn()
            results.append(result)
        except Exception as e:
            conn.rollback()  # Reset transaction so subsequent checks work
            results.append(CheckResult(name, "fail", f"Check crashed: {e}"))
    return results


def print_summary(results):
    """Print colored summary to terminal."""
    print(f"\n{BOLD}D4D Data Validation Suite{RESET}")
    print("=" * 50)

    for r in results:
        print(r)

    print()
    passes = sum(1 for r in results if r.status == "pass")
    warns = sum(1 for r in results if r.status == "warn")
    fails = sum(1 for r in results if r.status == "fail")

    if fails:
        overall = f"{RED}FAIL{RESET}"
    elif warns:
        overall = f"{YELLOW}WARN{RESET}"
    else:
        overall = f"{GREEN}PASS{RESET}"

    print(f"Overall: {overall}  ({passes} pass, {warns} warn, {fails} fail)")
    return passes, warns, fails


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="D4D Data Validation Suite")
    parser.add_argument("--election", help="Scope to a specific election_id")
    parser.add_argument("--fix", action="store_true",
                        help="Auto-fix issues (refresh MV)")
    parser.add_argument("--report", default="/home/user/workspace/validation_report.md",
                        help="Path for markdown report")
    args = parser.parse_args()

    conn = get_connection()

    if args.fix:
        print("Running auto-fixes...")
        try:
            fix_mv(conn)
        except Exception as e:
            print(f"  MV refresh failed: {e}")
        print()

    results = run_all_checks(conn, args.election)
    passes, warns, fails = print_summary(results)

    report_path = save_markdown_report(results, args.report)
    print(f"\nDetails saved to {report_path}")

    conn.close()

    if fails > 0:
        sys.exit(2)
    elif warns > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
