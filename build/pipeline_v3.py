#!/usr/bin/env python3
"""
D4D Election Heatmap Platform — Data Pipeline v3
Handles ALL race types:
  - SBOE: state_rep, state_senate, congress, us_senate, governor, judicial (circuit, subcircuit, appellate, supreme)
  - Chicago Elections Archive: mayor, clerk, treasurer, alderman (2023 municipal + runoff)
  - Chicago Elections Archive: MWRD, Cook County Commissioner (2022 general)
"""

import csv
import json
import re
import os
import sys
import datetime
from collections import defaultdict

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(WORKSPACE, 'data')
ROOT = os.path.dirname(WORKSPACE)

# ── SBOE Data Sources ──
SBOE_CSVS = {
    '2022_general': os.path.join(ROOT, 'chicago_cook_2022GE.csv'),
    '2024_primary': os.path.join(ROOT, 'chicago_cook_2024GP.csv'),
    '2024_general': os.path.join(ROOT, 'chicago_cook_2024GE.csv'),
}

# ── Chicago Elections Archive Sources ──
MUNICIPAL_2023_DIR = os.path.join(DATA_DIR, 'municipal_2023')
MUNICIPAL_2023_RUNOFF_DIR = os.path.join(DATA_DIR, 'municipal_2023_runoff')
COOK_COUNTY_2022_DIR = os.path.join(DATA_DIR, 'cook_county_2022')

SKIP_CANDIDATES = {'UNDER VOTES', 'OVER VOTES', 'WRITE-IN', 'NO CANDIDATE', ''}

# ── Contest Classification ──
# Returns (category, district_key) where district_key is like "state_rep_13" or "circuit_retain_smith"

def classify_contest(raw_name):
    """Classify SBOE contest names into categories. Returns (category, key) or (None, None)."""
    upper = raw_name.strip().upper()
    
    # State-level races
    m = re.search(r'(\d+)(?:ST|ND|RD|TH)\s+REPRESENTATIVE', upper)
    if m:
        return 'state_rep', f"state_rep_{int(m.group(1))}"
    
    m = re.search(r'(\d+)(?:ST|ND|RD|TH)\s+SENATE(?!\s+CENTRAL)', upper)
    if m:
        return 'state_senate', f"state_senate_{int(m.group(1))}"
    
    m = re.search(r'(\d+)(?:ST|ND|RD|TH)\s+CONGRESS', upper)
    if m:
        return 'congress', f"congress_{int(m.group(1))}"
    
    if re.search(r'UNITED STATES SENATOR|U\.?S\.?\s+SENATOR', upper):
        return 'us_senate', 'us_senate'
    
    if re.search(r'GOVERNOR', upper):
        return 'governor', 'governor'
    
    # Judicial: Subcircuit (must check before circuit)
    m = re.search(r'COOK\s*-\s*(\d+)(?:ST|ND|RD|TH)\s+SUBCIRCUIT', upper)
    if m:
        subcircuit_num = int(m.group(1))
        # Extract the vacancy/judge name
        name_part = re.sub(r'COOK\s*-\s*\d+(?:ST|ND|RD|TH)\s+SUBCIRCUIT\s*-?\s*', '', upper).strip()
        # Clean up: "CONVERTED FROM ASSOCIATE JUDGESHIP OF xxx" → shorten
        if 'CONVERTED FROM' in name_part:
            judge_name = re.sub(r'CONVERTED FROM ASSOCIATE JUDGESHIP OF\s*', '', name_part).strip()
            safe = re.sub(r'[^A-Z0-9]', '_', judge_name).strip('_')
            return 'subcircuit', f"subcircuit_{subcircuit_num}_conv_{safe}"
        safe = re.sub(r'[^A-Z0-9]', '_', name_part).strip('_')
        return 'subcircuit', f"subcircuit_{subcircuit_num}_{safe}"
    
    # Judicial: Circuit (county-wide Cook)
    m = re.search(r'COOK CIRCUIT\s*-?\s*RETAIN\s+(.+)', upper)
    if m:
        name = m.group(1).strip()
        safe = re.sub(r'[^A-Z0-9]', '_', name).strip('_')
        return 'circuit', f"circuit_retain_{safe}"
    
    m = re.search(r'COOK CIRCUIT\s*-?\s*(.+?)\s*(VACANCY)?$', upper)
    if m:
        name = m.group(1).strip()
        safe = re.sub(r'[^A-Z0-9]', '_', name).strip('_')
        return 'circuit', f"circuit_{safe}"
    
    # Judicial: Appellate (1st Appellate District covers Cook)
    m = re.search(r'1ST APPELLATE\s*-\s*RETAIN\s+(.+)', upper)
    if m:
        name = m.group(1).strip()
        safe = re.sub(r'[^A-Z0-9]', '_', name).strip('_')
        return 'appellate', f"appellate_retain_{safe}"
    
    m = re.search(r'1ST APPELLATE\s*-\s*(.+?)\s*(VACANCY)?$', upper)
    if m:
        name = m.group(1).strip()
        safe = re.sub(r'[^A-Z0-9]', '_', name).strip('_')
        return 'appellate', f"appellate_{safe}"
    
    # Judicial: Supreme (1st Supreme District covers Cook)
    m = re.search(r'1ST SUPREME\s*-\s*RETAIN\s+(.+)', upper)
    if m:
        name = m.group(1).strip()
        safe = re.sub(r'[^A-Z0-9]', '_', name).strip('_')
        return 'supreme', f"supreme_retain_{safe}"
    
    m = re.search(r'1ST SUPREME\s*-\s*(.+?)\s*(VACANCY)?$', upper)
    if m:
        name = m.group(1).strip()
        safe = re.sub(r'[^A-Z0-9]', '_', name).strip('_')
        return 'supreme', f"supreme_{safe}"
    
    return None, None


