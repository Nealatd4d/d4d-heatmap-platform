#!/usr/bin/env python3
"""
D4D Election Heatmap Platform — Data Pipeline v2
Produces a compact elections.json with only mappable races (state rep, senate, congress, etc.)
and a separate precinct geometry file.
"""

import csv
import json
import re
import os
import sys
import datetime
import xml.etree.ElementTree as ET
from collections import defaultdict

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(WORKSPACE, 'data')
ROOT = os.path.dirname(WORKSPACE)

# ── Data sources ──

CHICAGO_CSVS = {
    '2022_general': os.path.join(ROOT, 'chicago_cook_2022GE.csv'),
    '2024_primary': os.path.join(ROOT, 'chicago_cook_2024GP.csv'),
    '2024_general': os.path.join(ROOT, 'chicago_cook_2024GE.csv'),
}

# Categories we keep (mappable to district boundaries)
KEEP_CATEGORIES = {'state_rep', 'state_senate', 'congress', 'us_senate', 'governor'}

# Contest name patterns
PATTERNS = [
    (r'(\d+)(?:ST|ND|RD|TH)\s+REPRESENTATIVE', 'state_rep', lambda m: int(m.group(1))),
    (r'(\d+)(?:ST|ND|RD|TH)\s+SENATE(?!\s+CENTRAL)', 'state_senate', lambda m: int(m.group(1))),
    (r'(\d+)(?:ST|ND|RD|TH)\s+CONGRESS', 'congress', lambda m: int(m.group(1))),
    (r'UNITED STATES SENATOR', 'us_senate', lambda m: None),
    (r'U\.?S\.?\s+SENATOR', 'us_senate', lambda m: None),
    (r'GOVERNOR', 'governor', lambda m: None),
    (r'PRESIDENT.*U\.?S', 'president', lambda m: None),
    # Cook County specific
    (r'COMMISSIONER.*(\d+)', 'cook_commissioner', lambda m: int(m.group(1))),
    (r'WATER RECLAMATION', 'mwrd', lambda m: None),
]

SKIP_CANDIDATES = {'UNDER VOTES', 'OVER VOTES', 'WRITE-IN', 'NO CANDIDATE', ''}


def normalize_chicago_precinct(name):
    """'Ward 01 Precinct 05' → '01005'"""
    m = re.match(r'Ward\s+(\d+)\s+Precinct\s+(\d+)', name, re.I)
    if m:
        return f"{int(m.group(1)):02d}{int(m.group(2)):03d}"
    return None


def classify_contest(raw_name):
    """Returns (category, district_number_or_None) or (None, None)"""
    upper = raw_name.strip().upper()
    for pattern, category, dist_fn in PATTERNS:
        m = re.search(pattern, upper)
        if m:
            return category, dist_fn(m)
    return None, None


def parse_chicago(filepath, election_key):
    """Parse SBOE CSV → {precinct_id: {reg, bal, races: {contest: {cands}}}}"""
    print(f"  {os.path.basename(filepath)}...")
    
    precincts = {}
    
    with open(filepath, 'r', errors='ignore') as f:
        for row in csv.DictReader(f):
            pname = row.get('PrecinctName', '').strip()
            if not pname:
                continue
            pid = normalize_chicago_precinct(pname)
            if not pid:
                continue
            
            contest = row.get('ContestName', '').strip()
            candidate = row.get('CandidateName', '').strip()
            votes = int(row.get('VoteCount', '0').strip() or '0')
            reg = int(row.get('Registration', '0').strip() or '0')
            party = row.get('PartyName', '').strip()
            
            if pid not in precincts:
                precincts[pid] = {'reg': 0, 'bal': 0, 'races': {}}
            
            p = precincts[pid]
            
            # Blank contest = turnout summary
            if not contest:
                p['reg'] = reg
                p['bal'] = votes
                continue
            
            if candidate.upper() in SKIP_CANDIDATES:
                continue
            
            # Only keep mappable contests
            cat, dist = classify_contest(contest)
            if cat not in KEEP_CATEGORIES:
                continue
            
            # Build contest key
            ckey = f"{cat}_{dist}" if dist else cat
            
            if ckey not in p['races']:
                p['races'][ckey] = {'cat': cat, 'dist': dist, 'raw': contest, 'party': party, 'cands': []}
            
            p['races'][ckey]['cands'].append({
                'n': candidate,
                'v': votes,
                'pty': party
            })
    
    # Post-process: compute turnout, sort candidates, compute percentages
    for pid, p in precincts.items():
        p['to'] = round(p['bal'] / p['reg'] * 100, 1) if p['reg'] > 0 else 0
        
        for ckey, race in p['races'].items():
            race['cands'].sort(key=lambda x: x['v'], reverse=True)
            total = sum(c['v'] for c in race['cands'])
            race['total'] = total
            for c in race['cands']:
                c['pct'] = round(c['v'] / total * 100, 1) if total > 0 else 0
    
    print(f"    → {len(precincts)} precincts")
    return precincts


