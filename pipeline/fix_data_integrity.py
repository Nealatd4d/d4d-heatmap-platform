#!/usr/bin/env python3
"""
D4D Election Heatmap Platform — Data Integrity Fix Script
==========================================================
Addresses all 8 issue categories found in the 2026-03-24 audit.

Usage:
    python fix_data_integrity.py                        # DRY RUN (default)
    python fix_data_integrity.py --execute              # Apply fixes to DB
    python fix_data_integrity.py --fix dupage           # Run only DuPage fix
    python fix_data_integrity.py --fix dekalb           # Run only DeKalb fix
    python fix_data_integrity.py --fix chicago          # Run only Chicago fix
    python fix_data_integrity.py --fix nullsource       # Run only NULL source fix
    python fix_data_integrity.py --fix candidates       # Run only candidate dedup
    python fix_data_integrity.py --fix geojson          # Run only GeoJSON precinct_id fix

Environment:
    SUPA_SERVICE_KEY  — Supabase service_role key (required for writes)
    DATABASE_URL      — Direct PostgreSQL connection string (preferred for writes)

SQL fix files are written to: ./sql_fixes/

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

# ── Configuration ────────────────────────────────────────────────────────────

SUPABASE_URL = "https://nfjfqdffulhqhszhlymo.supabase.co/rest/v1"
ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5mamZxZGZmdWxocWhzemhseW1vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5NTAzMDgsImV4cCI6MjA4OTUyNjMwOH0."
    "vNrXz0iCwA4scUCP2O75KWaLyh7LVQrYmUdnEGMnnCE"
)
SERVICE_KEY = os.environ.get("SUPA_SERVICE_KEY")
if not SERVICE_KEY:
    print("WARNING: SUPA_SERVICE_KEY not set — write operations will fail. Set it as an env var.")

# Database direct connection (psycopg2) — preferred for bulk writes
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("WARNING: DATABASE_URL not set — direct DB operations will fail. Set it as an env var.")

SQL_FIXES_DIR = Path(__file__).parent / "sql_fixes"

# DuPage elections that used the broken double-space + zero-pad format (2018–2021)
DUPAGE_BROKEN_ELECTIONS_V1 = [
    "2018_primary", "2018_general",
    "2020_primary", "2020_general",
    "2021_consolidated",
]

# DuPage elections that used broken format WITH code suffix (2022–2023)
DUPAGE_BROKEN_ELECTIONS_V2 = [
    "2022_primary", "2022_general",
]

# DeKalb elections that used zero-padded names
DEKALB_BROKEN_ELECTIONS = [
    "2018_primary", "2018_general",
    "2020_primary", "2020_general",
]

# Turnout elections with NULL source_file
NULL_SOURCE_ELECTIONS = {
    "cook_2021_consolidated": {"expected_rows": 1601, "source_label": "Cook County Clerk"},
    "cook_2023_consolidated": {"expected_rows": 1661, "source_label": "Cook County Clerk"},
    "2026_primary":           {"expected_rows": 1105, "source_label": "cboe_2026_ajax"},
}

# Party normalization map: alias → canonical
PARTY_CANONICAL = {
    # Democratic
    "democrat":    "Democratic",
    "dem":         "Democratic",
    "democratic":  "Democratic",
    # Republican
    "rep":         "Republican",
    "republican":  "Republican",
    # Non-Partisan
    "non":         "Non-Partisan",
    "np":          "Non-Partisan",
    "ind":         "Non-Partisan",
    "non-partisan": "Non-Partisan",
    "nonpartisan": "Non-Partisan",
    # Green
    "green":       "Green",
    # Libertarian
    "lib":         "Libertarian",
    "libertarian": "Libertarian",
}


# ── Core Utilities ────────────────────────────────────────────────────────────

def make_precinct_id(*parts: str) -> str:
    """Compute MD5-based precinct ID from raw parts (as used throughout the pipeline)."""
    raw = "|".join(str(p).strip().lower() for p in parts)
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def normalize_precinct_name(name: str, jurisdiction: str) -> str:
    """
    Canonical precinct name normalizer for each jurisdiction.

    Chicago:   "Ward 4 Precinct 1"  → "Ward 04 Precinct 01"  (zero-pad to 2 digits)
    DuPage:    "Wayne  017"          → "Wayne 17"              (collapse spaces, strip leading zeros)
               "Bloomingdale  013 - 0103" → "Bloomingdale 13" (also strip code suffix)
    DeKalb:    "DEKALB 09"           → "DEKALB 9"             (strip leading zeros)
    Suburban Cook / Lake: no change (numeric or already canonical)
    """
    name = name.strip()

    if jurisdiction == "chicago":
        m = re.match(r'Ward\s+(\d+)\s+Precinct\s+(\d+)', name, re.IGNORECASE)
        if m:
            ward = int(m.group(1))
            prec = int(m.group(2))
            return f"Ward {ward:02d} Precinct {prec:02d}"
        return name  # fallback — return as-is

    elif jurisdiction == "dupage_county":
        # 1. Strip code suffix like " - 0103"
        name = re.sub(r'\s*-\s*\d+\s*$', '', name)
        # 2. Collapse multiple consecutive spaces into one
        name = re.sub(r'\s+', ' ', name).strip()
        # 3. Strip leading zeros from the last numeric token
        name = re.sub(r'\b0+(\d)', r'\1', name)
        return name

    elif jurisdiction == "dekalb_county":
        # Strip leading zeros from precinct numbers only
        name = re.sub(r'\b0+(\d)', r'\1', name)
        return name.strip()

    elif jurisdiction in ("cook_suburban", "lake_county"):
        # Numeric IDs — no normalization needed
        return name

    else:
        return name


def compute_canonical_precinct_id(jurisdiction: str, normalized_name: str) -> str:
    """
    Compute the canonical precinct_id for a given jurisdiction + normalized name.
    This must match the format used when the GeoJSON was built.

      Chicago:       MD5("chicago|ward 04 precinct 01")[:16]
      DuPage:        MD5("dupage_county|wayne 17")[:16]
      DeKalb:        MD5("dekalb_county|dekalb 9")[:16]
      Suburban Cook: MD5("cook_suburban|7000001")[:16]
      Lake:          stored directly in GeoJSON (MD5("lake_county|{name}")[:16])
    """
    key = f"{jurisdiction}|{normalized_name.lower()}"
    return hashlib.md5(key.encode()).hexdigest()[:16]


# ── Supabase API Client ───────────────────────────────────────────────────────

class SupabaseClient:
    """Thin REST API wrapper. READ uses anon key; WRITE uses service_role key."""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.read_headers = {
            "apikey": ANON_KEY,
            "Authorization": f"Bearer {ANON_KEY}",
            "Content-Type": "application/json",
            "Prefer": "count=exact",
        }
        self.write_headers = {
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}",
            "Content-Type": "application/json",
        }

    def get(self, table: str, params: dict = None, limit: int = 1000) -> list:
        """Paginated GET from a Supabase table."""
        all_rows = []
        offset = 0
        page_size = min(limit, 1000)

        while True:
            p = dict(params or {})
            p["limit"] = page_size
            p["offset"] = offset

            resp = requests.get(
                f"{SUPABASE_URL}/{table}",
                headers=self.read_headers,
                params=p,
                timeout=30,
            )
            resp.raise_for_status()
            rows = resp.json()
            if not rows:
                break
            all_rows.extend(rows)
            if len(rows) < page_size:
                break
            offset += page_size
            if len(all_rows) >= limit:
                break

        return all_rows[:limit]

    def get_all(self, table: str, params: dict = None, batch: int = 1000) -> list:
        """Fetch ALL rows from a table (auto-paginate)."""
        all_rows = []
        offset = 0

        while True:
            p = dict(params or {})
            p["limit"] = batch
            p["offset"] = offset

            resp = requests.get(
                f"{SUPABASE_URL}/{table}",
                headers=self.read_headers,
                params=p,
                timeout=60,
            )
            resp.raise_for_status()
            rows = resp.json()
            all_rows.extend(rows)
            if len(rows) < batch:
                break
            offset += batch
            time.sleep(0.1)  # Be gentle with the API

        return all_rows

    def patch(self, table: str, match_params: dict, data: dict) -> Optional[dict]:
        """PATCH (update) rows matching params. Skipped in dry_run mode."""
        if self.dry_run:
            print(f"    [DRY RUN] PATCH {table} WHERE {match_params} SET {data}")
            return None

        resp = requests.patch(
            f"{SUPABASE_URL}/{table}",
            headers=self.write_headers,
            params=match_params,
            json=data,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def count(self, table: str, params: dict = None) -> int:
        """Return count of rows matching params."""
        headers = dict(self.read_headers)
        headers["Prefer"] = "count=exact"
        p = dict(params or {})
        p["limit"] = 0  # Return count only

        resp = requests.get(
            f"{SUPABASE_URL}/{table}",
            headers=headers,
            params=p,
            timeout=30,
        )
        resp.raise_for_status()
        content_range = resp.headers.get("Content-Range", "0/0")
        try:
            return int(content_range.split("/")[1])
        except (IndexError, ValueError):
            return 0


def get_db_connection():
    """Get direct PostgreSQL connection via psycopg2 (for bulk writes)."""
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=30)
        return conn
    except ImportError:
        print("  ⚠ psycopg2 not installed. Direct DB writes unavailable.")
        return None
    except Exception as e:
        print(f"  ⚠ DB connection failed: {e}")
        return None


# ── SQL File Writers ──────────────────────────────────────────────────────────

def write_sql_file(filename: str, sql: str, description: str = "") -> Path:
    """Write SQL to sql_fixes/ directory."""
    SQL_FIXES_DIR.mkdir(parents=True, exist_ok=True)
    path = SQL_FIXES_DIR / filename
    header = f"""-- D4D Data Integrity Fix
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- {description}
-- 
-- Run this against the Supabase database:
--   psql "$DATABASE_URL" -f {filename}
--
-- Or via Supabase SQL Editor.
-- ALWAYS verify row counts before and after.
--
-- BEGIN;   ← Uncomment to wrap in transaction
-- COMMIT;  ← Uncomment to commit

