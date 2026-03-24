#!/usr/bin/env python3
"""
D4D Election Heatmap Platform — Post-Fix Data Integrity Validator
=================================================================
Run AFTER fix_data_integrity.py has been applied to confirm all fixes worked.

Usage:
    python validate_data_integrity.py                     # Full validation
    python validate_data_integrity.py --check dupage      # Only DuPage checks
    python validate_data_integrity.py --check dekalb      # Only DeKalb checks
    python validate_data_integrity.py --check chicago     # Only Chicago checks
    python validate_data_integrity.py --check nullsource  # Only NULL source checks
    python validate_data_integrity.py --check candidates  # Only candidate checks
    python validate_data_integrity.py --check coverage    # GeoJSON coverage check
    python validate_data_integrity.py --check matchrates  # Results↔Turnout match rates

Outputs:
    - Console report with pass/fail for each check
    - JSON report at: ./sql_fixes/validation_report_YYYYMMDD_HHMMSS.json
    - Exits with code 0 (all pass) or 1 (failures found)

Author: D4D Pipeline — generated 2026-03-24
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

# ── Configuration ─────────────────────────────────────────────────────────────

SUPABASE_URL = "https://nfjfqdffulhqhszhlymo.supabase.co/rest/v1"
ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5mamZxZGZmdWxocWhzemhseW1vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5NTAzMDgsImV4cCI6MjA4OTUyNjMwOH0."
    "vNrXz0iCwA4scUCP2O75KWaLyh7LVQrYmUdnEGMnnCE"
)

SQL_FIXES_DIR = Path(__file__).parent / "sql_fixes"

# Expected GeoJSON precinct counts per jurisdiction (from audit)
GEOJSON_PRECINCT_COUNTS = {
    "chicago":       1291,
    "cook_suburban": 1430,
    "dupage_county": 600,
    "lake_county":   431,
    "dekalb_county": 65,
}

# Known-good precinct IDs for spot-check verification
# These are canonical IDs that MUST be present after fixes
KNOWN_GOOD_PRECINCT_IDS = {
    "chicago":       "4dd7f97133863c91",  # chicago|ward 01 precinct 01
    "dupage_county": "dd3418983fe7ebfd",  # dupage_county|wayne 17
    "dekalb_county": "0d9d2f95abe393ab",  # dekalb_county|dekalb 9
}

# IDs that should NO LONGER exist after fixes (old broken format)
BROKEN_PRECINCT_IDS = {
    "dupage_county": "bc7331ba391c573e",  # dupage_county|wayne  017  (double-space + zero-pad)
    "dekalb_county": "c47ab2aafb66a5f2",  # dekalb_county|dekalb 09  (zero-padded)
}

# Elections and their expected precinct counts (approximate ranges)
ELECTION_PRECINCT_EXPECTATIONS = {
    "2018_primary":          {"dupage": (900, 940), "dekalb": (65, 65)},
    "2018_general":          {"dupage": (180, 200), "dekalb": (65, 65)},
    "2020_primary":          {"dupage": (920, 935), "dekalb": (65, 65)},
    "2020_general":          {"dupage": (915, 930), "dekalb": (65, 65)},
    "2021_consolidated":     {"dupage": (45, 50)},
    "2022_primary":          {"chicago": (1291, 2100), "cook_suburban": (1429, 1430),
                               "dupage": (1100, 1160)},
    "2022_general":          {"chicago": (1290, 1291), "cook_suburban": (1430, 1430),
                               "dupage": (1100, 1160)},
    "2024_primary":          {"chicago": (1291, 1291), "cook_suburban": (1430, 1430),
                               "dupage": (600, 600)},
    "2024_general":          {"chicago": (1291, 1291), "cook_suburban": (1430, 1430),
                               "dupage": (600, 600)},
}


# ── Precinct Normalization (mirrors fix_data_integrity.py) ───────────────────

def normalize_precinct_name(name: str, jurisdiction: str) -> str:
    name = name.strip()
    if jurisdiction == "chicago":
        m = re.match(r'Ward\s+(\d+)\s+Precinct\s+(\d+)', name, re.IGNORECASE)
        if m:
            return f"Ward {int(m.group(1)):02d} Precinct {int(m.group(2)):02d}"
    elif jurisdiction == "dupage_county":
        name = re.sub(r'\s*-\s*\d+\s*$', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        name = re.sub(r'\b0+(\d)', r'\1', name)
    elif jurisdiction == "dekalb_county":
        name = re.sub(r'\b0+(\d)', r'\1', name)
    return name.strip()


def compute_canonical_precinct_id(jurisdiction: str, normalized_name: str) -> str:
    key = f"{jurisdiction}|{normalized_name.lower()}"
    return hashlib.md5(key.encode()).hexdigest()[:16]


# ── API Client ───────────────────────────────────────────────────────────────

class SupabaseClient:
    def __init__(self):
        self.headers = {
            "apikey": ANON_KEY,
            "Authorization": f"Bearer {ANON_KEY}",
            "Content-Type": "application/json",
            "Prefer": "count=exact",
        }

    def get_all(self, table: str, params: dict = None, batch: int = 1000) -> list:
        all_rows = []
        offset = 0
        while True:
            p = dict(params or {})
            p["limit"] = batch
            p["offset"] = offset
            resp = requests.get(
                f"{SUPABASE_URL}/{table}",
                headers=self.headers,
                params=p,
                timeout=60,
            )
            resp.raise_for_status()
            rows = resp.json()
            all_rows.extend(rows)
            if len(rows) < batch:
                break
            offset += batch
            time.sleep(0.05)
        return all_rows

    def get(self, table: str, params: dict = None, limit: int = 100) -> list:
        p = dict(params or {})
        p["limit"] = limit
        resp = requests.get(
            f"{SUPABASE_URL}/{table}",
            headers=self.headers,
            params=p,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def count(self, table: str, params: dict = None) -> int:
        headers = dict(self.headers)
        p = dict(params or {})
        p["limit"] = 0
        resp = requests.get(
            f"{SUPABASE_URL}/{table}",
            headers=headers,
            params=p,
            timeout=30,
        )
        resp.raise_for_status()
        cr = resp.headers.get("Content-Range", "0/0")
        try:
            return int(cr.split("/")[1])
        except (IndexError, ValueError):
            return 0


# ── Check Result Tracker ─────────────────────────────────────────────────────

class CheckResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.details: list[dict] = []

    def pass_(self, msg: str, data: dict = None):
        self.passed += 1
        self.details.append({"status": "PASS", "message": msg, "data": data or {}})
        print(f"    ✓ PASS  {msg}")

    def fail(self, msg: str, data: dict = None):
        self.failed += 1
        self.details.append({"status": "FAIL", "message": msg, "data": data or {}})
        print(f"    ✗ FAIL  {msg}")

    def warn(self, msg: str, data: dict = None):
        self.warnings += 1
        self.details.append({"status": "WARN", "message": msg, "data": data or {}})
        print(f"    ⚠ WARN  {msg}")

    def summary(self) -> str:
        total = self.passed + self.failed + self.warnings
        status = "PASS" if self.failed == 0 else "FAIL"
        return f"[{status}] {self.name}: {self.passed}/{total} passed, {self.failed} failed, {self.warnings} warnings"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "overall": "PASS" if self.failed == 0 else "FAIL",
            "details": self.details,
        }


# ── Check 1: DuPage Precinct IDs ─────────────────────────────────────────────

def check_dupage_precinct_ids(client: SupabaseClient) -> CheckResult:
    print("\n" + "-" * 60)
    print("CHECK 1: DuPage Precinct ID Correctness")
    print("-" * 60)
    result = CheckResult("DuPage Precinct IDs")

    broken_elections = [
        "2018_primary", "2018_general",
        "2020_primary", "2020_general",
        "2021_consolidated",
        "2022_primary", "2022_general",
    ]

    for election_id in broken_elections:
        rows = client.get(
            "results",
            params={
                "election_id": f"eq.{election_id}",
                "source_file": f"like.SBOE DuPage%",
                "select": "precinct_id,source_precinct_name",
            },
            limit=200,
        )

        if not rows:
            result.warn(f"{election_id}: No DuPage results found (may not be loaded)")
            continue

        broken_count = 0
        total = len(rows)
        for row in rows:
            pid = row.get("precinct_id", "")
            raw_name = row.get("source_precinct_name", "") or ""
            if not raw_name:
                continue
            norm = normalize_precinct_name(raw_name, "dupage_county")
            expected_pid = compute_canonical_precinct_id("dupage_county", norm)
            if pid != expected_pid:
                broken_count += 1

        if broken_count == 0:
            result.pass_(f"{election_id}: All {total} sampled DuPage precincts have canonical IDs")
        else:
            pct = round(100 * broken_count / total, 1)
            result.fail(
                f"{election_id}: {broken_count}/{total} ({pct}%) DuPage precincts still have broken IDs",
                {"election": election_id, "broken": broken_count, "sampled": total},
            )

    # Spot-check: broken ID must not exist
    broken_id = BROKEN_PRECINCT_IDS.get("dupage_county")
    if broken_id:
        count = client.count("results", {"precinct_id": f"eq.{broken_id}"})
        if count == 0:
            result.pass_(f"Broken DuPage ID '{broken_id}' not present in results")
        else:
            result.fail(
                f"Broken DuPage ID '{broken_id}' still found in {count} result rows",
                {"broken_id": broken_id, "count": count},
            )

    return result


# ── Check 2: DeKalb Precinct IDs ─────────────────────────────────────────────

def check_dekalb_precinct_ids(client: SupabaseClient) -> CheckResult:
    print("\n" + "-" * 60)
    print("CHECK 2: DeKalb Precinct ID Correctness")
    print("-" * 60)
    result = CheckResult("DeKalb Precinct IDs")

    broken_elections = ["2018_primary", "2018_general", "2020_primary", "2020_general"]

    for election_id in broken_elections:
        rows = client.get(
            "results",
            params={
                "election_id": f"eq.{election_id}",
                "source_file": f"like.SBOE DeKalb%",
                "select": "precinct_id,source_precinct_name",
            },
            limit=200,
        )

        if not rows:
            result.warn(f"{election_id}: No DeKalb results found")
            continue

        broken_count = 0
        total = len(rows)
        for row in rows:
            pid = row.get("precinct_id", "")
            raw_name = row.get("source_precinct_name", "") or ""
            if not raw_name:
                continue
            norm = normalize_precinct_name(raw_name, "dekalb_county")
            expected_pid = compute_canonical_precinct_id("dekalb_county", norm)
            if pid != expected_pid:
                broken_count += 1

        if broken_count == 0:
            result.pass_(f"{election_id}: All {total} DeKalb precincts have canonical IDs")
        else:
            pct = round(100 * broken_count / total, 1)
            result.fail(
                f"{election_id}: {broken_count}/{total} ({pct}%) DeKalb precincts still broken",
                {"election": election_id, "broken": broken_count, "sampled": total},
            )

    # Spot-check: DEKALB 09 broken ID must not exist
    broken_id = BROKEN_PRECINCT_IDS.get("dekalb_county")
    if broken_id:
        count = client.count("results", {"precinct_id": f"eq.{broken_id}"})
        if count == 0:
            result.pass_(f"Broken DeKalb ID '{broken_id}' (DEKALB 09) not present in results")
        else:
            result.fail(
                f"Broken DeKalb ID '{broken_id}' (DEKALB 09) still found in {count} rows",
                {"broken_id": broken_id, "count": count},
            )

    # Verify 2022+ DeKalb still correct (regression check)
    rows_2022 = client.get(
        "results",
        params={
            "election_id": "eq.2022_primary",
            "source_file": "like.SBOE DeKalb%",
            "select": "precinct_id,source_precinct_name",
        },
        limit=100,
    )
    broken_2022 = 0
    for row in rows_2022:
        pid = row.get("precinct_id", "")
        raw = row.get("source_precinct_name", "") or ""
        if not raw:
            continue
        norm = normalize_precinct_name(raw, "dekalb_county")
        if pid != compute_canonical_precinct_id("dekalb_county", norm):
            broken_2022 += 1
    if broken_2022 == 0:
        result.pass_(f"Regression: 2022_primary DeKalb IDs unaffected ({len(rows_2022)} checked)")
    else:
        result.fail(f"Regression: 2022_primary DeKalb has {broken_2022} broken IDs (REGRESSION!)")

    return result


# ── Check 3: Chicago Precinct IDs ────────────────────────────────────────────

def check_chicago_precinct_ids(client: SupabaseClient) -> CheckResult:
    print("\n" + "-" * 60)
    print("CHECK 3: Chicago Precinct ID Correctness")
    print("-" * 60)
    result = CheckResult("Chicago Precinct IDs")

    chicago_elections = [
        "2022_primary", "2022_general",
        "2024_primary", "2024_general",
        "2026_primary",
    ]

    for election_id in chicago_elections:
        # Check turnout
        rows = client.get(
            "turnout",
            params={
                "election_id": f"eq.{election_id}",
                "select": "precinct_id,source_precinct_name,source_file",
            },
            limit=200,
        )
        if not rows:
            result.warn(f"{election_id}: No Chicago turnout rows found")
            continue

        broken = 0
        for row in rows:
            src = row.get("source_file", "") or ""
            # Only check Chicago rows
            if "chicago" not in src.lower() and "cboe" not in src.lower():
                continue
            pid = row.get("precinct_id", "")
            raw = row.get("source_precinct_name", "") or ""
            if not raw:
                continue
            norm = normalize_precinct_name(raw, "chicago")
            expected = compute_canonical_precinct_id("chicago", norm)
            if pid != expected:
                broken += 1

        if broken == 0:
            result.pass_(f"{election_id}: Chicago turnout IDs all canonical ({len(rows)} checked)")
        else:
            result.fail(
                f"{election_id}: {broken} Chicago turnout rows have non-canonical IDs",
                {"election": election_id, "broken": broken},
            )

    # Known-good spot check
    known_id = KNOWN_GOOD_PRECINCT_IDS.get("chicago")
    if known_id:
        count = client.count("results", {
            "precinct_id": f"eq.{known_id}",
            "election_id": "eq.2024_general",
        })
        if count > 0:
            result.pass_(f"Known Chicago precinct_id '{known_id}' (Ward 01 Precinct 01) found in 2024_general")
        else:
            result.warn(f"Known Chicago precinct_id '{known_id}' not found in 2024_general results")

    return result


# ── Check 4: NULL Source Files ────────────────────────────────────────────────

def check_null_source_files(client: SupabaseClient) -> CheckResult:
    print("\n" + "-" * 60)
    print("CHECK 4: NULL source_file Cleanup")
    print("-" * 60)
    result = CheckResult("NULL Source Files")

    null_elections = [
        "cook_2021_consolidated",
        "cook_2023_consolidated",
        "2026_primary",
    ]

    for election_id in null_elections:
        count = client.count("turnout", {
            "election_id": f"eq.{election_id}",
            "source_file": "is.null",
        })

        if count == 0:
            result.pass_(f"{election_id}: 0 turnout rows with NULL source_file")
        else:
            result.fail(
                f"{election_id}: {count} turnout rows still have NULL source_file",
                {"election": election_id, "null_count": count},
            )

    # Global check — no election should have NULL source_file in turnout
    total_null = client.count("turnout", {"source_file": "is.null"})
    if total_null == 0:
        result.pass_("Global: No NULL source_file rows in turnout table")
    else:
        result.warn(
            f"Global: {total_null} turnout rows still have NULL source_file (may include new data)",
            {"global_null_count": total_null},
        )

    return result


# ── Check 5: Candidate Deduplication ─────────────────────────────────────────

def check_candidate_deduplication(client: SupabaseClient) -> CheckResult:
    print("\n" + "-" * 60)
    print("CHECK 5: Candidate Deduplication")
    print("-" * 60)
    result = CheckResult("Candidate Deduplication")

    print("  Fetching candidates...")
    all_candidates = client.get_all(
        "candidates",
        params={"select": "id,name,party"},
    )
    total = len(all_candidates)
    print(f"  Total candidates: {total}")

    # Group by name
    by_name: dict[str, list] = {}
    for c in all_candidates:
        name = (c.get("name") or "").strip()
        if name:
            by_name.setdefault(name, []).append(c)

    duplicates = {n: v for n, v in by_name.items() if len(v) > 1}
    dup_count = len(duplicates)

    # Pre-fix baseline from audit: 1,038
    AUDIT_BASELINE = 1038
    if dup_count == 0:
        result.pass_(f"0 duplicate candidate names (all {total} candidates are unique)")
    elif dup_count < AUDIT_BASELINE:
        result.pass_(
            f"Duplicate-name candidates reduced from {AUDIT_BASELINE} → {dup_count} "
            f"({AUDIT_BASELINE - dup_count} fixed)",
            {"remaining_duplicates": dup_count, "fixed": AUDIT_BASELINE - dup_count},
        )
    else:
        result.fail(
            f"Still {dup_count} duplicate candidate names (baseline was {AUDIT_BASELINE})",
            {"duplicate_count": dup_count},
        )

    # Check party normalization — should not see raw aliases
    non_canonical_parties = []
    bad_aliases = {
        "Democrat", "DEM", "DEMOCRATIC", "dem",
        "REP", "REPUBLICAN", "rep",
        "NON", "NP", "IND",
    }
    party_counts: dict[str, int] = {}
    for c in all_candidates:
        p = c.get("party") or ""
        party_counts[p] = party_counts.get(p, 0) + 1
        if p in bad_aliases:
            non_canonical_parties.append(p)

    if not non_canonical_parties:
        result.pass_(f"All party labels are canonical (no raw aliases found)")
    else:
        from collections import Counter
        alias_counts = Counter(non_canonical_parties)
        result.fail(
            f"{len(non_canonical_parties)} candidates still have non-canonical party aliases",
            {"alias_counts": dict(alias_counts)},
        )

    # Report party distribution
    top_parties = sorted(party_counts.items(), key=lambda x: -x[1])[:10]
    print(f"\n  Party distribution (top 10):")
    for party, cnt in top_parties:
        label = repr(party) if party else "NULL"
        print(f"    {label:25s}  {cnt:,}")

    # Sample remaining duplicates
    if duplicates:
        print(f"\n  Sample remaining duplicates (first 5):")
        for name, entries in list(duplicates.items())[:5]:
            parties = [repr(e.get("party") or "NULL") for e in entries]
            print(f"    '{name}': {len(entries)} IDs, parties: {', '.join(parties)}")

    return result


# ── Check 6: Results↔Turnout Match Rates ─────────────────────────────────────

def check_match_rates(client: SupabaseClient) -> CheckResult:
    print("\n" + "-" * 60)
    print("CHECK 6: Results ↔ Turnout Match Rates")
    print("-" * 60)
    result = CheckResult("Results-Turnout Match Rates")

    # Key elections to validate — focus on previously-broken ones
    check_elections = [
        ("2018_primary",   "dupage_county",  "SBOE DuPage%"),
        ("2018_general",   "dupage_county",  "SBOE DuPage%"),
        ("2020_primary",   "dupage_county",  "SBOE DuPage%"),
        ("2020_general",   "dupage_county",  "SBOE DuPage%"),
        ("2018_primary",   "dekalb_county",  "SBOE DeKalb%"),
        ("2018_general",   "dekalb_county",  "SBOE DeKalb%"),
        ("2020_primary",   "dekalb_county",  "SBOE DeKalb%"),
        ("2020_general",   "dekalb_county",  "SBOE DeKalb%"),
        ("2024_primary",   "chicago",        "SBOE 2024 Primary%"),
        ("2024_general",   "chicago",        "SBOE 2024 General%"),
        ("cook_2021_consolidated", "cook_suburban", None),
        ("cook_2023_consolidated", "cook_suburban", None),
    ]

    for election_id, jurisdiction, source_pattern in check_elections:
        # Get result precinct IDs
        result_params = {
            "election_id": f"eq.{election_id}",
            "select": "precinct_id",
        }
        if source_pattern:
            result_params["source_file"] = f"like.{source_pattern}"

        result_rows = client.get("results", params=result_params, limit=2000)
        result_pids = {r["precinct_id"] for r in result_rows if r.get("precinct_id")}

        # Get turnout precinct IDs
        turnout_params = {
            "election_id": f"eq.{election_id}",
            "select": "precinct_id",
        }
        if source_pattern:
            turnout_params["source_file"] = f"like.{source_pattern}"

        turnout_rows = client.get("turnout", params=turnout_params, limit=2000)
        turnout_pids = {r["precinct_id"] for r in turnout_rows if r.get("precinct_id")}

        if not result_pids or not turnout_pids:
            result.warn(f"{election_id}/{jurisdiction}: No data for match-rate check")
            continue

        matched = result_pids & turnout_pids
        total = max(len(result_pids), len(turnout_pids))
        pct = round(100 * len(matched) / total, 1) if total > 0 else 0

        # Expected: DuPage 2018–2021 should now match since both use same normalization
        # (turnout was never loaded for DuPage 2018–2021, so N/A)
        if jurisdiction == "dupage_county" and election_id in [
            "2018_primary", "2018_general", "2020_primary", "2020_general"
        ]:
            if not turnout_pids:
                result.warn(
                    f"{election_id}/dupage: No turnout data exists (expected — never loaded). "
                    f"Results: {len(result_pids)} precincts."
                )
            else:
                if pct >= 95:
                    result.pass_(f"{election_id}/dupage: {pct}% match rate ({len(matched)}/{total})")
                else:
                    result.fail(f"{election_id}/dupage: Only {pct}% match rate",
                                {"pct": pct, "matched": len(matched), "total": total})

        elif jurisdiction == "dekalb_county":
            if pct == 100:
                result.pass_(f"{election_id}/dekalb: 100% match ({len(matched)} precincts)")
            elif pct >= 95:
                result.pass_(f"{election_id}/dekalb: {pct}% match ({len(matched)}/{total})")
            else:
                result.fail(
                    f"{election_id}/dekalb: {pct}% match rate (expected 100%)",
                    {"pct": pct, "matched": len(matched), "total": total,
                     "unmatched_sample": list(result_pids - turnout_pids)[:5]},
                )

        elif election_id in ("cook_2021_consolidated", "cook_2023_consolidated"):
            if pct >= 80:
                result.pass_(f"{election_id}: {pct}% match rate ({len(matched)}/{total})")
            elif pct >= 50:
                result.warn(
                    f"{election_id}: {pct}% match rate (improved from 22.9% baseline)",
                    {"pct": pct, "matched": len(matched), "total": total},
                )
            else:
                result.fail(
                    f"{election_id}: {pct}% match rate (too low — fix may not have worked)",
                    {"pct": pct, "matched": len(matched), "total": total},
                )

        else:
            if pct >= 99:
                result.pass_(f"{election_id}/{jurisdiction}: {pct}% match rate")
            else:
                result.warn(
                    f"{election_id}/{jurisdiction}: {pct}% match rate",
                    {"pct": pct, "matched": len(matched), "total": total},
                )

    return result


# ── Check 7: GeoJSON Coverage Spot-Check ─────────────────────────────────────

def check_geojson_coverage(client: SupabaseClient) -> CheckResult:
    print("\n" + "-" * 60)
    print("CHECK 7: GeoJSON Coverage Spot-Check")
    print("-" * 60)
    result = CheckResult("GeoJSON Coverage")

    # For each jurisdiction, verify the 2024_general election has
    # correct precinct count (the fully-correct reference election)
    reference_elections = {
        "chicago":       "2024_general",
        "cook_suburban": "2024_general",
        "dupage_county": "2024_general",
        "lake_county":   "2024_general",
        "dekalb_county": "2024_general",
    }

    source_patterns = {
        "chicago":       "SBOE 2024 General - Chicago%",
        "cook_suburban": "SBOE 2024 General - Suburban Cook%",
        "dupage_county": "SBOE DuPage 2024GE%",
        "lake_county":   "Lake County 2024%",
        "dekalb_county": "SBOE DeKalb 2024GE%",
    }

    for jurisdiction, election_id in reference_elections.items():
        expected_count = GEOJSON_PRECINCT_COUNTS[jurisdiction]
        source_pat = source_patterns.get(jurisdiction)

        params = {
            "election_id": f"eq.{election_id}",
            "select": "precinct_id",
        }
        if source_pat:
            params["source_file"] = f"like.{source_pat}"

        rows = client.get("results", params=params, limit=2000)
        actual_pids = {r["precinct_id"] for r in rows if r.get("precinct_id")}
        actual_count = len(actual_pids)

        pct = round(100 * actual_count / expected_count, 1) if expected_count > 0 else 0

        if pct >= 99:
            result.pass_(
                f"{jurisdiction} 2024_general: {actual_count}/{expected_count} "
                f"precinct IDs ({pct}% coverage)"
            )
        elif pct >= 90:
            result.warn(
                f"{jurisdiction} 2024_general: {actual_count}/{expected_count} "
                f"({pct}% coverage)",
                {"jurisdiction": jurisdiction, "actual": actual_count, "expected": expected_count},
            )
        else:
            result.fail(
                f"{jurisdiction} 2024_general: Only {actual_count}/{expected_count} "
                f"({pct}% coverage) — possible ID format issue",
                {"jurisdiction": jurisdiction, "actual": actual_count, "expected": expected_count},
            )

    # Now check the previously-broken elections
    print("\n  Checking post-fix GeoJSON coverage for previously-broken elections:")
    previously_broken = [
        ("2018_primary", "dupage_county", "SBOE DuPage 2018GP%", 600),  # ~930 unique but GeoJSON=600
        ("2018_general", "dupage_county", "SBOE DuPage 2018GE%", 600),
        ("2020_primary", "dekalb_county", "SBOE DeKalb 2020GP%", 65),
        ("2020_general", "dekalb_county", "SBOE DeKalb 2020GE%", 65),
    ]

    for election_id, jurisdiction, source_pat, geojson_count in previously_broken:
        rows = client.get(
            "results",
            params={
                "election_id": f"eq.{election_id}",
                "source_file": f"like.{source_pat}",
                "select": "precinct_id,source_precinct_name",
            },
            limit=1000,
        )
        if not rows:
            result.warn(f"{election_id}/{jurisdiction}: No results to check")
            continue

        # Re-verify each precinct_id matches canonical
        correct = 0
        incorrect = 0
        for row in rows:
            pid = row.get("precinct_id", "")
            raw = row.get("source_precinct_name", "") or ""
            if not raw:
                continue
            norm = normalize_precinct_name(raw, jurisdiction)
            expected = compute_canonical_precinct_id(jurisdiction, norm)
            if pid == expected:
                correct += 1
            else:
                incorrect += 1

        total = correct + incorrect
        pct = round(100 * correct / total, 1) if total > 0 else 0

        if incorrect == 0:
            result.pass_(
                f"{election_id}/{jurisdiction}: All {total} sampled IDs match canonical format ({pct}%)"
            )
        else:
            result.fail(
                f"{election_id}/{jurisdiction}: {incorrect}/{total} IDs still broken ({100 - pct:.1f}% failure)",
                {"election": election_id, "incorrect": incorrect, "total": total},
            )

    return result


# ── Check 8: Normalization Function Self-Test ─────────────────────────────────

def check_normalization_function() -> CheckResult:
    print("\n" + "-" * 60)
    print("CHECK 8: Normalization Function Self-Test")
    print("-" * 60)
    result = CheckResult("Normalization Self-Test")

    test_cases = [
        # (raw, jurisdiction, expected_normalized, expected_pid)
        ("Ward 4 Precinct 1",     "chicago",       "Ward 04 Precinct 01",
         hashlib.md5("chicago|ward 04 precinct 01".encode()).hexdigest()[:16]),
        ("Ward 31 Precinct 9",    "chicago",       "Ward 31 Precinct 09",
         hashlib.md5("chicago|ward 31 precinct 09".encode()).hexdigest()[:16]),
        ("Wayne  017",            "dupage_county", "Wayne 17",
         hashlib.md5("dupage_county|wayne 17".encode()).hexdigest()[:16]),
        ("Bloomingdale  013 - 0103", "dupage_county", "Bloomingdale 13",
         hashlib.md5("dupage_county|bloomingdale 13".encode()).hexdigest()[:16]),
        ("Addison  001",          "dupage_county", "Addison 1",
         hashlib.md5("dupage_county|addison 1".encode()).hexdigest()[:16]),
        ("DEKALB 09",             "dekalb_county", "DEKALB 9",
         hashlib.md5("dekalb_county|dekalb 9".encode()).hexdigest()[:16]),
        ("AFTON 01",              "dekalb_county", "AFTON 1",
         hashlib.md5("dekalb_county|afton 1".encode()).hexdigest()[:16]),
        ("SYCAMORE 10",           "dekalb_county", "SYCAMORE 10",
         hashlib.md5("dekalb_county|sycamore 10".encode()).hexdigest()[:16]),
        ("7000001",               "cook_suburban", "7000001",
         hashlib.md5("cook_suburban|7000001".encode()).hexdigest()[:16]),
    ]

    for raw, jur, expected_norm, expected_pid in test_cases:
        actual_norm = normalize_precinct_name(raw, jur)
        actual_pid = compute_canonical_precinct_id(jur, actual_norm)

        if actual_norm == expected_norm and actual_pid == expected_pid:
            result.pass_(f"[{jur}] '{raw}' → '{actual_norm}' = {actual_pid}")
        elif actual_norm != expected_norm:
            result.fail(
                f"[{jur}] Normalize FAIL: '{raw}' → '{actual_norm}' (expected '{expected_norm}')",
                {"raw": raw, "actual": actual_norm, "expected": expected_norm},
            )
        else:
            result.fail(
                f"[{jur}] Hash FAIL for '{actual_norm}': got {actual_pid}, expected {expected_pid}",
                {"norm": actual_norm, "actual_pid": actual_pid, "expected_pid": expected_pid},
            )

    return result


# ── Check 9: Database Integrity Counts ───────────────────────────────────────

def check_database_counts(client: SupabaseClient) -> CheckResult:
    print("\n" + "-" * 60)
    print("CHECK 9: Database Row Counts (sanity check vs audit baseline)")
    print("-" * 60)
    result = CheckResult("Database Counts")

    # Baseline from audit — these should still be approximately correct
    # (fixes don't delete rows, only update precinct_ids)
    BASELINES = {
        "results":    (4_000_000, 5_000_000),  # ~4.4M ± reasonable margin
        "turnout":    (25_000, 35_000),          # ~30,111
        "candidates": (10_000, 12_500),          # ~11,362
        "races":      (4_500, 6_000),            # ~5,500
    }

    for table, (min_expected, max_expected) in BASELINES.items():
        actual = client.count(table)
        if min_expected <= actual <= max_expected:
            result.pass_(f"{table}: {actual:,} rows (within expected range {min_expected:,}–{max_expected:,})")
        elif actual < min_expected:
            result.fail(
                f"{table}: {actual:,} rows — below expected minimum {min_expected:,} "
                f"(data may have been deleted accidentally!)",
                {"table": table, "actual": actual, "min": min_expected},
            )
        else:
            result.warn(
                f"{table}: {actual:,} rows — above expected maximum {max_expected:,} "
                f"(new data loaded?)",
                {"table": table, "actual": actual, "max": max_expected},
            )

    return result


# ── Full Validation Runner ────────────────────────────────────────────────────

def run_all_checks(client: SupabaseClient, check_filter: Optional[str] = None) -> list[CheckResult]:
    """Run all validation checks and return results."""
    all_results = []
    start_time = time.time()

    check_map = {
        "normalize":    (check_normalization_function,  False),  # no client needed
        "dupage":       (check_dupage_precinct_ids,     True),
        "dekalb":       (check_dekalb_precinct_ids,     True),
        "chicago":      (check_chicago_precinct_ids,    True),
        "nullsource":   (check_null_source_files,       True),
        "candidates":   (check_candidate_deduplication, True),
        "matchrates":   (check_match_rates,             True),
        "coverage":     (check_geojson_coverage,        True),
        "counts":       (check_database_counts,         True),
    }

    for check_name, (fn, needs_client) in check_map.items():
        if check_filter and check_name != check_filter:
            continue
        try:
            if needs_client:
                check_result = fn(client)
            else:
                check_result = fn()
            all_results.append(check_result)
        except Exception as e:
            print(f"\n  ERROR in {check_name}: {e}")
            import traceback
            traceback.print_exc()
            error_result = CheckResult(check_name)
            error_result.fail(f"Check crashed with exception: {e}")
            all_results.append(error_result)

    elapsed = time.time() - start_time
    return all_results, elapsed


def print_final_report(results: list[CheckResult], elapsed: float, dry_run: bool = False):
    """Print consolidated pass/fail report."""
    print("\n" + "=" * 70)
    print("VALIDATION REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {elapsed:.1f}s")
    print("=" * 70)

    total_pass = sum(r.passed for r in results)
    total_fail = sum(r.failed for r in results)
    total_warn = sum(r.warnings for r in results)

    print(f"\nResults: {total_pass} passed  |  {total_fail} failed  |  {total_warn} warnings\n")

    for r in results:
        status_icon = "✓" if r.failed == 0 else "✗"
        print(f"  {status_icon}  {r.summary()}")

    overall = "ALL CHECKS PASSED" if total_fail == 0 else f"VALIDATION FAILED ({total_fail} failures)"
    print(f"\n{'=' * 70}")
    print(f"OVERALL: {overall}")
    print("=" * 70)

    return total_fail == 0


def save_report(results: list[CheckResult], elapsed: float) -> Path:
    """Save validation results to JSON."""
    SQL_FIXES_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = SQL_FIXES_DIR / f"validation_report_{timestamp}.json"

    report = {
        "generated_at": datetime.now().isoformat(),
        "duration_seconds": round(elapsed, 2),
        "summary": {
            "total_passed": sum(r.passed for r in results),
            "total_failed": sum(r.failed for r in results),
            "total_warnings": sum(r.warnings for r in results),
            "overall_pass": all(r.failed == 0 for r in results),
        },
        "checks": [r.to_dict() for r in results],
    }

    path.write_text(json.dumps(report, indent=2))
    print(f"\nValidation report saved: {path}")
    return path


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="D4D Data Integrity Validator — run after fix_data_integrity.py"
    )
    parser.add_argument(
        "--check",
        choices=["all", "normalize", "dupage", "dekalb", "chicago",
                 "nullsource", "candidates", "matchrates", "coverage", "counts"],
        default="all",
        help="Which check to run (default: all)",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip saving JSON report",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("D4D Election Heatmap — Data Integrity Validator")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Check: {args.check}")
    print("=" * 70)
    print("\nConnecting to Supabase...", end=" ")

    client = SupabaseClient()

    # Quick connectivity test
    try:
        test = client.get("elections", limit=1)
        print(f"OK (found {len(test)} election row)")
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(2)

    check_filter = None if args.check == "all" else args.check
    results, elapsed = run_all_checks(client, check_filter=check_filter)

    all_passed = print_final_report(results, elapsed)

    if not args.no_report:
        save_report(results, elapsed)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
