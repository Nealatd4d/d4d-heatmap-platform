#!/usr/bin/env python3
"""
D4D Map Coverage Test
=====================
Tests EVERY race across ALL elections to verify:
1. get_race_map(race_id) returns data
2. Precinct IDs in results match GeoJSON features (via MD5 hashing)
3. No race has zero precincts
4. Coverage meets expected thresholds by district type

The GeoJSON files don't store precinct_id hashes directly — they store
ward+precinct (Chicago) or precinctid (suburban). This test computes
the MD5 hashes the same way the frontend and loaders do.

Usage:
    python test_map_coverage.py                  # Full test
    python test_map_coverage.py --election 2026  # Filter by election year
    python test_map_coverage.py --summary        # Summary only
"""

import json
import sys
import os
import hashlib
import urllib.request
import urllib.error
from collections import defaultdict
from datetime import datetime, timezone

# ─── Configuration ───
SUPA_URL = "https://nfjfqdffulhqhszhlymo.supabase.co"
SUPA_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5mamZxZGZmdWxocWhzemhseW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Mzk1MDMwOCwiZXhwIjoyMDg5NTI2MzA4fQ.zy7Bfl5cOZGF_CU2yiHn3sd24olsx_Hzc985Ov_t5Ys"

GEOJSON_URLS = {
    "chicago": f"{SUPA_URL}/storage/v1/object/public/geojson/precincts_chicago.geojson",
    "suburban": f"{SUPA_URL}/storage/v1/object/public/geojson/precincts_suburban.geojson",
}


def make_precinct_id(*parts):
    """Compute precinct_id hash — must match frontend makeId() and all loaders.
    
    Formula: MD5("part1|part2|...".lower())[:16]
    """
    raw = "|".join(str(p).strip().lower() for p in parts)
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def pad2(n):
    return str(n).zfill(2)