def normalize_precinct_id(ward, precinct):
    """Create standard 5-digit precinct ID: WWPPP."""
    return f"{int(ward):02d}{int(precinct):03d}"


def parse_sboe_csv(filepath, election_key):
    """Parse SBOE CSV → {precinct_id: {reg, bal, races: {key: {cands: [...]}}}}"""
    print(f"  Parsing SBOE: {os.path.basename(filepath)}...")
    
    precincts = {}
    skipped_categories = defaultdict(int)
    
    with open(filepath, 'r', errors='ignore') as f:
        for row in csv.DictReader(f):
            pname = row.get('PrecinctName', '').strip()
            if not pname:
                continue
            
            m = re.match(r'Ward\s+(\d+)\s+Precinct\s+(\d+)', pname, re.I)
            if not m:
                continue
            pid = normalize_precinct_id(m.group(1), m.group(2))
            
            contest = row.get('ContestName', '').strip()
            candidate = row.get('CandidateName', '').strip()
            votes = int(row.get('VoteCount', '0').strip() or '0')
            reg = int(row.get('Registration', '0').strip() or '0')
            party = row.get('PartyName', '').strip()
            
            if pid not in precincts:
                precincts[pid] = {'reg': 0, 'bal': 0, 'races': {}}
            
            p = precincts[pid]
            
            if not contest:
                p['reg'] = reg
                p['bal'] = votes
                continue
            
            if candidate.upper() in SKIP_CANDIDATES:
                continue
            
            cat, ckey = classify_contest(contest)
            if cat is None:
                skipped_categories[contest] += 1
                continue
            
            if ckey not in p['races']:
                p['races'][ckey] = {'cat': cat, 'raw': contest, 'cands': []}
            
            p['races'][ckey]['cands'].append({
                'n': candidate,
                'v': votes,
                'pty': party
            })
    
    # Post-process
    for pid, p in precincts.items():
        p['to'] = round(p['bal'] / p['reg'] * 100, 1) if p['reg'] > 0 else 0
        for ckey, race in p['races'].items():
            race['cands'].sort(key=lambda x: x['v'], reverse=True)
            total = sum(c['v'] for c in race['cands'])
            race['total'] = total
            for c in race['cands']:
                c['pct'] = round(c['v'] / total * 100, 1) if total > 0 else 0
    
    # Summary
    cats = defaultdict(int)
    for p in precincts.values():
        for r in p['races'].values():
            cats[r['cat']] += 1
    
    print(f"    → {len(precincts)} precincts, races by category: {dict(cats)}")
    if skipped_categories:
        top_skipped = sorted(skipped_categories.items(), key=lambda x: -x[1])[:5]
        print(f"    → Top skipped: {top_skipped}")
    
    return precincts


