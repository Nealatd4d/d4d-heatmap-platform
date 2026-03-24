#!/usr/bin/env python3
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