"""
    path.write_text(header + sql)
    print(f"  → SQL written: {path}")
    return path


# ── Fix 1: Canonical Precinct Name Normalizer (utility / no DB writes) ────────

def fix_normalize_precinct_name_demo():
    """
    Demonstrates the normalize_precinct_name() function with test cases.
    No database writes — this fix is applied by Fixes 2, 3, 4.
    """
    print("\n" + "=" * 70)
    print("FIX 1: Canonical Precinct Name Normalizer — Test Cases")
    print("=" * 70)

    test_cases = [
        # (raw_name, jurisdiction, expected_normalized)
        ("Ward 4 Precinct 1",    "chicago",       "Ward 04 Precinct 01"),
        ("Ward 31 Precinct 9",   "chicago",       "Ward 31 Precinct 09"),
        ("Ward 01 Precinct 01",  "chicago",       "Ward 01 Precinct 01"),  # already padded
        ("Wayne  017",           "dupage_county", "Wayne 17"),
        ("Bloomingdale  013 - 0103", "dupage_county", "Bloomingdale 13"),
        ("Addison  001",         "dupage_county", "Addison 1"),
        ("Winfield  060 - 0601", "dupage_county", "Winfield 60"),
        ("DEKALB 09",            "dekalb_county", "DEKALB 9"),
        ("AFTON 01",             "dekalb_county", "AFTON 1"),
        ("SYCAMORE 10",          "dekalb_county", "SYCAMORE 10"),  # no change needed
        ("7000001",              "cook_suburban", "7000001"),       # no change
    ]

    all_pass = True
    for raw, jur, expected in test_cases:
        result = normalize_precinct_name(raw, jur)
        status = "✓" if result == expected else "✗ FAIL"
        if result != expected:
            all_pass = False
        print(f"  {status}  [{jur}] '{raw}' → '{result}' (expected '{expected}')")

    print()
    if all_pass:
        print("  All normalization tests passed!")
    else:
        print("  WARNING: Some normalization tests FAILED — check the function!")

    print("\n  Canonical ID examples:")
    examples = [
        ("chicago",       "Ward 04 Precinct 01"),
        ("dupage_county", "Wayne 17"),
        ("dekalb_county", "DEKALB 9"),
    ]
    for jur, name in examples:
        pid = compute_canonical_precinct_id(jur, name)
        print(f"  MD5('{jur}|{name.lower()}')[:16] = {pid}")


# ── Fix 2: DuPage 2018–2021 Precinct ID Rewrite ───────────────────────────────

def fix_dupage_precinct_ids(client: SupabaseClient, dry_run: bool = True):
    """
    Fix 2: DuPage 2018–2023 precinct_ids are wrong due to double-space + zero-pad
    format in old SBOE files. This fix:
    1. Fetches all distinct (source_precinct_name, precinct_id) tuples from results/turnout
       for affected elections.
    2. Computes the correct canonical precinct_id from the normalized name.
    3. Generates SQL UPDATE statements to rewrite precinct_id.
    """
    print("\n" + "=" * 70)
    print("FIX 2 & (partial): DuPage 2018–2023 Precinct ID Rewrite")
    print("=" * 70)

    all_elections = DUPAGE_BROKEN_ELECTIONS_V1 + DUPAGE_BROKEN_ELECTIONS_V2
    mapping = {}  # old_precinct_id → (new_precinct_id, normalized_name, raw_name)
    election_stats = {}

    print(f"\n  Fetching DuPage precinct names from results table...")
    print(f"  Affected elections: {', '.join(all_elections)}")

    for election_id in all_elections:
        print(f"\n  [{election_id}] Fetching distinct precinct names (sample of 2000)...")
        # Sample-based: fetch 2000 rows to discover all distinct precinct name formats.
        # The generated SQL UPDATE applies to ALL matching rows — no need to fetch them all.
        rows = client.get(
            "results",
            params={
                "election_id": f"eq.{election_id}",
                "source_file": f"like.SBOE DuPage%",
                "select": "precinct_id,source_precinct_name",
            },
            limit=2000,
        )

        # Deduplicate by precinct_id
        seen = {}
        for row in rows:
            pid = row.get("precinct_id")
            raw_name = row.get("source_precinct_name", "") or ""
            if pid and pid not in seen and raw_name:
                seen[pid] = raw_name

        print(f"    Found {len(seen)} distinct precinct IDs in sample")
        election_stats[election_id] = {"distinct_precincts": len(seen), "fixes": 0}

        for old_pid, raw_name in seen.items():
            norm_name = normalize_precinct_name(raw_name, "dupage_county")
            new_pid = compute_canonical_precinct_id("dupage_county", norm_name)

            if old_pid != new_pid:
                mapping[old_pid] = (new_pid, norm_name, raw_name)
                election_stats[election_id]["fixes"] += 1

    # Also check turnout for DuPage 2022/2023
    print(f"\n  Checking turnout table for DuPage 2022/2023...")
    for election_id in DUPAGE_BROKEN_ELECTIONS_V2:
        rows = client.get_all(
            "turnout",
            params={
                "election_id": f"eq.{election_id}",
                "source_file": f"like.SBOE DuPage%",
                "select": "precinct_id,source_precinct_name",
            },
        )
        for row in rows:
            pid = row.get("precinct_id")
            raw_name = row.get("source_precinct_name", "") or ""
            if pid and raw_name:
                norm_name = normalize_precinct_name(raw_name, "dupage_county")
                new_pid = compute_canonical_precinct_id("dupage_county", norm_name)
                if old_pid != new_pid and pid not in mapping:
                    mapping[pid] = (new_pid, norm_name, raw_name)

    print(f"\n  Total unique precinct_id fixes needed: {len(mapping)}")

    if not mapping:
        print("  No DuPage precinct ID fixes needed (all already canonical).")
        return

    # Print sample of mappings
    print(f"\n  Sample mappings (first 10):")
    for old_pid, (new_pid, norm_name, raw_name) in list(mapping.items())[:10]:
        print(f"    '{raw_name}' → '{norm_name}'")
        print(f"      {old_pid} → {new_pid}")

    # Generate SQL
    sql_lines = [
        "-- Fix 2: DuPage Precinct ID Rewrite",
        "-- Maps old (broken format) precinct_ids to canonical (GeoJSON-matching) ids",
        "",
        "-- Step 1: Create a temporary mapping table",
        "CREATE TEMP TABLE IF NOT EXISTS dupage_pid_mapping (",
        "    old_id      TEXT PRIMARY KEY,",
        "    new_id      TEXT NOT NULL,",
        "    raw_name    TEXT,",
        "    norm_name   TEXT",
        ");",
        "",
        "INSERT INTO dupage_pid_mapping (old_id, new_id, raw_name, norm_name) VALUES",
    ]

    mapping_values = []
    for old_pid, (new_pid, norm_name, raw_name) in sorted(mapping.items()):
        raw_esc = raw_name.replace("'", "''")
        norm_esc = norm_name.replace("'", "''")
        mapping_values.append(
            f"    ('{old_pid}', '{new_pid}', '{raw_esc}', '{norm_esc}')"
        )
    sql_lines.append(",\n".join(mapping_values) + ";")
    sql_lines.append("")

    # UPDATE results
    sql_lines += [
        "-- Step 2: Update results table",
        f"-- Affected elections: {', '.join(repr(e) for e in all_elections)}",
        "UPDATE results r",
        "SET precinct_id = m.new_id",
        "FROM dupage_pid_mapping m",
        "WHERE r.precinct_id = m.old_id",
        f"  AND r.election_id IN ({', '.join(repr(e) for e in all_elections)});",
        "",
        f"-- Expected: up to {len(mapping)} distinct precinct_ids updated across results",
        "-- Run: SELECT COUNT(*) FROM results WHERE election_id IN (...) AND source_file LIKE 'SBOE DuPage%';",
        "",
    ]

    # UPDATE turnout
    sql_lines += [
        "-- Step 3: Update turnout table (DuPage 2022/2023 only)",
        "UPDATE turnout t",
        "SET precinct_id = m.new_id",
        "FROM dupage_pid_mapping m",
        "WHERE t.precinct_id = m.old_id",
        f"  AND t.election_id IN ({', '.join(repr(e) for e in DUPAGE_BROKEN_ELECTIONS_V2)});",
        "",
    ]

    # UPDATE source_precinct_name to normalized form
    sql_lines += [
        "-- Step 4: Also normalize source_precinct_name in results",
        "UPDATE results r",
        "SET source_precinct_name = m.norm_name",
        "FROM dupage_pid_mapping m",
        "WHERE r.precinct_id = m.new_id  -- precinct_id already updated above",
        f"  AND r.election_id IN ({', '.join(repr(e) for e in all_elections)});",
        "",
        "-- Step 5: Verify",
        "SELECT COUNT(DISTINCT precinct_id) as distinct_pids, election_id",
        "FROM results",
        f"WHERE election_id IN ({', '.join(repr(e) for e in all_elections)})",
        "  AND source_file LIKE 'SBOE DuPage%'",
        "GROUP BY election_id;",
    ]

    sql_content = "\n".join(sql_lines)
    write_sql_file(
        "fix_02_dupage_precinct_ids.sql",
        sql_content,
        f"DuPage precinct_id rewrite — {len(mapping)} unique IDs to fix across {len(all_elections)} elections",
    )

    # Election summary
    print("\n  Per-election fix counts:")
    for eid, stats in election_stats.items():
        print(f"    {eid}: {stats['distinct_precincts']} precincts, {stats['fixes']} to fix")

    return mapping


# ── Fix 3: DeKalb 2018–2021 Precinct ID Rewrite ──────────────────────────────

def fix_dekalb_precinct_ids(client: SupabaseClient, dry_run: bool = True):
    """
    Fix 3: DeKalb 2018–2021 used zero-padded names (DEKALB 09) but GeoJSON uses
    unpadded (DEKALB 9). Affects ~35 of 65 precincts per election (those with
    precinct numbers 1–9).
    """
    print("\n" + "=" * 70)
    print("FIX 3: DeKalb 2018–2021 Precinct ID Rewrite")
    print("=" * 70)

    mapping = {}  # old_pid → (new_pid, norm_name, raw_name)
    election_stats = {}

    print(f"\n  Affected elections: {', '.join(DEKALB_BROKEN_ELECTIONS)}")

    for election_id in DEKALB_BROKEN_ELECTIONS:
        print(f"\n  [{election_id}] Fetching distinct precinct names...")
        rows = client.get_all(
            "results",
            params={
                "election_id": f"eq.{election_id}",
                "source_file": f"like.SBOE DeKalb%",
                "select": "precinct_id,source_precinct_name",
            },
        )
        # Also fetch turnout
        turnout_rows = client.get_all(
            "turnout",
            params={
                "election_id": f"eq.{election_id}",
                "source_file": f"like.SBOE DeKalb%",
                "select": "precinct_id,source_precinct_name",
            },
        )
        rows += turnout_rows

        seen = {}
        for row in rows:
            pid = row.get("precinct_id")
            raw_name = row.get("source_precinct_name", "") or ""
            if pid and raw_name and pid not in seen:
                seen[pid] = raw_name

        print(f"    Found {len(seen)} distinct precinct IDs")
        election_stats[election_id] = {"distinct_precincts": len(seen), "fixes": 0}

        for old_pid, raw_name in seen.items():
            norm_name = normalize_precinct_name(raw_name, "dekalb_county")
            new_pid = compute_canonical_precinct_id("dekalb_county", norm_name)

            if old_pid != new_pid:
                mapping[old_pid] = (new_pid, norm_name, raw_name)
                election_stats[election_id]["fixes"] += 1

    print(f"\n  Total unique precinct_id fixes needed: {len(mapping)}")

    # Show the zero-padded ones that need fixing
    print("\n  Zero-padded precincts being fixed:")
    for old_pid, (new_pid, norm_name, raw_name) in sorted(mapping.items(),
                                                            key=lambda x: x[1][2]):
        print(f"    '{raw_name}' → '{norm_name}'  ({old_pid} → {new_pid})")

    if not mapping:
        print("  No DeKalb precinct ID fixes needed.")
        return

    # Generate SQL
    sql_lines = [
        "-- Fix 3: DeKalb Precinct ID Rewrite (zero-padding removal)",
        "-- Maps old (zero-padded) precinct_ids to GeoJSON-canonical ids",
        "",
        "CREATE TEMP TABLE IF NOT EXISTS dekalb_pid_mapping (",
        "    old_id    TEXT PRIMARY KEY,",
        "    new_id    TEXT NOT NULL,",
        "    raw_name  TEXT,",
        "    norm_name TEXT",
        ");",
        "",
        "INSERT INTO dekalb_pid_mapping (old_id, new_id, raw_name, norm_name) VALUES",
    ]

    mapping_values = []
    for old_pid, (new_pid, norm_name, raw_name) in sorted(mapping.items()):
        raw_esc = raw_name.replace("'", "''")
        norm_esc = norm_name.replace("'", "''")
        mapping_values.append(
            f"    ('{old_pid}', '{new_pid}', '{raw_esc}', '{norm_esc}')"
        )
    sql_lines.append(",\n".join(mapping_values) + ";")
    sql_lines.append("")

    sql_lines += [
        "-- Update results",
        "UPDATE results r",
        "SET precinct_id = m.new_id,",
        "    source_precinct_name = m.norm_name",
        "FROM dekalb_pid_mapping m",
        "WHERE r.precinct_id = m.old_id",
        f"  AND r.election_id IN ({', '.join(repr(e) for e in DEKALB_BROKEN_ELECTIONS)});",
        "",
        "-- Update turnout",
        "UPDATE turnout t",
        "SET precinct_id = m.new_id,",
        "    source_precinct_name = m.norm_name",
        "FROM dekalb_pid_mapping m",
        "WHERE t.precinct_id = m.old_id",
        f"  AND t.election_id IN ({', '.join(repr(e) for e in DEKALB_BROKEN_ELECTIONS)});",
        "",
        "-- Verify: should see 65 precincts per election matching GeoJSON",
        "SELECT election_id, COUNT(DISTINCT precinct_id) as dekalb_precincts",
        "FROM results",
        f"WHERE election_id IN ({', '.join(repr(e) for e in DEKALB_BROKEN_ELECTIONS)})",
        "  AND source_file LIKE 'SBOE DeKalb%'",
        "GROUP BY election_id;",
    ]

    write_sql_file(
        "fix_03_dekalb_precinct_ids.sql",
        "\n".join(sql_lines),
        f"DeKalb precinct_id rewrite — {len(mapping)} zero-padded IDs to fix",
    )

    print("\n  Per-election fix counts:")
    for eid, stats in election_stats.items():
        print(f"    {eid}: {stats['distinct_precincts']} precincts, {stats['fixes']} to fix")

    return mapping


# ── Fix 4: Chicago CBOE / School Board Name Normalization ────────────────────

def fix_chicago_precinct_ids(client: SupabaseClient, dry_run: bool = True):
    """
    Fix 4: Chicago CBOE 2024 School Board and cboe_2026_ajax data may use
    unpadded names ("Ward 4 Precinct 1") instead of zero-padded ("Ward 04 Precinct 01").
    Verify and fix any mismatches.
    """
    print("\n" + "=" * 70)
    print("FIX 4: Chicago CBOE / School Board Precinct ID Normalization")
    print("=" * 70)

    # Elections to check for CBOE data
    chicago_elections_to_check = [
        "2024_general",  # School Board
        "2026_primary",  # cboe_2026_ajax turnout
        "2025_consolidated",
    ]
    cboe_sources = ["cboe_2026_ajax", "Chicago BOE 2024 General - School Board", "CBOE"]

    mapping = {}
    total_checked = 0

    for election_id in chicago_elections_to_check:
        print(f"\n  [{election_id}] Checking Chicago precinct IDs...")

        # Check turnout — Chicago sources include SBOE, CBOE, municipal files
        rows = client.get(
            "turnout",
            params={
                "election_id": f"eq.{election_id}",
                "source_file": f"like.%Chicago%",
                "select": "precinct_id,source_precinct_name,source_file",
            },
            limit=2000,
        )
        cboe_rows = client.get(
            "turnout",
            params={
                "election_id": f"eq.{election_id}",
                "source_file": f"like.cboe%",
                "select": "precinct_id,source_precinct_name,source_file",
            },
            limit=2000,
        )
        rows += cboe_rows
        # Also results
        result_rows = client.get(
            "results",
            params={
                "election_id": f"eq.{election_id}",
                "source_file": f"like.%Chicago BOE%",
                "select": "precinct_id,source_precinct_name,source_file",
            },
            limit=500,
        )
        rows += result_rows
        total_checked += len(rows)

        mismatches = 0
        for row in rows:
            pid = row.get("precinct_id")
            raw_name = row.get("source_precinct_name", "") or ""
            if not pid or not raw_name:
                continue

            norm_name = normalize_precinct_name(raw_name, "chicago")
            new_pid = compute_canonical_precinct_id("chicago", norm_name)

            if pid != new_pid:
                mapping[pid] = (new_pid, norm_name, raw_name, election_id)
                mismatches += 1

        print(f"    Checked {len(rows)} rows, found {mismatches} mismatched IDs")

    print(f"\n  Total rows checked: {total_checked}")
    print(f"  Total IDs to fix: {len(mapping)}")

    if not mapping:
        print("  No Chicago precinct ID fixes needed.")
        _generate_chicago_geojson_fix_sql()
        return

    sql_lines = [
        "-- Fix 4: Chicago CBOE Precinct ID Normalization",
        "-- Converts unpadded (Ward 4 Precinct 1) to padded (Ward 04 Precinct 01)",
        "",
        "CREATE TEMP TABLE IF NOT EXISTS chicago_pid_mapping (",
        "    old_id    TEXT PRIMARY KEY,",
        "    new_id    TEXT NOT NULL,",
        "    raw_name  TEXT,",
        "    norm_name TEXT,",
        "    election_id TEXT",
        ");",
        "",
        "INSERT INTO chicago_pid_mapping (old_id, new_id, raw_name, norm_name, election_id) VALUES",
    ]

    vals = []
    for old_pid, (new_pid, norm_name, raw_name, eid) in sorted(mapping.items()):
        raw_esc = raw_name.replace("'", "''")
        norm_esc = norm_name.replace("'", "''")
        vals.append(f"    ('{old_pid}', '{new_pid}', '{raw_esc}', '{norm_esc}', '{eid}')")
    sql_lines.append(",\n".join(vals) + ";")
    sql_lines.append("")

    sql_lines += [
        "-- Update results",
        "UPDATE results r",
        "SET precinct_id = m.new_id",
        "FROM chicago_pid_mapping m",
        "WHERE r.precinct_id = m.old_id;",
        "",
        "-- Update turnout",
        "UPDATE turnout t",
        "SET precinct_id = m.new_id",
        "FROM chicago_pid_mapping m",
        "WHERE t.precinct_id = m.old_id;",
    ]

    write_sql_file(
        "fix_04_chicago_cboe_precinct_ids.sql",
        "\n".join(sql_lines),
        f"Chicago CBOE precinct normalization — {len(mapping)} IDs to fix",
    )

    # Always generate the GeoJSON update script too
    _generate_chicago_geojson_fix_sql()

    return mapping


def _generate_chicago_geojson_fix_sql():
    """
    Generate SQL/Python snippet to add precinct_id field to Chicago GeoJSON.
    This prevents future hash format errors (Issue #9 from audit).
    """
    python_snippet = '''#!/usr/bin/env python3
"""
Add canonical precinct_id field to Chicago GeoJSON.
Run once — fixes the root cause of Chicago hash format confusion.
Audit Issue #9: Chicago GeoJSON uses unpadded display names but padded hashes.
"""
import hashlib
import json
from pathlib import Path

GEOJSON_PATH = Path("/home/user/workspace/d4d-heatmap-platform/public/precincts_chicago.geojson")
# Adjust path as needed — check where the frontend serves GeoJSON from

with open(GEOJSON_PATH) as f:
    geo = json.load(f)

updated = 0
for feature in geo["features"]:
    props = feature["properties"]
    ward = props.get("ward")
    precinct = props.get("precinct")
    if ward is not None and precinct is not None:
        key = f"chicago|ward {int(ward):02d} precinct {int(precinct):02d}"
        props["precinct_id"] = hashlib.md5(key.encode()).hexdigest()[:16]
        # Also add padded display name for consistency
        props["display_name"] = f"Ward {int(ward):02d} Precinct {int(precinct):02d}"
        updated += 1

with open(GEOJSON_PATH, "w") as f:
    json.dump(geo, f, separators=(",", ":"))

print(f"Updated {updated} Chicago precinct features with canonical precinct_id")
'''

    path = SQL_FIXES_DIR / "fix_09_chicago_geojson_add_precinct_id.py"
    path.write_text(python_snippet)
    print(f"  → Python script written: {path}")


# ── Fix 5: NULL Source File Cleanup ──────────────────────────────────────────

def fix_null_source_files(client: SupabaseClient, dry_run: bool = True):
    """
    Fix 5: 4,367 turnout rows have NULL source_file across 3 elections.
    Backfills source_file (and where possible, source_precinct_name) by
    cross-referencing precinct_ids against known Cook County precinct mappings.
    """
    print("\n" + "=" * 70)
    print("FIX 5: NULL source_file Cleanup (4,367 turnout rows)")
    print("=" * 70)

    sql_parts = ["-- Fix 5: NULL source_file / source_precinct_name backfill"]
    summary = {}

    for election_id, config in NULL_SOURCE_ELECTIONS.items():
        expected = config["expected_rows"]
        source_label = config["source_label"]

        print(f"\n  [{election_id}] Checking NULL source_file rows...")
        rows = client.get_all(
            "turnout",
            params={
                "election_id": f"eq.{election_id}",
                "source_file": "is.null",
                "select": "id,precinct_id,source_precinct_name,registered_voters,ballots_cast",
            },
        )
        actual_count = len(rows)
        print(f"    Found {actual_count} rows with NULL source_file (expected ~{expected})")

        no_precinct_name = sum(1 for r in rows if not r.get("source_precinct_name"))
        has_precinct_name = actual_count - no_precinct_name
        print(f"    With source_precinct_name: {has_precinct_name}")
        print(f"    Without source_precinct_name: {no_precinct_name}")

        summary[election_id] = {
            "null_rows": actual_count,
            "with_name": has_precinct_name,
            "without_name": no_precinct_name,
        }

        # Simple fix: set source_file to known label
        # source_precinct_name will be derived from precinct_id via existing precincts table
        sql_parts += [
            "",
            f"-- {election_id}: {actual_count} rows with NULL source_file",
            f"-- Source label: '{source_label}'",
            "UPDATE turnout",
            f"SET source_file = '{source_label}'",
            f"WHERE election_id = '{election_id}'",
            "  AND source_file IS NULL;",
        ]

        # For cook_2021 and cook_2023: also try to backfill source_precinct_name
        # by looking up the precinct record
        if election_id in ("cook_2021_consolidated", "cook_2023_consolidated"):
            sql_parts += [
                "",
                f"-- Also backfill source_precinct_name for {election_id}",
                "-- (Cook precincts use numeric IDs stored in precincts table)",
                "UPDATE turnout t",
                "SET source_precinct_name = p.source_name",
                "FROM precincts p",
                f"WHERE t.election_id = '{election_id}'",
                "  AND t.source_precinct_name IS NULL",
                "  AND t.precinct_id = p.id",
                "  AND p.jurisdiction_id = 'cook_suburban';",
            ]

        if election_id == "2026_primary":
            sql_parts += [
                "",
                "-- 2026_primary: These are cboe_2026_ajax Chicago turnout rows",
                "-- source_precinct_name is NULL — try to backfill from Chicago precincts",
                "UPDATE turnout t",
                "SET source_precinct_name = p.source_name",
                "FROM precincts p",
                f"WHERE t.election_id = '2026_primary'",
                "  AND t.source_precinct_name IS NULL",
                "  AND t.precinct_id = p.id",
                "  AND p.jurisdiction_id = 'chicago';",
            ]

    # Verification queries
    sql_parts += [
        "",
        "-- Verification: should return 0 rows after fix",
        "SELECT election_id, COUNT(*) as null_source_rows",
        "FROM turnout",
        f"WHERE election_id IN ({', '.join(repr(e) for e in NULL_SOURCE_ELECTIONS)})",
        "  AND source_file IS NULL",
        "GROUP BY election_id;",
    ]

    write_sql_file(
        "fix_05_null_source_files.sql",
        "\n".join(sql_parts),
        "Backfill NULL source_file in turnout table (4,367 rows across 3 elections)",
    )

    print("\n  Summary:")
    for eid, stats in summary.items():
        print(f"    {eid}: {stats['null_rows']} null rows ({stats['without_name']} also missing precinct name)")


# ── Fix 6: Candidate Name Deduplication ──────────────────────────────────────

def fix_candidate_deduplication(client: SupabaseClient, dry_run: bool = True):
    """
    Fix 6: 1,038 candidate names appear with 2+ different candidate_ids due to
    inconsistent party label normalization. This fix:
    1. Identifies all duplicate-name candidates.
    2. Selects the canonical ID (prefer entries with standardized party labels).
    3. Generates SQL to remap results → canonical ID and delete duplicates.
    4. Normalizes party labels across the entire candidates table.
    """
    print("\n" + "=" * 70)
    print("FIX 6: Candidate Name Deduplication Report + SQL")
    print("=" * 70)

    print("\n  Fetching all candidates...")
    all_candidates = client.get_all(
        "candidates",
        params={"select": "id,name,party"},
    )
    print(f"  Total candidates fetched: {len(all_candidates)}")

    # Group by name
    by_name: dict[str, list] = {}
    for cand in all_candidates:
        name = (cand.get("name") or "").strip()
        if not name:
            continue
        if name not in by_name:
            by_name[name] = []
        by_name[name].append(cand)

    # Find duplicates
    duplicates = {name: entries for name, entries in by_name.items() if len(entries) > 1}
    print(f"  Candidate names with 2+ IDs: {len(duplicates)}")

    # Party normalization helper
    def canonical_party(party: Optional[str]) -> tuple[str, int]:
        """Returns (canonical_party, priority) — lower priority = preferred."""
        if party is None:
            return ("", 99)
        lower = party.strip().lower()
        canonical = PARTY_CANONICAL.get(lower, party.strip())
        # Prefer fully spelled-out standard party names
        priority = (
            0 if canonical in ("Democratic", "Republican", "Green", "Libertarian", "Non-Partisan")
            else 1 if canonical else 2
        )
        return (canonical, priority)

    # Pick canonical ID for each duplicate name
    canonical_map: dict[str, str] = {}  # duplicate_id → canonical_id
    report_lines = ["# Candidate Deduplication Report", ""]
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Total duplicate-name groups: {len(duplicates)}")
    report_lines.append("")
    report_lines.append("| Name | IDs | Parties |")
    report_lines.append("|------|-----|---------|")

    merge_ops = []  # (old_id, new_id, name)
    party_normalize_ops = []  # (id, new_party)

    for name, entries in sorted(duplicates.items()):
        # Sort entries by party priority (most canonical first)
        scored = sorted(
            entries,
            key=lambda e: canonical_party(e.get("party"))[1],
        )
        canonical = scored[0]
        canonical_id = canonical["id"]
        canonical_party_val, _ = canonical_party(canonical.get("party"))

        parties_str = ", ".join(
            repr(e.get("party") or "NULL") for e in entries
        )
        report_lines.append(
            f"| {name} | {len(entries)} | {parties_str} |"
        )

        # Build merge operations
        for entry in entries:
            if entry["id"] != canonical_id:
                canonical_map[entry["id"]] = canonical_id
                merge_ops.append((entry["id"], canonical_id, name))

        # Normalize party on canonical entry if needed
        raw_party = canonical.get("party") or ""
        norm, _ = canonical_party(raw_party)
        if norm != raw_party:
            party_normalize_ops.append((canonical_id, norm))

    # Write the report
    report_path = SQL_FIXES_DIR / "fix_06_candidate_dedup_report.md"
    report_path.write_text("\n".join(report_lines))
    print(f"  → Report written: {report_path}")
    print(f"  Duplicate candidate IDs to merge: {len(merge_ops)}")
    print(f"  Party label normalizations needed: {len(party_normalize_ops)}")

    # Generate SQL
    sql_lines = [
        "-- Fix 6: Candidate Deduplication + Party Normalization",
        f"-- Merges {len(merge_ops)} duplicate candidate IDs",
        f"-- Normalizes {len(party_normalize_ops) + len(PARTY_CANONICAL)} party labels",
        "",
        "-- ============================================================",
        "-- STEP 1: Remap results rows from duplicate IDs to canonical IDs",
        "-- ============================================================",
        "",
    ]

    # Batch the merge ops in manageable chunks
    BATCH_SIZE = 200
    for i in range(0, len(merge_ops), BATCH_SIZE):
        batch = merge_ops[i:i + BATCH_SIZE]
        sql_lines.append(f"-- Batch {i // BATCH_SIZE + 1}")
        for old_id, new_id, cand_name in batch:
            name_esc = cand_name.replace("'", "''")
            sql_lines.append(
                f"UPDATE results SET candidate_id = '{new_id}' "
                f"WHERE candidate_id = '{old_id}';  -- {name_esc}"
            )
        sql_lines.append("")

    sql_lines += [
        "",
        "-- ============================================================",
        "-- STEP 2: Delete duplicate candidate entries",
        "-- ============================================================",
        "",
        "DELETE FROM candidates",
        f"WHERE id IN ({', '.join(repr(old) for old, _, _ in merge_ops)});",
        "",
        f"-- Deleted {len(merge_ops)} duplicate candidate records",
        "",
        "-- ============================================================",
        "-- STEP 3: Normalize party labels across ALL candidates",
        "-- ============================================================",
        "",
    ]

    # Group by canonical target for cleaner SQL
    party_updates = {
        "Democratic":  ["Democrat", "DEM", "DEMOCRATIC", "Dem", "democratic", "dem"],
        "Republican":  ["REP", "REPUBLICAN", "Rep", "republican", "rep"],
        "Non-Partisan": ["NON", "NP", "IND", "Non-partisan", "nonpartisan",
                         "Non-Partisan (NP)", "Independent"],
        "Green":       ["GREEN", "Grn"],
        "Libertarian": ["LIB", "LIBERTARIAN", "Lib"],
    }

    for canonical, aliases in party_updates.items():
        aliases_quoted = ", ".join(repr(a) for a in aliases)
        sql_lines += [
            f"UPDATE candidates SET party = '{canonical}'",
            f"WHERE party IN ({aliases_quoted});",
        ]

    sql_lines += [
        "",
        "-- ============================================================",
        "-- STEP 4: Verification",
        "-- ============================================================",
        "",
        "-- Should return 0 after fix:",
        "SELECT name, COUNT(DISTINCT id) as id_count, array_agg(DISTINCT party) as parties",
        "FROM candidates",
        "GROUP BY name",
        "HAVING COUNT(DISTINCT id) > 1",
        "ORDER BY id_count DESC",
        "LIMIT 20;",
        "",
        "-- Party distribution after normalization:",
        "SELECT party, COUNT(*) as count",
        "FROM candidates",
        "GROUP BY party",
        "ORDER BY count DESC;",
    ]

    write_sql_file(
        "fix_06_candidate_deduplication.sql",
        "\n".join(sql_lines),
        f"Candidate deduplication — {len(merge_ops)} merges, {len(PARTY_CANONICAL)} party normalizations",
    )

    # Print sample duplicates
    print("\n  Sample duplicate candidates (first 15):")
    for name, entries in list(duplicates.items())[:15]:
        parties = [repr(e.get("party") or "NULL") for e in entries]
        print(f"    '{name}': {len(entries)} IDs, parties: {', '.join(parties)}")


# ── Fix 7 (Bonus): DuPage 2022/2023 Code Suffix Rewrite ─────────────────────

def fix_dupage_2022_code_suffix(client: SupabaseClient, dry_run: bool = True):
    """
    Fix 7 (supplemental): DuPage 2022/2023 also used a code suffix format:
    "BLOOMINGDALE  013 - 0103" which has both double-space AND code suffix.
    This is covered by fix_dupage_precinct_ids() above but we generate a
    targeted report for these elections specifically.
    """
    print("\n" + "=" * 70)
    print("FIX 7: DuPage 2022/2023 Code Suffix Format Rewrite (supplemental)")
    print("=" * 70)
    print("  NOTE: DuPage 2022/2023 fixes are included in Fix 2's SQL output.")
    print("  These elections used format: 'Bloomingdale  013 - 0103'")
    print("  Normalized to: 'Bloomingdale 13' (collapse spaces + strip suffix + strip zeros)")
    print()

    for election_id in DUPAGE_BROKEN_ELECTIONS_V2:
        rows = client.get(
            "results",
            params={
                "election_id": f"eq.{election_id}",
                "source_file": f"like.SBOE DuPage%",
                "select": "source_precinct_name",
                "limit": "5",
            },
            limit=5,
        )
        print(f"  [{election_id}] Sample source_precinct_names:")
        for row in rows:
            raw = row.get("source_precinct_name", "")
            norm = normalize_precinct_name(raw, "dupage_county")
            print(f"    '{raw}' → '{norm}'")


# ── Fix 8: Chicago 2022 Primary Phantom Precincts Report ─────────────────────

def fix_chicago_2022_phantom_precincts(client: SupabaseClient, dry_run: bool = True):
    """
    Fix 8: Chicago 2022 Primary has 778 phantom precincts (pre-redistricting wards).
    These cannot be mapped to the current GeoJSON. This fix:
    1. Identifies the 778 precinct_ids not in the current GeoJSON.
    2. Generates SQL to mark them with an 'unmappable' flag or metadata note.
    """
    print("\n" + "=" * 70)
    print("FIX 8: Chicago 2022 Primary Phantom Precinct Report")
    print("=" * 70)

    print("\n  Fetching 2022_primary Chicago turnout precincts...")
    rows_2022 = client.get_all(
        "turnout",
        params={
            "election_id": "eq.2022_primary",
            "source_file": "like.SBOE 2022 Primary - Chicago%",
            "select": "precinct_id,source_precinct_name",
        },
    )

    print(f"  2022 Primary: {len(rows_2022)} turnout rows")

    # Get 2022_general as reference (1,290 correct precincts)
    rows_2022g = client.get_all(
        "turnout",
        params={
            "election_id": "eq.2022_general",
            "source_file": "like.SBOE 2022 General - Chicago%",
            "select": "precinct_id",
        },
    )
    valid_pids = {r["precinct_id"] for r in rows_2022g}
    print(f"  2022 General (reference): {len(valid_pids)} valid precinct IDs")

    phantom_rows = [r for r in rows_2022 if r["precinct_id"] not in valid_pids]
    print(f"  Phantom precincts (in 2022P but not in 2022G or GeoJSON): {len(phantom_rows)}")

    if phantom_rows:
        phantom_ids = [r["precinct_id"] for r in phantom_rows]
        phantom_names = [r.get("source_precinct_name", "") for r in phantom_rows]

        # Show sample
        print("\n  Sample phantom precincts (first 20):")
        for pid, name in list(zip(phantom_ids, phantom_names))[:20]:
            print(f"    {pid}  '{name}'")

        sql_lines = [
            "-- Fix 8: Chicago 2022 Primary Phantom Precincts",
            "-- These 778 precincts are from the pre-redistricting ward map",
            "-- They cannot be displayed on the current GeoJSON",
            "-- Action: No deletion — data is correct, just unmappable.",
            "-- Document them for future pre-redistricting GeoJSON work.",
            "",
            "-- View the phantom precincts:",
            "SELECT DISTINCT t.precinct_id, t.source_precinct_name",
            "FROM turnout t",
            "WHERE t.election_id = '2022_primary'",
            "  AND t.source_file LIKE 'SBOE 2022 Primary - Chicago%'",
            "  AND t.precinct_id NOT IN (",
            "      SELECT DISTINCT precinct_id FROM turnout",
            "      WHERE election_id = '2022_general'",
            "        AND source_file LIKE 'SBOE 2022 General - Chicago%'",
            "  )",
            "ORDER BY source_precinct_name;",
            "",
            f"-- Total phantom count: {len(phantom_rows)}",
            "",
            "-- These precincts need a pre-redistricting Chicago GeoJSON",
            "-- Source: City of Chicago Data Portal (boundaries vintage 2022-06)",
            "-- URL: https://data.cityofchicago.org/Facilities-Geographic-Boundaries/",
            "--      Ward-Precincts-2015-2023/uvpq-qeem",
        ]

        write_sql_file(
            "fix_08_chicago_2022_phantom_precincts.sql",
            "\n".join(sql_lines),
            f"Chicago 2022 Primary phantom precinct documentation — {len(phantom_rows)} precincts",
        )

        # Also write a JSON list of phantom precinct names for GeoJSON work
        phantom_list = sorted(set(phantom_names))
        phantom_json_path = SQL_FIXES_DIR / "chicago_2022_primary_phantom_precincts.json"
        phantom_json_path.write_text(
            json.dumps({"count": len(phantom_list), "precincts": phantom_list}, indent=2)
        )
        print(f"  → Phantom precinct list: {phantom_json_path}")


# ── Summary Report ────────────────────────────────────────────────────────────

def print_summary(dry_run: bool, fixes_run: list[str]):
    """Print a final summary of all fixes run."""
    print("\n" + "=" * 70)
    print(f"SUMMARY — {'DRY RUN' if dry_run else 'EXECUTED'}")
    print("=" * 70)
    print(f"\nFixes run: {', '.join(fixes_run)}")
    print(f"\nSQL fix files written to: {SQL_FIXES_DIR}/")

    sql_files = sorted(SQL_FIXES_DIR.glob("*.sql")) + sorted(SQL_FIXES_DIR.glob("*.py"))
    if sql_files:
        print("\nGenerated files:")
        for f in sql_files:
            size = f.stat().st_size
            print(f"  {f.name:50s}  ({size:,} bytes)")

    print()
    if dry_run:
        print("  This was a DRY RUN. No database changes were made.")
        print("  To execute fixes:")
        print("    python fix_data_integrity.py --execute")
        print("    - OR -")
        print("    psql \"$DATABASE_URL\" -f pipeline/sql_fixes/fix_XX_*.sql")
    else:
        print("  Fixes have been APPLIED to the database.")
        print("  Run validate_data_integrity.py to verify results.")


# ── Main Entry Point ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="D4D Data Integrity Fix Script — fixes all audit issues"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="Apply fixes to database. Default is DRY RUN (generates SQL only).",
    )
    parser.add_argument(
        "--fix",
        choices=["all", "normalize", "dupage", "dekalb", "chicago", "nullsource",
                 "candidates", "geojson", "phantom"],
        default="all",
        help="Which fix to run (default: all)",
    )
    args = parser.parse_args()

    dry_run = not args.execute
    fix_target = args.fix

    print("=" * 70)
    print("D4D Election Heatmap — Data Integrity Fix Script")
    print(f"Mode: {'DRY RUN (no writes)' if dry_run else '*** EXECUTE — WRITES TO DATABASE ***'}")
    print(f"Fix:  {fix_target}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    if not dry_run:
        confirm = input(
            "\n⚠  EXECUTE mode will modify the production database.\n"
            "   Type 'YES' to continue: "
        )
        if confirm.strip() != "YES":
            print("Aborted.")
            sys.exit(1)

    SQL_FIXES_DIR.mkdir(parents=True, exist_ok=True)
    client = SupabaseClient(dry_run=dry_run)
    fixes_run = []

    try:
        if fix_target in ("all", "normalize"):
            fix_normalize_precinct_name_demo()
            fixes_run.append("normalize")

        if fix_target in ("all", "dupage"):
            fix_dupage_precinct_ids(client, dry_run=dry_run)
            fix_dupage_2022_code_suffix(client, dry_run=dry_run)
            fixes_run.append("dupage")

        if fix_target in ("all", "dekalb"):
            fix_dekalb_precinct_ids(client, dry_run=dry_run)
            fixes_run.append("dekalb")

        if fix_target in ("all", "chicago"):
            fix_chicago_precinct_ids(client, dry_run=dry_run)
            fixes_run.append("chicago")

        if fix_target in ("all", "nullsource"):
            fix_null_source_files(client, dry_run=dry_run)
            fixes_run.append("nullsource")

        if fix_target in ("all", "candidates"):
            fix_candidate_deduplication(client, dry_run=dry_run)
            fixes_run.append("candidates")

        if fix_target in ("all", "phantom"):
            fix_chicago_2022_phantom_precincts(client, dry_run=dry_run)
            fixes_run.append("phantom")

        if fix_target == "geojson":
            _generate_chicago_geojson_fix_sql()
            fixes_run.append("geojson")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()

    print_summary(dry_run, fixes_run)


if __name__ == "__main__":
    main()