def parse_archive_csv(filepath, race_category, race_key, district_num=None):
    """Parse a Chicago Elections Archive CSV → {precinct_id: race_data}
    
    Archive CSV format: id,ward,precinct,registered,ballots,total,Cand1,Cand2,...,Cand1 Percent,...
    """
    result = {}
    
    with open(filepath, 'r', errors='ignore') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        # Find candidate columns (between 'total' and the first 'Percent' column)
        total_idx = None
        for i, h in enumerate(header):
            if h.strip().lower() == 'total':
                total_idx = i
                break
        
        if total_idx is None:
            print(f"    WARNING: No 'total' column in {filepath}")
            return result
        
        # Candidate columns are after 'total' until we hit a 'Percent' column
        cand_cols = []
        for i in range(total_idx + 1, len(header)):
            if 'percent' in header[i].lower():
                break
            cand_cols.append((i, header[i].strip()))
        
        for row in reader:
            if len(row) < total_idx + 1:
                continue
            
            try:
                ward = int(row[1].strip())
                precinct = int(row[2].strip())
            except (ValueError, IndexError):
                continue
            
            pid = normalize_precinct_id(ward, precinct)
            
            try:
                total_votes = int(float(row[total_idx].strip() or '0'))
            except ValueError:
                total_votes = 0
            
            cands = []
            for col_idx, cand_name in cand_cols:
                if col_idx < len(row):
                    try:
                        votes = int(float(row[col_idx].strip() or '0'))
                    except ValueError:
                        votes = 0
                    pct = round(votes / total_votes * 100, 1) if total_votes > 0 else 0
                    cands.append({'n': cand_name, 'v': votes, 'pct': pct})
            
            cands.sort(key=lambda x: x['v'], reverse=True)
            
            result[pid] = {
                'cat': race_category,
                'raw': race_key,
                'total': total_votes,
                'cands': cands
            }
    
    return result


def parse_municipal_2023(precincts_dict, election_key):
    """Parse all 2023 Municipal General data and add to precincts dict."""
    print(f"  Parsing 2023 Municipal General...")
    
    # Mayor
    mayor_path = os.path.join(MUNICIPAL_2023_DIR, 'mayor.csv')
    if os.path.exists(mayor_path):
        mayor_data = parse_archive_csv(mayor_path, 'mayor', 'mayor')
        for pid, race in mayor_data.items():
            if pid not in precincts_dict:
                precincts_dict[pid] = {'reg': 0, 'bal': 0, 'races': {}}
            precincts_dict[pid]['races']['mayor'] = race
        print(f"    Mayor: {len(mayor_data)} precincts")
    
    # Clerk
    clerk_path = os.path.join(MUNICIPAL_2023_DIR, 'clerk.csv')
    if os.path.exists(clerk_path):
        clerk_data = parse_archive_csv(clerk_path, 'clerk', 'clerk')
        for pid, race in clerk_data.items():
            if pid not in precincts_dict:
                precincts_dict[pid] = {'reg': 0, 'bal': 0, 'races': {}}
            precincts_dict[pid]['races']['clerk'] = race
        print(f"    Clerk: {len(clerk_data)} precincts")
    
    # Treasurer
    treasurer_path = os.path.join(MUNICIPAL_2023_DIR, 'treasurer.csv')
    if os.path.exists(treasurer_path):
        treasurer_data = parse_archive_csv(treasurer_path, 'treasurer', 'treasurer')
        for pid, race in treasurer_data.items():
            if pid not in precincts_dict:
                precincts_dict[pid] = {'reg': 0, 'bal': 0, 'races': {}}
            precincts_dict[pid]['races']['treasurer'] = race
        print(f"    Treasurer: {len(treasurer_data)} precincts")
    
    # Alderperson wards 1-50
    ald_count = 0
    for ward_num in range(1, 51):
        ald_path = os.path.join(MUNICIPAL_2023_DIR, f'alderperson_ward_{ward_num}.csv')
        if os.path.exists(ald_path):
            ald_data = parse_archive_csv(ald_path, 'alderman', f'alderman_{ward_num}', ward_num)
            for pid, race in ald_data.items():
                if pid not in precincts_dict:
                    precincts_dict[pid] = {'reg': 0, 'bal': 0, 'races': {}}
                precincts_dict[pid]['races'][f'alderman_{ward_num}'] = race
            ald_count += len(ald_data)
    print(f"    Alderman (50 wards): {ald_count} total precinct-races")
    
    # Turnout data
    turnout_path = os.path.join(MUNICIPAL_2023_DIR, 'turnout.csv')
    if os.path.exists(turnout_path):
        with open(turnout_path, 'r', errors='ignore') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if len(row) < 5:
                    continue
                try:
                    ward = int(row[1].strip())
                    precinct = int(row[2].strip())
                    reg = int(float(row[3].strip() or '0'))
                    bal = int(float(row[4].strip() or '0'))
                except (ValueError, IndexError):
                    continue
                pid = normalize_precinct_id(ward, precinct)
                if pid in precincts_dict:
                    precincts_dict[pid]['reg'] = reg
                    precincts_dict[pid]['bal'] = bal
                    precincts_dict[pid]['to'] = round(bal / reg * 100, 1) if reg > 0 else 0
    
    return precincts_dict


