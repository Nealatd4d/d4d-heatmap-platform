#!/usr/bin/env python3
"""
Fix precinct-to-district mapping v2: handles split precincts.

Strategy:
1. Extract all precinct-district assignments from election data
2. For split precincts (appearing in 2+ districts of same type), 
   assign to the district with the highest vote total
3. Use 2024 general as primary source, fall back to earlier elections
4. Output clean 1:1 mapping per district type
"""
import json
import os
from collections import defaultdict

DATA_DIR = "/home/user/workspace/d4d-heatmap-platform/data"

# Election files in priority order (most recent first)
ELECTION_FILES = [
    "election_2024_general.json",
    "election_2024_primary.json", 
    "election_2022_general.json",
]

DISTRICT_PREFIXES = ["congress_", "state_senate_", "state_rep_"]

# Step 1: For each precinct + district type, accumulate (district, total_votes) across elections
# Structure: precinct_assignments[pid][prefix] = {district_key: total_votes}
precinct_assignments = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

for fn in ELECTION_FILES:
    fpath = os.path.join(DATA_DIR, fn)
    with open(fpath) as f:
        data = json.load(f)
    
    for pid, pdata in data.items():
        if "x" not in pdata:
            continue
        for race_key, race_data in pdata["x"].items():
            for prefix in DISTRICT_PREFIXES:
                if race_key.startswith(prefix):
                    votes = race_data.get("t", 0)
                    precinct_assignments[pid][prefix][race_key] += votes
                    break

# Step 2: Resolve each precinct to exactly one district per type
# Pick the district with the most total votes across all elections
district_precincts = defaultdict(set)  # district_key -> set of pids
precinct_districts = defaultdict(list)  # pid -> list of district_keys (one per type)

split_log = []

for pid in sorted(precinct_assignments.keys()):
    for prefix in DISTRICT_PREFIXES:
        candidates = precinct_assignments[pid][prefix]
        if not candidates:
            continue
        
        if len(candidates) == 1:
            # Clean assignment
            winner = list(candidates.keys())[0]
        else:
            # Split precinct — pick highest vote total
            sorted_cands = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
            winner = sorted_cands[0][0]
            split_log.append({
                "precinct": pid,
                "type": prefix.rstrip("_"),
                "assigned_to": winner,
                "votes": sorted_cands[0][1],
                "alternatives": [(k, v) for k, v in sorted_cands[1:]],
            })
        
        district_precincts[winner].add(pid)
        precinct_districts[pid].append(winner)

# Step 3: Convert to JSON-serializable format
district_precincts_json = {k: sorted(v) for k, v in sorted(district_precincts.items())}
precinct_districts_json = {k: sorted(v) for k, v in sorted(precinct_districts.items())}

# Step 4: Write output
dp_path = os.path.join(DATA_DIR, "district_precincts.json")
pd_path = os.path.join(DATA_DIR, "precinct_districts.json")

with open(dp_path, "w") as f:
    json.dump(district_precincts_json, f)
print(f"Wrote {dp_path}")

with open(pd_path, "w") as f:
    json.dump(precinct_districts_json, f)
print(f"Wrote {pd_path}")

# Step 5: Summary
print(f"\n=== Ground-Truth Mapping (Split-Resolved) ===")
print(f"Total precincts mapped: {len(precinct_districts_json)}")
print(f"Split precincts resolved: {len(split_log)}")

for prefix, label in [("congress_", "Congress"), ("state_senate_", "State Senate"), ("state_rep_", "State Rep")]:
    keys = sorted([k for k in district_precincts_json if k.startswith(prefix)])
    total = sum(len(district_precincts_json[k]) for k in keys)
    print(f"\n{label} ({len(keys)} districts, {total} total precinct assignments):")
    for k in keys:
        print(f"  {k}: {len(district_precincts_json[k])} precincts")

# Step 6: Validate — each precinct should now have exactly one of each type
print("\n=== Validation ===")
issues = 0
for pid, districts in precinct_districts_json.items():
    for prefix in DISTRICT_PREFIXES:
        matches = [d for d in districts if d.startswith(prefix)]
        if len(matches) > 1:
            print(f"  ERROR: {pid} still in multiple {prefix}: {matches}")
            issues += 1
if issues == 0:
    print("  PASS: Every precinct assigned to exactly one district per type")
else:
    print(f"  FAIL: {issues} conflicts remain")

# Step 7: Cross-check totals
print("\n=== Total Precinct Check ===")
all_pids = set(precinct_districts_json.keys())
print(f"Precincts in mapping: {len(all_pids)}")
# Check every precinct in every election file is covered
for fn in ELECTION_FILES:
    fpath = os.path.join(DATA_DIR, fn)
    with open(fpath) as f:
        data = json.load(f)
    election_pids = set(data.keys())
    missing = election_pids - all_pids
    extra = all_pids - election_pids
    print(f"  {fn}: {len(election_pids)} precincts, {len(missing)} not in mapping, {len(extra)} only in mapping")

# Step 8: Compare with old centroid mapping
print("\n=== vs Old Centroid Mapping ===")
old_path = os.path.join(DATA_DIR, "district_precincts_old.json")
if os.path.exists(old_path):
    with open(old_path) as f:
        old = json.load(f)
    for k in sorted(district_precincts_json.keys()):
        new_count = len(district_precincts_json[k])
        old_count = len(old.get(k, []))
        diff = new_count - old_count
        marker = " =" if diff == 0 else f" +{diff}" if diff > 0 else f" {diff}"
        print(f"  {k}: {old_count} -> {new_count} ({marker})")

# Show a few split examples
print(f"\n=== Split Precinct Examples (first 15) ===")
for s in split_log[:15]:
    alts = ", ".join([f"{k}({v} votes)" for k, v in s["alternatives"]])
    print(f"  {s['precinct']}: assigned to {s['assigned_to']} ({s['votes']} votes), rejected: {alts}")