def rpc_call(function_name, params=None):
    """Call a Supabase RPC function."""
    url = f"{SUPA_URL}/rest/v1/rpc/{function_name}"
    data = json.dumps(params or {}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("apikey", SUPA_KEY)
    req.add_header("Authorization", f"Bearer {SUPA_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "return=representation")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"  RPC ERROR {function_name}: {e.code} — {body[:200]}")
        return None


def fetch_geojson_pids():
    """Fetch precinct IDs from both GeoJSON files, computing MD5 hashes.
    
    Chicago GeoJSON: properties = {ward, precinct, name, jur}
      → MD5("chicago|ward XX precinct YY".lower())[:16]
    Suburban GeoJSON: properties = {precinctid, name, jur}
      → MD5("cook_suburban|PRECINCTID".lower())[:16]
    """
    all_pids = set()
    
    for geo_name, url in GEOJSON_URLS.items():
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=60) as resp:
                geo = json.loads(resp.read().decode())
                features = geo.get("features", [])
                count = 0
                
                for f in features:
                    props = f.get("properties", {})
                    
                    if geo_name == "chicago":
                        ward = props.get("ward")
                        precinct = props.get("precinct")
                        if ward is not None and precinct is not None:
                            name = f"Ward {pad2(ward)} Precinct {pad2(precinct)}"
                            pid = make_precinct_id("chicago", name)
                            all_pids.add(pid)
                            count += 1
                    elif geo_name == "suburban":
                        precinctid = props.get("precinctid")
                        if precinctid:
                            pid = make_precinct_id("cook_suburban", precinctid)
                            all_pids.add(pid)
                            count += 1
                
                print(f"  GeoJSON '{geo_name}': {len(features)} features → {count} precinct IDs computed")
        except Exception as e:
            print(f"  ERROR loading GeoJSON '{geo_name}': {e}")
    
    return all_pids


def main():
    import argparse
    parser = argparse.ArgumentParser(description="D4D Map Coverage Test")
    parser.add_argument("--election", help="Filter by election year (e.g., 2026)")
    parser.add_argument("--summary", action="store_true", help="Summary only")
    args = parser.parse_args()

    print("=" * 70)
    print("  D4D MAP COVERAGE TEST")
    print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 70)

    # Step 1: Load GeoJSON precinct IDs (compute hashes)
    print("\n[1/3] Loading GeoJSON precinct IDs (computing MD5 hashes)...")
    geo_pids = fetch_geojson_pids()
    print(f"  Total GeoJSON precinct IDs: {len(geo_pids)}")

    # Step 2: Get all elections and races
    print("\n[2/3] Fetching elections and races from Supabase...")
    elections = rpc_call("get_elections")
    if not elections:
        print("  FATAL: Could not fetch elections")
        sys.exit(2)
    print(f"  Elections: {len(elections)}")

    if args.election:
        elections = [e for e in elections if args.election in str(e.get("id", "")) or args.election in str(e.get("name", ""))]
        print(f"  Filtered to {len(elections)} elections matching '{args.election}'")

    all_races = []
    for elec in elections:
        eid = elec["id"]
        races = rpc_call("get_races", {"p_election_id": eid})
        if races:
            for r in races:
                r["_election_id"] = eid
                r["_election_name"] = elec.get("name", eid)
            all_races.extend(races)
            print(f"  {elec.get('name', eid)}: {len(races)} races")
        else:
            print(f"  {elec.get('name', eid)}: NO RACES RETURNED")

    print(f"  Total races to test: {len(all_races)}")

    # Step 3: Test each race
    print(f"\n[3/3] Testing map data for {len(all_races)} races...")
    
    results = {"pass": [], "warn": [], "fail": []}
    stats_by_election = defaultdict(lambda: {"total": 0, "pass": 0, "warn": 0, "fail": 0, "precincts": set()})
    stats_by_race_type = defaultdict(lambda: {"total": 0, "pass": 0, "warn": 0, "fail": 0})

    for i, race in enumerate(all_races):
        race_id = race.get("id") or race.get("race_id")
        race_name = race.get("name") or race.get("race_name", "?")
        race_type = race.get("race_type", "?")
        election_name = race.get("_election_name", "?")
        election_id = race.get("_election_id", "?")

        map_data = rpc_call("get_race_map", {"p_race_id": race_id})

        if map_data is None:
            status = "fail"
            msg = "RPC returned None/error"
            results["fail"].append((election_name, race_name, race_type, msg, 0))
        elif len(map_data) == 0:
            status = "fail"
            msg = "0 precinct results — empty map"
            results["fail"].append((election_name, race_name, race_type, msg, 0))
        else:
            map_pids = set()
            for row in map_data:
                pid = row.get("precinct_id")
                if pid:
                    map_pids.add(pid)
            
            matched = map_pids & geo_pids
            unmatched = map_pids - geo_pids
            match_rate = len(matched) / len(map_pids) if map_pids else 0

            stats_by_election[election_id]["precincts"].update(map_pids)

            if match_rate < 0.90:
                status = "fail"
                msg = f"{len(map_pids)} precincts, {match_rate:.1%} match ({len(unmatched)} unmatched)"
                results["fail"].append((election_name, race_name, race_type, msg, len(map_pids)))
            elif match_rate < 1.0:
                status = "warn"
                msg = f"{len(map_pids)} precincts, {match_rate:.1%} match ({len(unmatched)} unmatched)"
                results["warn"].append((election_name, race_name, race_type, msg, len(map_pids)))
            else:
                status = "pass"
                msg = f"{len(map_pids)} precincts, 100% GeoJSON match"
                results["pass"].append((election_name, race_name, race_type, msg, len(map_pids)))

        stats_by_election[election_id]["total"] += 1
        stats_by_election[election_id][status] += 1
        stats_by_race_type[race_type]["total"] += 1
        stats_by_race_type[race_type][status] += 1

        if (i + 1) % 200 == 0 or (i + 1) == len(all_races):
            print(f"  Tested {i+1}/{len(all_races)} races... "
                  f"({len(results['pass'])} pass, {len(results['warn'])} warn, {len(results['fail'])} fail)")

    # ─── Report ───
    print("\n" + "=" * 70)
    print("  RESULTS")
    print("=" * 70)

    print("\n── By Election ──")
    for eid in sorted(stats_by_election.keys()):
        s = stats_by_election[eid]
        elec_name = next((e.get("name", eid) for e in elections if e["id"] == eid), eid)
        icon = "✓" if s["fail"] == 0 and s["warn"] == 0 else ("⚠" if s["fail"] == 0 else "✗")
        print(f"  {icon} {elec_name}: {s['total']} races — "
              f"{s['pass']} pass, {s['warn']} warn, {s['fail']} fail — "
              f"{len(s['precincts'])} distinct precincts")

    print("\n── By Race Type ──")
    for rtype in sorted(stats_by_race_type.keys()):
        s = stats_by_race_type[rtype]
        icon = "✓" if s["fail"] == 0 and s["warn"] == 0 else ("⚠" if s["fail"] == 0 else "✗")
        print(f"  {icon} {rtype}: {s['total']} races — "
              f"{s['pass']} pass, {s['warn']} warn, {s['fail']} fail")

    if results["fail"]:
        print(f"\n── FAILURES ({len(results['fail'])}) ──")
        for elec, name, rtype, msg, _ in results["fail"][:50]:
            print(f"  ✗ [{elec}] {name} ({rtype}): {msg}")
        if len(results["fail"]) > 50:
            print(f"  ... and {len(results['fail']) - 50} more failures")

    if results["warn"] and not args.summary:
        print(f"\n── WARNINGS ({len(results['warn'])}) ──")
        for elec, name, rtype, msg, _ in results["warn"][:30]:
            print(f"  ⚠ [{elec}] {name} ({rtype}): {msg}")
        if len(results["warn"]) > 30:
            print(f"  ... and {len(results['warn']) - 30} more warnings")

    total = len(all_races)
    p, w, f = len(results["pass"]), len(results["warn"]), len(results["fail"])
    overall = "PASS" if f == 0 and w == 0 else ("WARN" if f == 0 else "FAIL")
    
    print("\n" + "─" * 70)
    print(f"  OVERALL: {overall}  ({p} pass, {w} warn, {f} fail out of {total} races)")
    print("─" * 70)

    # Save JSON report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall": overall,
        "total_races": total,
        "passes": p,
        "warnings": w,
        "failures": f,
        "failed_races": [
            {"election": e, "race": n, "type": t, "detail": m, "precincts": pc}
            for e, n, t, m, pc in results["fail"]
        ],
        "warned_races": [
            {"election": e, "race": n, "type": t, "detail": m, "precincts": pc}
            for e, n, t, m, pc in results["warn"]
        ],
        "by_election": {
            eid: {"total": s["total"], "pass": s["pass"], "warn": s["warn"], "fail": s["fail"],
                  "distinct_precincts": len(s["precincts"])}
            for eid, s in stats_by_election.items()
        },
        "by_race_type": dict(stats_by_race_type),
    }
    
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "map_coverage_report.json")
    with open(report_path, "w") as f_out:
        json.dump(report, f_out, indent=2, default=str)
    print(f"\n  Report saved: {report_path}")

    sys.exit(0 if overall == "PASS" else (1 if overall == "WARN" else 2))


if __name__ == "__main__":
    main()