def parse_municipal_2023_runoff(precincts_dict, election_key):
    """Parse 2023 Municipal Runoff data."""
    print(f"  Parsing 2023 Municipal Runoff...")
    
    # Mayor runoff
    mayor_path = os.path.join(MUNICIPAL_2023_RUNOFF_DIR, 'mayor.csv')
    if os.path.exists(mayor_path):
        mayor_data = parse_archive_csv(mayor_path, 'mayor', 'mayor_runoff')
        for pid, race in mayor_data.items():
            if pid not in precincts_dict:
                precincts_dict[pid] = {'reg': 0, 'bal': 0, 'races': {}}
            precincts_dict[pid]['races']['mayor_runoff'] = race
        print(f"    Mayor Runoff: {len(mayor_data)} precincts")
    
    # Alderperson runoffs - map race files to ward numbers
    runoff_ward_map = {
        'race_12': 4, 'race_13': 5, 'race_14': 6, 'race_15': 10,
        'race_16': 11, 'race_17': 21, 'race_18': 24, 'race_19': 29,
        'race_20': 30, 'race_21': 36, 'race_22': 43, 'race_23': 45,
        'race_24': 46, 'race_25': 48,
    }
    
    ald_count = 0
    for race_file, ward_num in runoff_ward_map.items():
        ald_path = os.path.join(MUNICIPAL_2023_RUNOFF_DIR, f'{race_file}.csv')
        if os.path.exists(ald_path):
            ald_data = parse_archive_csv(ald_path, 'alderman', f'alderman_{ward_num}_runoff', ward_num)
            for pid, race in ald_data.items():
                if pid not in precincts_dict:
                    precincts_dict[pid] = {'reg': 0, 'bal': 0, 'races': {}}
                precincts_dict[pid]['races'][f'alderman_{ward_num}_runoff'] = race
            ald_count += len(ald_data)
    print(f"    Alderman Runoffs (14 wards): {ald_count} precinct-races")
    
    # Turnout
    turnout_path = os.path.join(MUNICIPAL_2023_RUNOFF_DIR, 'turnout.csv')
    if os.path.exists(turnout_path):
        with open(turnout_path, 'r', errors='ignore') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if len(row) < 5:
                    continue
                try:
                    ward = int(row[1].strip())
                    precinct = int(row[2].strip())
                    reg = int(float(row[3].strip() or '0'))
                    bal = int(float(row[4].strip() or '0'))
                except (ValueError, IndexError):
                    continue
                pid = normalize_precinct_id(ward, precinct)
                if pid in precincts_dict:
                    precincts_dict[pid]['reg'] = reg
                    precincts_dict[pid]['bal'] = bal
                    precincts_dict[pid]['to'] = round(bal / reg * 100, 1) if reg > 0 else 0
    
    return precincts_dict