def parse_kml_boundaries(kml_path, name_prefix=''):
    """Parse a KML file into a dict of {district_name: geojson_geometry}"""
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    tree = ET.parse(kml_path)
    root = tree.getroot()
    
    districts = {}
    
    for pm in root.findall('.//kml:Placemark', ns):
        name_el = pm.find('kml:name', ns)
        if name_el is None or name_el.text is None:
            continue
        name = name_el.text.strip()
        
        # Get coordinates from various geometry types
        coords_list = []
        
        for coord_el in pm.findall('.//kml:coordinates', ns):
            if coord_el.text:
                ring = []
                for point in coord_el.text.strip().split():
                    parts = point.split(',')
                    if len(parts) >= 2:
                        ring.append([float(parts[0]), float(parts[1])])
                if ring:
                    coords_list.append(ring)
        
        if not coords_list:
            continue
        
        key = f"{name_prefix}{name}" if name_prefix else name
        
        if key in districts:
            # Multi-polygon: append rings
            if districts[key]['type'] == 'Polygon':
                districts[key] = {
                    'type': 'MultiPolygon',
                    'coordinates': [districts[key]['coordinates'], [coords_list[0]]]
                }
            else:
                districts[key]['coordinates'].append([coords_list[0]])
        else:
            if len(coords_list) == 1:
                districts[key] = {'type': 'Polygon', 'coordinates': [coords_list[0]]}
            else:
                districts[key] = {'type': 'MultiPolygon', 'coordinates': [[c] for c in coords_list]}
    
    return districts


def parse_chicago_precinct_kml(kml_path):
    """Parse Chicago ward-precinct KML → {precinct_id: geojson_geometry}"""
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    tree = ET.parse(kml_path)
    root = tree.getroot()
    
    precincts = {}
    
    for pm in root.findall('.//kml:Placemark', ns):
        # Get ward and precinct from Data elements
        ward = None
        precinct = None
        
        for data_el in pm.findall('.//kml:Data', ns):
            name = data_el.get('name', '')
            val_el = data_el.find('kml:value', ns)
            if val_el is not None and val_el.text:
                if name == 'ward':
                    ward = int(val_el.text)
                elif name == 'precinct':
                    precinct = int(val_el.text)
        
        if ward is None or precinct is None:
            continue
        
        pid = f"{ward:02d}{precinct:03d}"
        
        # Get coordinates
        coords_list = []
        for coord_el in pm.findall('.//kml:coordinates', ns):
            if coord_el.text:
                ring = []
                for point in coord_el.text.strip().split():
                    parts = point.split(',')
                    if len(parts) >= 2:
                        ring.append([float(parts[0]), float(parts[1])])
                if ring:
                    coords_list.append(ring)
        
        if coords_list:
            precincts[pid] = {
                'type': 'Polygon',
                'coordinates': coords_list  # outer ring + any holes
            }
    
    return precincts


def build_precinct_geojson(chicago_precincts, election_data):
    """Build a GeoJSON FeatureCollection of all precincts with embedded election data."""
    features = []
    
    for pid, geom in chicago_precincts.items():
        props = {
            'id': pid,
            'ward': int(pid[:2]),
            'precinct': int(pid[2:]),
            'name': f"Ward {int(pid[:2])} Precinct {int(pid[2:])}",
        }
        
        # Add election data for each election
        for ekey, edata in election_data.items():
            if pid in edata:
                pdata = edata[pid]
                props[f"{ekey}_reg"] = pdata['reg']
                props[f"{ekey}_bal"] = pdata['bal']
                props[f"{ekey}_to"] = pdata['to']
                
                # Add race results
                for rkey, rdata in pdata['races'].items():
                    # Store winner info and candidate breakdown
                    if rdata['cands']:
                        winner = rdata['cands'][0]
                        props[f"{ekey}_{rkey}_winner"] = winner['n']
                        props[f"{ekey}_{rkey}_winner_pct"] = winner['pct']
                        props[f"{ekey}_{rkey}_winner_v"] = winner['v']
                        props[f"{ekey}_{rkey}_total"] = rdata['total']
                        
                        # Store all candidates as JSON string
                        props[f"{ekey}_{rkey}_cands"] = json.dumps(rdata['cands'], separators=(',', ':'))
        
        features.append({
            'type': 'Feature',
            'geometry': geom,
            'properties': props
        })
    
    return {
        'type': 'FeatureCollection',
        'features': features
    }


