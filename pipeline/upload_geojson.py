#!/usr/bin/env python3
"""
Upload Lake County and DuPage County precinct GeoJSON to Supabase Storage.

Strips unnecessary properties to reduce file size for frontend loading.
Normalizes property names to match Cook County format for the frontend.
"""

import hashlib
import json
import os
import sys

import requests

SUPABASE_URL = "https://nfjfqdffulhqhszhlymo.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5mamZxZGZmdWxocWhzemhseW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Mzk1MDMwOCwiZXhwIjoyMDg5NTI2MzA4fQ.zy7Bfl5cOZGF_CU2yiHn3sd24olsx_Hzc985Ov_t5Ys"
BUCKET = "geojson"

JURISDICTION_LAKE = "lake_county"
JURISDICTION_DUPAGE = "dupage_county"


def make_id(*parts):
    raw = "|".join(str(p).strip().lower() for p in parts)
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def prepare_lake_county_geojson():
    """Load Lake County voting precincts, strip to essential properties."""
    path = "/home/user/workspace/county_expansion/LakeCounty_PoliticalBoundaries_2514434723204303043.geojson"
    with open(path, 'r') as f:
        data = json.load(f)
    
    features = []
    for feat in data['features']:
        props = feat['properties']
        twp_pct = props.get('TWP_PCT', '')
        precinct_num = props.get('PRECINCT')
        
        # Generate precinct_id matching the DB
        pid = make_id(JURISDICTION_LAKE, twp_pct)
        
        new_feat = {
            "type": "Feature",
            "properties": {
                "precinct_id": pid,
                "name": twp_pct,
                "jurisdiction_id": JURISDICTION_LAKE,
            },
            "geometry": feat['geometry']
        }
        features.append(new_feat)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


def prepare_dupage_county_geojson():
    """Load DuPage County election precincts, strip to essential properties."""
    path = "/home/user/workspace/county_expansion/Election_Precincts.geojson"
    with open(path, 'r') as f:
        data = json.load(f)
    
    features = []
    for feat in data['features']:
        props = feat['properties']
        source_name = props.get('PrecinctName', '').strip()
        if not source_name:
            continue
        
        pid = make_id(JURISDICTION_DUPAGE, source_name)
        
        new_feat = {
            "type": "Feature",
            "properties": {
                "precinct_id": pid,
                "name": source_name,
                "jurisdiction_id": JURISDICTION_DUPAGE,
            },
            "geometry": feat['geometry']
        }
        features.append(new_feat)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


def upload_to_supabase(filename, geojson_data):
    """Upload GeoJSON to Supabase Storage bucket."""
    content = json.dumps(geojson_data, separators=(',', ':'))  # minified
    
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "apikey": SUPABASE_SERVICE_KEY,
        "Content-Type": "application/json",
    }
    
    # Try to upsert (delete + create)
    # First delete if exists
    delete_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{filename}"
    requests.delete(delete_url, headers=headers)
    
    # Upload
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{filename}"
    resp = requests.post(upload_url, headers=headers, data=content.encode('utf-8'))
    
    if resp.status_code in (200, 201):
        size_mb = len(content) / (1024 * 1024)
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"
        print(f"  Uploaded {filename} ({size_mb:.1f} MB)")
        print(f"  URL: {public_url}")
        return True
    else:
        print(f"  FAILED to upload {filename}: {resp.status_code} {resp.text}")
        return False


def main():
    print("=" * 60)
    print("GEOJSON UPLOAD TO SUPABASE STORAGE")
    print("=" * 60)
    
    # Lake County
    print("\n--- Lake County ---")
    lake_geojson = prepare_lake_county_geojson()
    print(f"  Prepared {len(lake_geojson['features'])} features")
    upload_to_supabase("precincts_lake.geojson", lake_geojson)
    
    # DuPage County
    print("\n--- DuPage County ---")
    dupage_geojson = prepare_dupage_county_geojson()
    print(f"  Prepared {len(dupage_geojson['features'])} features")
    upload_to_supabase("precincts_dupage.geojson", dupage_geojson)
    
    # Verify: list files in bucket
    print("\n--- Files in geojson bucket ---")
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "apikey": SUPABASE_SERVICE_KEY,
    }
    resp = requests.post(
        f"{SUPABASE_URL}/storage/v1/object/list/{BUCKET}",
        headers=headers,
        json={"prefix": "", "limit": 100}
    )
    if resp.status_code == 200:
        for item in resp.json():
            print(f"  {item.get('name', '?')} ({item.get('metadata', {}).get('size', '?')} bytes)")
    
    print("\n" + "=" * 60)
    print("UPLOAD COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