def parse_cook_county_2022(precincts_dict):
    """Parse 2022 Cook County data (MWRD, Commissioner) from Chicago Elections Archive."""
    print(f"  Parsing 2022 Cook County (MWRD + Commissioner)...")
    
    # MWRD full term  
    mwrd_path = os.path.join(COOK_COUNTY_2022_DIR, 'mwrd_full.csv')
    if os.path.exists(mwrd_path):
        mwrd_data = parse_archive_csv(mwrd_path, 'mwrd', 'mwrd')
        for pid, race in mwrd_data.items():
            if pid not in precincts_dict:
                precincts_dict[pid] = {'reg': 0, 'bal': 0, 'races': {}}
            precincts_dict[pid]['races']['mwrd'] = race
        print(f"    MWRD (full term): {len(mwrd_data)} precincts")
    
    # MWRD 2-year term
    mwrd2_path = os.path.join(COOK_COUNTY_2022_DIR, 'mwrd_2yr.csv')
    if os.path.exists(mwrd2_path):
        mwrd2_data = parse_archive_csv(mwrd2_path, 'mwrd', 'mwrd_2yr')
        for pid, race in mwrd2_data.items():
            if pid not in precincts_dict:
                precincts_dict[pid] = {'reg': 0, 'bal': 0, 'races': {}}
            precincts_dict[pid]['races']['mwrd_2yr'] = race
        print(f"    MWRD (2yr term): {len(mwrd2_data)} precincts")
    
    # Cook County Board President
    bp_path = os.path.join(COOK_COUNTY_2022_DIR, 'board_president.csv')
    if os.path.exists(bp_path):
        bp_data = parse_archive_csv(bp_path, 'cook_board_president', 'cook_board_president')
        for pid, race in bp_data.items():
            if pid not in precincts_dict:
                precincts_dict[pid] = {'reg': 0, 'bal': 0, 'races': {}}
            precincts_dict[pid]['races']['cook_board_president'] = race
        print(f"    Cook County Board President: {len(bp_data)} precincts")
    
    # Commissioner districts
    # Map race IDs to district numbers
    commissioner_races = {
        94: 1, 95: 2, 96: 3, 97: 4, 98: 5, 99: 7, 100: 8,
        101: 9, 102: 10, 103: 11, 104: 12, 105: 13, 107: 16
    }
    
    comm_count = 0
    for race_id, dist_num in commissioner_races.items():
        comm_path = os.path.join(COOK_COUNTY_2022_DIR, f'commissioner_race_{race_id}.csv')
        if os.path.exists(comm_path):
            comm_data = parse_archive_csv(comm_path, 'commissioner', f'commissioner_{dist_num}', dist_num)
            for pid, race in comm_data.items():
                if pid not in precincts_dict:
                    precincts_dict[pid] = {'reg': 0, 'bal': 0, 'races': {}}
                precincts_dict[pid]['races'][f'commissioner_{dist_num}'] = race
            comm_count += len(comm_data)
    print(f"    Commissioner ({len(commissioner_races)} districts): {comm_count} precinct-races")
    
    return precincts_dict


def build_compact_election(precincts_dict):
    """Convert precincts dict to compact JSON format."""
    compact = {}
    for pid, pdata in precincts_dict.items():
        compact[pid] = {
            'r': pdata.get('reg', 0),
            'b': pdata.get('bal', 0),
            't': pdata.get('to', 0),
            'x': {}
        }
        for rkey, rdata in pdata.get('races', {}).items():
            compact[pid]['x'][rkey] = {
                'c': [[c['n'], c['v'], c['pct']] for c in rdata['cands']],
                't': rdata['total']
            }
    return compact