def main():
    print("=" * 60)
    print("D4D Heatmap Platform — Data Pipeline v2")
    print("=" * 60)
    
    # ── Step 1: Parse election data ──
    print("\n── Step 1: Parse election data ──")
    election_data = {}
    
    for ekey, filepath in CHICAGO_CSVS.items():
        if os.path.exists(filepath):
            election_data[ekey] = parse_chicago(filepath, ekey)
    
    # ── Step 2: Parse precinct geometry ──
    print("\n── Step 2: Parse precinct geometry ──")
    chicago_kml = os.path.join(ROOT, 'Chicago-Ward-Precincts-2023-2.kml')
    chicago_precincts = parse_chicago_precinct_kml(chicago_kml)
    print(f"  Chicago precincts: {len(chicago_precincts)} geometries")
    
    # Also load Cook County precincts
    cook_geojson = os.path.join(ROOT, 'cook_precincts.geojson')
    cook_precincts = {}
    if os.path.exists(cook_geojson):
        with open(cook_geojson, 'r') as f:
            cook_data = json.load(f)
        for feat in cook_data.get('features', []):
            pid = feat['properties'].get('id2010', '') or feat['properties'].get('objectid', '')
            if pid:
                cook_precincts[str(pid)] = feat['geometry']
        print(f"  Cook County precincts: {len(cook_precincts)} geometries")
    
    # ── Step 3: Parse district boundaries ──
    print("\n── Step 3: Parse district boundaries ──")
    boundaries = {}
    
    kml_files = {
        'state_rep': os.path.join(ROOT, 'Illinois-House-Legislative-Maps-2021.kml'),
        'state_senate': os.path.join(ROOT, 'Illinois-State-Senate-2.kml'),
        'congress': os.path.join(ROOT, 'Illinois-Congressional-Districts.kml'),
    }
    
    for btype, kml_path in kml_files.items():
        if os.path.exists(kml_path):
            districts = parse_kml_boundaries(kml_path)
            boundaries[btype] = districts
            print(f"  {btype}: {len(districts)} districts")
    
    # ── Step 4: Build compact output ──
    print("\n── Step 4: Build output files ──")
    
    # A) Precinct GeoJSON with election data embedded
    precinct_geojson = build_precinct_geojson(chicago_precincts, election_data)
    precinct_path = os.path.join(DATA_DIR, 'chicago_precincts.geojson')
    with open(precinct_path, 'w') as f:
        json.dump(precinct_geojson, f, separators=(',', ':'))
    print(f"  Precincts: {precinct_path} ({os.path.getsize(precinct_path)/1024/1024:.1f} MB, {len(precinct_geojson['features'])} features)")
    
    # B) District boundaries GeoJSON files (one per type)
    for btype, districts in boundaries.items():
        features = []
        for name, geom in districts.items():
            features.append({
                'type': 'Feature',
                'geometry': geom,
                'properties': {'name': name, 'district': name, 'type': btype}
            })
        
        boundary_geojson = {'type': 'FeatureCollection', 'features': features}
        boundary_path = os.path.join(DATA_DIR, f'boundaries_{btype}.geojson')
        with open(boundary_path, 'w') as f:
            json.dump(boundary_geojson, f, separators=(',', ':'))
        print(f"  Boundaries ({btype}): {boundary_path} ({os.path.getsize(boundary_path)/1024:.0f} KB)")
    
    # C) Election metadata (what races exist, what elections, etc.)
    meta = {
        'generated': datetime.datetime.now().isoformat(),
        'elections': {},
        'district_types': list(boundaries.keys()),
        'chicago_precinct_count': len(chicago_precincts),
    }
    
    for ekey, edata in election_data.items():
        races_found = defaultdict(set)
        for pid, pdata in edata.items():
            for rkey, rdata in pdata['races'].items():
                races_found[rdata['cat']].add(rkey)
        
        meta['elections'][ekey] = {
            'precinct_count': len(edata),
            'races': {cat: sorted(list(keys)) for cat, keys in races_found.items()}
        }
    
    meta_path = os.path.join(DATA_DIR, 'meta.json')
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)
    print(f"  Meta: {meta_path}")
    
    # D) Compact per-election data files (one per election, only race results)
    for ekey, edata in election_data.items():
        compact = {}
        for pid, pdata in edata.items():
            compact[pid] = {
                'r': pdata['reg'],
                'b': pdata['bal'],
                't': pdata['to'],
                'x': {}  # races
            }
            for rkey, rdata in pdata['races'].items():
                compact[pid]['x'][rkey] = {
                    'c': [[c['n'], c['v'], c['pct']] for c in rdata['cands']],
                    't': rdata['total']
                }
        
        elec_path = os.path.join(DATA_DIR, f'election_{ekey}.json')
        with open(elec_path, 'w') as f:
            json.dump(compact, f, separators=(',', ':'))
        print(f"  Election data ({ekey}): {os.path.getsize(elec_path)/1024:.0f} KB")
    
    print(f"\n{'=' * 60}")
    print("Pipeline complete.")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
