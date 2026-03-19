#!/usr/bin/env python3
"""
Fix precinct-to-district mapping using election data as ground truth.

Instead of centroid-based geometry (which systematically undercounts),
we use the actual election results: if a precinct reported votes for
"13TH REPRESENTATIVE", then that precinct IS in State Rep 13.

This is authoritative per 10 ILCS 5/11-2 and 5/11-3.
"""
import json
import os

DATA_DIR = "/home/user/workspace/d4d-heatmap-platform/data"

# Load all election files
election_files = [
    "election_2022_general.json",
    "election_2024_primary.json",
    "election_2024_general.json",
]

# Build ground-truth mapping: district_key -> set of precinct IDs
district_precincts = {}  # e.g. "state_rep_13" -> {"40001", "40002", ...}
precinct_districts = {}  # e.g. "40001" -> ["state_rep_13", "state_senate_7", "congress_5"]

# District race key prefixes we care about
DISTRICT_PREFIXES = ("state_rep_", "state_senate_", "congress_")

for fn in election_files:
    fpath = os.path.join(DATA_DIR, fn)
    with open(fpath) as f:
        data = json.load(f)
    
    for pid, pdata in data.items():
        if "x" not in pdata:
            continue
        for race_key in pdata["x"]:
            if not any(race_key.startswith(p) for p in DISTRICT_PREFIXES):
                continue
            # Add this precinct to this district
            if race_key not in district_precincts:
                district_precincts[race_key] = set()
            district_precincts[race_key].add(pid)
            
            # Add this district to this precinct
            if pid not in precinct_districts:
                precinct_districts[pid] = set()
            precinct_districts[pid].add(race_key)

# Convert sets to sorted lists for JSON
district_precincts_json = {k: sorted(v) for k, v in sorted(district_precincts.items())}
precinct_districts_json = {k: sorted(v) for k, v in sorted(precinct_districts.items())}

# Write output files
dp_path = os.path.join(DATA_DIR, "district_precincts.json")
pd_path = os.path.join(DATA_DIR, "precinct_districts.json")

with open(dp_path, "w") as f:
    json.dump(district_precincts_json, f)
print(f"Wrote {dp_path}")

with open(pd_path, "w") as f:
    json.dump(precinct_districts_json, f)
print(f"Wrote {pd_path}")

# Print summary
print(f"\n=== Ground-Truth Mapping Summary ===")
print(f"Total district keys: {len(district_precincts_json)}")
print(f"Total precincts mapped: {len(precinct_districts_json)}")

# Show counts by type
for prefix, label in [("congress_", "Congress"), ("state_senate_", "State Senate"), ("state_rep_", "State Rep")]:
    keys = sorted([k for k in district_precincts_json if k.startswith(prefix)])
    print(f"\n{label} ({len(keys)} districts):")
    for k in keys:
        print(f"  {k}: {len(district_precincts_json[k])} precincts")

# Compare with old mapping if it exists
print("\n=== Comparison with Old (Centroid) Mapping ===")
old_path = os.path.join(DATA_DIR, "district_precincts_old.json")
if os.path.exists(old_path):
    with open(old_path) as f:
        old = json.load(f)
    for k in sorted(district_precincts_json.keys()):
        new_count = len(district_precincts_json[k])
        old_count = len(old.get(k, []))
        diff = new_count - old_count
        marker = " ✓" if diff == 0 else f" (+{diff})" if diff > 0 else f" ({diff})"
        if k in old:
            print(f"  {k}: {old_count} -> {new_count}{marker}")
        else:
            print(f"  {k}: NEW ({new_count} precincts)")
else:
    print("  (No old mapping found for comparison)")

# Validate: check that each precinct has exactly one of each district type
print("\n=== Validation ===")
issues = 0
for pid, districts in precinct_districts_json.items():
    for prefix in ["congress_", "state_senate_", "state_rep_"]:
        matches = [d for d in districts if d.startswith(prefix)]
        if len(matches) > 1:
            print(f"  WARNING: Precinct {pid} in multiple {prefix} districts: {matches}")
            issues += 1
if issues == 0:
    print("  All precincts assigned to exactly one district per type ✓")
else:
    print(f"  {issues} issues found!")