def build_district_precincts(all_elections):
    """Build district_precincts.json mapping from election data.
    
    Uses ground truth: if a precinct reports votes for a race, it's in that district.
    For split precincts (appearing in multiple districts of same type), assign to the
    district with the most votes across all elections.
    """
    print("\n── Building district-precinct mapping ──")
    
    # Collect all (precinct, district_key, vote_count) across all elections
    precinct_district_votes = defaultdict(lambda: defaultdict(int))
    
    for ekey, edata in all_elections.items():
        for pid, pdata in edata.items():
            for rkey, rdata in pdata.get('races', {}).items():
                total = rdata.get('total', sum(c['v'] for c in rdata.get('cands', [])))
                precinct_district_votes[pid][rkey] += total
    
    # Group race keys by category to detect split precincts
    # Category extraction: 'state_rep_13' → 'state_rep', 'alderman_5' → 'alderman', etc.
    def get_category(rkey):
        # Remove trailing _runoff
        base = re.sub(r'_runoff$', '', rkey)
        # Special cases for judicial
        if base.startswith('circuit_'):
            return 'circuit'
        if base.startswith('subcircuit_'):
            # Extract subcircuit number: subcircuit_5_xxx → subcircuit
            return 'subcircuit'
        if base.startswith('appellate_'):
            return 'appellate'
        if base.startswith('supreme_'):
            return 'supreme'
        if base.startswith('alderman_'):
            return 'alderman'
        if base.startswith('commissioner_'):
            return 'commissioner'
        if base.startswith('mwrd'):
            return 'mwrd'
        # For state_rep_13, state_senate_5, congress_3: category is everything before last _N
        m = re.match(r'^(state_rep|state_senate|congress)_\d+$', base)
        if m:
            return m.group(1)
        # county-wide races
        return base
    
    # Build the mapping
    # For district-based races (state_rep, state_senate, congress, alderman, commissioner, subcircuit):
    # each precinct should be in exactly one district per category
    # For county-wide races (circuit, appellate, supreme, mwrd, mayor, clerk, etc.):
    # all precincts participate
    
    # District-based categories that have numbered districts
    DISTRICT_CATEGORIES = {'state_rep', 'state_senate', 'congress', 'alderman', 'commissioner'}
    
    # For subcircuits, each subcircuit number is its own geographic area
    # But different subcircuit races in the same subcircuit overlap
    # We group by subcircuit number
    
    district_precincts = defaultdict(list)
    
    # 1) Handle district-based categories: resolve split precincts
    for cat in DISTRICT_CATEGORIES:
        # Collect all precincts per district for this category
        precinct_to_districts = defaultdict(lambda: defaultdict(int))  # pid → {district_key: total_votes}
        
        for pid, rkeys in precinct_district_votes.items():
            for rkey, votes in rkeys.items():
                rkey_base = re.sub(r'_runoff$', '', rkey)
                if get_category(rkey) == cat:
                    precinct_to_districts[pid][rkey_base] = max(
                        precinct_to_districts[pid].get(rkey_base, 0),
                        votes
                    )
        
        # Assign each precinct to the district with the most votes
        for pid, districts in precinct_to_districts.items():
            if not districts:
                continue
            best_district = max(districts, key=districts.get)
            district_precincts[best_district].append(pid)
    
    # 2) Handle subcircuits similarly — group by subcircuit number
    subcircuit_precinct_votes = defaultdict(lambda: defaultdict(int))  # pid → {subcircuit_N: total_votes}
    for pid, rkeys in precinct_district_votes.items():
        for rkey, votes in rkeys.items():
            m = re.match(r'subcircuit_(\d+)_', rkey)
            if m:
                sub_num = int(m.group(1))
                subcircuit_precinct_votes[pid][f'subcircuit_{sub_num}'] += votes
    
    for pid, subs in subcircuit_precinct_votes.items():
        if not subs:
            continue
        best_sub = max(subs, key=subs.get)
        district_precincts[best_sub].append(pid)
    
    # 3) County-wide races: all precincts with data
    all_precincts = set()
    for edata in all_elections.values():
        all_precincts.update(edata.keys())
    
    for county_wide_cat in ['circuit', 'appellate', 'supreme', 'mwrd', 'mayor', 'clerk', 
                            'treasurer', 'governor', 'us_senate', 'cook_board_president']:
        district_precincts[county_wide_cat] = sorted(all_precincts)
    
    # Sort precinct lists and deduplicate
    for key in district_precincts:
        district_precincts[key] = sorted(set(district_precincts[key]))
    
    # Report
    print(f"  Total district keys: {len(district_precincts)}")
    for cat in ['state_rep', 'state_senate', 'congress', 'alderman', 'commissioner', 'subcircuit']:
        keys = [k for k in district_precincts if get_category(k) == cat or k.startswith(cat)]
        total_p = sum(len(v) for k, v in district_precincts.items() if k in keys)
        print(f"    {cat}: {len(keys)} districts, {total_p} precinct assignments")
    
    return dict(district_precincts)


