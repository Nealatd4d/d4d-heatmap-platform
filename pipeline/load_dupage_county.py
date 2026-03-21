#!/usr/bin/env python3
"""
DuPage County IL → Supabase Postgres loader.

Boundaries only (no election data in archive).
Creates jurisdiction and precincts from Election_Precincts.geojson.
"""

import hashlib
import json
import os
import sys
import time

import psycopg2

DB_URI = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres.nfjfqdffulhqhszhlymo:D4dHeatmap2026!Pg"
    "@aws-0-us-west-2.pooler.supabase.com:5432/postgres"
)

JURISDICTION_ID = "dupage_county"
GEOJSON_PATH = "/home/user/workspace/county_expansion/Election_Precincts.geojson"


def make_id(*parts):
    raw = "|".join(str(p).strip().lower() for p in parts)
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def main():
    print("=" * 60)
    print("DUPAGE COUNTY LOADER (Boundaries Only)")
    print("=" * 60)
    t0 = time.time()

    # Load GeoJSON
    with open(GEOJSON_PATH, 'r') as f:
        data = json.load(f)

    features = data['features']
    print(f"Loaded {len(features)} precinct features from GeoJSON")

    # Build precinct list
    precincts = []
    for feat in features:
        props = feat['properties']
        source_name = props.get('PrecinctName', '').strip()
        if not source_name:
            continue
        
        pid = make_id(JURISDICTION_ID, source_name)
        # DuPage uses PrecinctName = "Bloomingdale 60", PrecinctID = "2-60"
        # No ward concept — just precinct number
        label = props.get('Label')
        precinct_num = int(label) if label else None
        
        precincts.append((pid, JURISDICTION_ID, source_name, None, precinct_num))

    print(f"Parsed {len(precincts)} precincts")

    # Connect to DB
    conn = psycopg2.connect(DB_URI, connect_timeout=30)
    conn.autocommit = False
    cur = conn.cursor()

    # Create jurisdiction
    print("\n--- Jurisdiction ---")
    cur.execute("""
        INSERT INTO jurisdictions (id, name, type, county, state)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
    """, (JURISDICTION_ID, "DuPage County", "county", "DuPage", "IL"))
    conn.commit()
    print(f"  Upserted: {JURISDICTION_ID}")

    # Load precincts
    print(f"\n--- Precincts ({len(precincts)}) ---")
    for pid, jid, sname, ward, pnum in precincts:
        cur.execute("""
            INSERT INTO precincts (id, jurisdiction_id, source_precinct_name, ward, precinct_number)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                jurisdiction_id = EXCLUDED.jurisdiction_id,
                source_precinct_name = EXCLUDED.source_precinct_name,
                ward = EXCLUDED.ward,
                precinct_number = EXCLUDED.precinct_number;
        """, (pid, jid, sname, ward, pnum))
    conn.commit()
    print(f"  Loaded {len(precincts)}")

    # Verify
    cur.execute("SELECT COUNT(*) FROM precincts WHERE jurisdiction_id = %s;", (JURISDICTION_ID,))
    print(f"\nDuPage precincts in DB: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM precincts;")
    print(f"Total precincts in DB: {cur.fetchone()[0]}")

    cur.close()
    conn.close()

    print(f"\n{'='*60}")
    print(f"DUPAGE COUNTY LOAD COMPLETE in {time.time()-t0:.1f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