def build_meta(all_elections, district_precincts):
    """Build metadata JSON."""
    meta = {
        'generated': datetime.datetime.now().isoformat(),
        'elections': {},
        'district_types': [],
        'chicago_precinct_count': 1291,
    }
    
    # Categorize district types for the UI
    district_types = set()
    for key in district_precincts:
        if key.startswith('state_rep_'):
            district_types.add('state_rep')
        elif key.startswith('state_senate_'):
            district_types.add('state_senate')
        elif key.startswith('congress_'):
            district_types.add('congress')
        elif key.startswith('alderman_'):
            district_types.add('alderman')
        elif key.startswith('commissioner_'):
            district_types.add('commissioner')
        elif key.startswith('subcircuit_'):
            district_types.add('subcircuit')
        elif key in ('circuit', 'appellate', 'supreme', 'mwrd', 'mayor', 'clerk', 
                     'treasurer', 'governor', 'us_senate', 'cook_board_president'):
            district_types.add(key)
    
    meta['district_types'] = sorted(district_types)
    
    for ekey, edata in all_elections.items():
        races_found = defaultdict(set)
        for pid, pdata in edata.items():
            for rkey in pdata.get('races', {}):
                # Categorize
                if rkey.startswith('circuit_'):
                    races_found['circuit'].add(rkey)
                elif rkey.startswith('subcircuit_'):
                    races_found['subcircuit'].add(rkey)
                elif rkey.startswith('appellate_'):
                    races_found['appellate'].add(rkey)
                elif rkey.startswith('supreme_'):
                    races_found['supreme'].add(rkey)
                elif rkey.startswith('alderman_'):
                    races_found['alderman'].add(rkey)
                elif rkey.startswith('commissioner_'):
                    races_found['commissioner'].add(rkey)
                elif rkey.startswith('state_rep_'):
                    races_found['state_rep'].add(rkey)
                elif rkey.startswith('state_senate_'):
                    races_found['state_senate'].add(rkey)
                elif rkey.startswith('congress_'):
                    races_found['congress'].add(rkey)
                else:
                    races_found[rkey].add(rkey)
        
        meta['elections'][ekey] = {
            'precinct_count': len(edata),
            'races': {cat: sorted(list(keys)) for cat, keys in races_found.items()}
        }
    
    return meta


def main():
    print("=" * 60)
    print("D4D Heatmap Platform — Data Pipeline v3")
    print("=" * 60)
    
    all_elections = {}
    
    # ── Step 1: Parse SBOE data (state/federal races + judicial) ──
    print("\n── Step 1: Parse SBOE election data ──")
    for ekey, filepath in SBOE_CSVS.items():
        if os.path.exists(filepath):
            all_elections[ekey] = parse_sboe_csv(filepath, ekey)
    
    # ── Step 2: Parse 2023 Municipal General ──
    print("\n── Step 2: Parse 2023 Municipal General ──")
    muni_2023 = {}
    parse_municipal_2023(muni_2023, '2023_municipal')
    # Compute turnout for precincts that have it
    for pid, p in muni_2023.items():
        if p['reg'] > 0:
            p['to'] = round(p['bal'] / p['reg'] * 100, 1)
    all_elections['2023_municipal'] = muni_2023
    print(f"    → Total: {len(muni_2023)} precincts")
    
    # ── Step 3: Parse 2023 Municipal Runoff ──
    print("\n── Step 3: Parse 2023 Municipal Runoff ──")
    muni_2023_runoff = {}
    parse_municipal_2023_runoff(muni_2023_runoff, '2023_municipal_runoff')
    for pid, p in muni_2023_runoff.items():
        if p['reg'] > 0:
            p['to'] = round(p['bal'] / p['reg'] * 100, 1)
    all_elections['2023_municipal_runoff'] = muni_2023_runoff
    print(f"    → Total: {len(muni_2023_runoff)} precincts")
    
    # ── Step 4: Parse 2022 Cook County (MWRD, Commissioner) ──
    # These are from the same 2022 General election, so merge into that election
    print("\n── Step 4: Merge 2022 Cook County data into 2022 General ──")
    if '2022_general' in all_elections:
        parse_cook_county_2022(all_elections['2022_general'])
    
    # ── Step 5: Build district-precinct mapping ──
    district_precincts = build_district_precincts(all_elections)
    
    dp_path = os.path.join(DATA_DIR, 'district_precincts.json')
    with open(dp_path, 'w') as f:
        json.dump(district_precincts, f, separators=(',', ':'))
    print(f"  Saved: {dp_path} ({os.path.getsize(dp_path)/1024:.0f} KB)")
    
    # Also build reverse mapping (precinct → districts)
    precinct_districts = defaultdict(dict)
    for dkey, pids in district_precincts.items():
        # Determine category
        for cat_prefix in ['state_rep_', 'state_senate_', 'congress_', 'alderman_', 
                           'commissioner_', 'subcircuit_']:
            if dkey.startswith(cat_prefix):
                cat = cat_prefix.rstrip('_')
                for pid in pids:
                    precinct_districts[pid][cat] = dkey
                break
    
    pd_path = os.path.join(DATA_DIR, 'precinct_districts.json')
    with open(pd_path, 'w') as f:
        json.dump(dict(precinct_districts), f, separators=(',', ':'))
    print(f"  Saved: {pd_path} ({os.path.getsize(pd_path)/1024:.0f} KB)")
    
    # ── Step 6: Build compact election data files ──
    print("\n── Step 6: Build compact election data ──")
    for ekey, edata in all_elections.items():
        compact = build_compact_election(edata)
        elec_path = os.path.join(DATA_DIR, f'election_{ekey}.json')
        with open(elec_path, 'w') as f:
            json.dump(compact, f, separators=(',', ':'))
        
        # Count races by category
        cats = defaultdict(int)
        for p in edata.values():
            for rkey in p.get('races', {}):
                if rkey.startswith('circuit_'): cats['circuit'] += 1
                elif rkey.startswith('subcircuit_'): cats['subcircuit'] += 1
                elif rkey.startswith('appellate_'): cats['appellate'] += 1
                elif rkey.startswith('supreme_'): cats['supreme'] += 1
                elif rkey.startswith('alderman_'): cats['alderman'] += 1
                elif rkey.startswith('commissioner_'): cats['commissioner'] += 1
                elif rkey.startswith('state_rep_'): cats['state_rep'] += 1
                elif rkey.startswith('state_senate_'): cats['state_senate'] += 1
                elif rkey.startswith('congress_'): cats['congress'] += 1
                else: cats[rkey] += 1
        
        print(f"  {ekey}: {os.path.getsize(elec_path)/1024:.0f} KB, {len(edata)} precincts")
        print(f"    Races: {dict(cats)}")
    
    # ── Step 7: Build metadata ──
    print("\n── Step 7: Build metadata ──")
    meta = build_meta(all_elections, district_precincts)
    meta_path = os.path.join(DATA_DIR, 'meta.json')
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)
    print(f"  Saved: {meta_path}")
    print(f"  District types: {meta['district_types']}")
    print(f"  Elections: {list(meta['elections'].keys())}")
    
    print(f"\n{'=' * 60}")
    print("Pipeline v3 complete.")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
