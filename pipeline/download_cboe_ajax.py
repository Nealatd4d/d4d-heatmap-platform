#!/usr/bin/env python3
"""
Download ALL CBOE 2026 Primary results via AJAX endpoint.
Parses the HTML tables (with <h3>Ward N</h3> headers) correctly.

Saves each contest to /tmp/cboe_parsed/contest_{election_id}_{contest_id}.json
and a combined CSV at /tmp/cboe_parsed/cboe_2026_all.csv
"""

import json
import os
import re
import sys
import time
import csv
import requests
from html import unescape

OUTPUT_DIR = '/tmp/cboe_parsed'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def parse_ajax_html(html_data, contest_name):
    """Parse CBOE AJAX HTML response into precinct-level results.
    
    HTML structure:
    - Summary table with totals
    - <h3>Ward N</h3> followed by per-ward table
    - Ward tables: Precinct | Total Voters | Candidate1 | % | Candidate2 | % | ...
    """
    html = unescape(html_data)
    results = []
    
    # Extract candidate names from the FIRST table's <thead>
    first_table = re.search(r'<thead>(.*?)</thead>', html, re.DOTALL)
    if not first_table:
        return results
    
    th_matches = re.findall(r'<th>(.*?)</th>', first_table.group(1), re.DOTALL)
    candidates = []
    for th in th_matches:
        name = th.strip()
        if name and name not in ('Total Votes', '%', 'Precinct', 'Total Voters'):
            candidates.append(name)
    
    if not candidates:
        return results
    
    # Split by ward headers: <h3>Ward N</h3>
    ward_sections = re.split(r'<h3>Ward\s+(\d+)</h3>', html)
    
    # ward_sections[0] = summary stuff before first ward
    # ward_sections[1] = ward number, ward_sections[2] = ward html
    # ward_sections[3] = ward number, ward_sections[4] = ward html, etc.
    
    for i in range(1, len(ward_sections), 2):
        if i+1 >= len(ward_sections):
            break
        
        ward_num = int(ward_sections[i])
        ward_html = ward_sections[i+1]
        
        # Find all data rows in <tbody>
        tbody = re.search(r'<tbody>(.*?)</tbody>', ward_html, re.DOTALL)
        if not tbody:
            continue
        
        # Extract each <tr> row
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody.group(1), re.DOTALL)
        
        for row_html in rows:
            tds = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
            if not tds:
                continue
            
            # First td = precinct number
            precinct_str = tds[0].strip()
            if not re.match(r'^\d+$', precinct_str):
                continue  # Skip total/footer rows
            
            precinct = int(precinct_str)
            total_voters_str = tds[1].replace(',', '').strip() if len(tds) > 1 else '0'
            total_voters = int(total_voters_str) if total_voters_str.isdigit() else 0
            
            # Parse candidate votes: tds[2]=cand1_votes, tds[3]=pct1, tds[4]=cand2_votes, ...
            for ci, cand_name in enumerate(candidates):
                vote_idx = 2 + ci * 2
                if vote_idx < len(tds):
                    votes_str = tds[vote_idx].replace(',', '').strip()
                    votes = int(votes_str) if votes_str.isdigit() else 0
                else:
                    votes = 0
                
                results.append({
                    'ward': ward_num,
                    'precinct': precinct,
                    'candidate': cand_name,
                    'votes': votes,
                    'total_voters': total_voters,
                })
    
    return results


def parse_turnout_html(html_data):
    """Parse turnout HTML (different structure)."""
    html = unescape(html_data)
    results = []
    
    ward_sections = re.split(r'<h3>Ward\s+(\d+)</h3>', html)
    
    for i in range(1, len(ward_sections), 2):
        if i+1 >= len(ward_sections):
            break
        
        ward_num = int(ward_sections[i])
        ward_html = ward_sections[i+1]
        
        tbody = re.search(r'<tbody>(.*?)</tbody>', ward_html, re.DOTALL)
        if not tbody:
            continue
        
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody.group(1), re.DOTALL)
        
        for row_html in rows:
            tds = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
            if not tds or not re.match(r'^\d+$', tds[0].strip()):
                continue
            
            precinct = int(tds[0].strip())
            reg_str = tds[1].replace(',', '').strip() if len(tds) > 1 else '0'
            cast_str = tds[2].replace(',', '').strip() if len(tds) > 2 else '0'
            
            results.append({
                'ward': ward_num,
                'precinct': precinct,
                'registered_voters': int(reg_str) if reg_str.isdigit() else 0,
                'ballots_cast': int(cast_str) if cast_str.isdigit() else 0,
            })
    
    return results


def fetch_contest(session, election_id, contest_id, form_build_id):
    """Fetch one contest via AJAX. Returns (html, new_form_build_id)."""
    data = {
        'election_id': str(election_id),
        'contest': str(contest_id),
        'ward': '',
        'precinct': '',
        'form_build_id': form_build_id,
        'form_id': 'election_results_form',
        '_triggering_element_name': 'submit',
        '_triggering_element_value': 'Submit',
    }
    
    resp = session.post(
        f'https://chicagoelections.gov/elections/results/{election_id}?ajax_form=1',
        data=data,
        headers={
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        },
        timeout=60,
    )
    
    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}")
    
    ajax_json = resp.json()
    new_fbid = form_build_id
    html_data = ''
    
    for cmd in ajax_json:
        if cmd.get('command') == 'update_build_id':
            new_fbid = cmd.get('new', form_build_id)
        elif cmd.get('command') == 'openDialog':
            html_data = cmd.get('data', '')
    
    return html_data, new_fbid


def download_election(election_id, contests, party_label):
    """Download all contests for one election (DEM or REP)."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    })
    
    print(f"\n{'='*60}")
    print(f"Downloading {party_label} (election_id={election_id}): {len(contests)} contests")
    print(f"{'='*60}")
    
    # Get initial page + form_build_id
    resp = session.get(f'https://chicagoelections.gov/elections/results/{election_id}')
    fbid = re.search(r'name="form_build_id"\s+value="([^"]+)"', resp.text)
    if not fbid:
        print("ERROR: Could not get form_build_id")
        return []
    form_build_id = fbid.group(1)
    
    all_results = []
    success = 0
    empty = 0
    fail = 0
    
    for contest_id, contest_name in sorted(contests.items()):
        cache_file = os.path.join(OUTPUT_DIR, f'contest_{election_id}_{contest_id}.json')
        
        # Check cache
        if os.path.exists(cache_file):
            with open(cache_file) as f:
                cached = json.load(f)
            if cached.get('results'):
                all_results.extend(cached['results'])
                success += 1
                n = len(cached['results'])
                print(f"  [CACHE] {contest_id}: {contest_name} ({n} rows)")
                continue
            elif cached.get('empty'):
                empty += 1
                continue
        
        try:
            html_data, form_build_id = fetch_contest(
                session, election_id, contest_id, form_build_id
            )
            
            if not html_data or '<table' not in html_data:
                # Save as empty
                with open(cache_file, 'w') as f:
                    json.dump({'empty': True, 'contest_name': contest_name}, f)
                empty += 1
                print(f"  [EMPTY] {contest_id}: {contest_name}")
                time.sleep(0.3)
                continue
            
            # Check if turnout
            is_turnout = 'Registered Voters' in html_data and 'Ballots Cast' in html_data
            
            if is_turnout:
                parsed = parse_turnout_html(html_data)
                record_type = 'turnout'
            else:
                parsed = parse_ajax_html(html_data, contest_name)
                record_type = 'results'
            
            # Add metadata
            for row in parsed:
                row['contest_id'] = contest_id
                row['contest_name'] = contest_name
                row['election_id'] = election_id
                row['party'] = party_label
                row['record_type'] = record_type
            
            # Cache
            with open(cache_file, 'w') as f:
                json.dump({
                    'contest_name': contest_name,
                    'record_type': record_type,
                    'results': parsed,
                    'count': len(parsed),
                }, f)
            
            all_results.extend(parsed)
            success += 1
            
            precincts = len(set((r.get('ward'), r.get('precinct')) for r in parsed))
            print(f"  [OK] {contest_id}: {contest_name} -> {len(parsed)} rows, {precincts} precincts")
            
            time.sleep(0.3)
            
        except Exception as e:
            fail += 1
            print(f"  [FAIL] {contest_id}: {contest_name} -> {e}")
            time.sleep(2)
    
    print(f"\n{party_label} Summary: {success} OK, {empty} empty, {fail} fail, {len(all_results)} total rows")
    return all_results


# Contest mappings
DEM_CONTESTS = {
    11: "Senator, U.S. - DEM",
    12: "Governor & Lieutenant Governor, Illinois - DEM",
    13: "Attorney General, State of Illinois - DEM",
    14: "Secretary of State, State of Illinois - DEM",
    15: "Comptroller, State of Illinois - DEM",
    16: "Treasurer, State of Illinois - DEM",
    17: "U.S. Representative, 1st District - DEM",
    18: "U.S. Representative, 2nd District - DEM",
    19: "U.S. Representative, 3rd District - DEM",
    20: "U.S. Representative, 4th District - DEM",
    21: "U.S. Representative, 5th District - DEM",
    22: "U.S. Representative, 6th District - DEM",
    23: "U.S. Representative, 7th District - DEM",
    24: "U.S. Representative, 8th District - DEM",
    25: "U.S. Representative, 9th District - DEM",
    26: "Committeeperson, Dem State Central, 1st - DEM",
    27: "Committeeperson, Dem State Central, 2nd - DEM",
    28: "Committeeperson, Dem State Central, 3rd - DEM",
    29: "Committeeperson, Dem State Central, 4th - DEM",
    30: "Committeeperson, Dem State Central, 5th - DEM",
    31: "Committeeperson, Dem State Central, 6th - DEM",
    32: "Committeeperson, Dem State Central, 7th - DEM",
    33: "Committeeperson, Dem State Central, 8th - DEM",
    34: "Committeeperson, Dem State Central, 9th - DEM",
    35: "State Senator, 2nd District - DEM",
    36: "State Senator, 3rd District - DEM",
    37: "State Senator, 5th District - DEM",
    38: "State Senator, 6th District - DEM",
    39: "State Senator, 8th District - DEM",
    40: "State Senator, 9th District - DEM",
    41: "State Senator, 11th District - DEM",
    42: "State Senator, 12th District - DEM",
    43: "State Senator, 14th District - DEM",
    44: "State Senator, 15th District - DEM",
    45: "State Senator, 17th District - DEM",
    46: "State Senator, 18th District - DEM",
    47: "State Senator, 20th District - DEM",
    48: "State Senator, 39th District - DEM",
    49: "State Representative, 1st District - DEM",
    50: "State Representative, 3rd District - DEM",
    51: "State Representative, 4th District - DEM",
    52: "State Representative, 5th District - DEM",
    53: "State Representative, 6th District - DEM",
    54: "State Representative, 8th District - DEM",
    55: "State Representative, 9th District - DEM",
    56: "State Representative, 10th District - DEM",
    57: "State Representative, 11th District - DEM",
    58: "State Representative, 12th District - DEM",
    59: "State Representative, 13th District - DEM",
    60: "State Representative, 14th District - DEM",
    61: "State Representative, 15th District - DEM",
    62: "State Representative, 16th District - DEM",
    63: "State Representative, 18th District - DEM",
    64: "State Representative, 19th District - DEM",
    65: "State Representative, 20th District - DEM",
    66: "State Representative, 21st District - DEM",
    67: "State Representative, 22nd District - DEM",
    68: "State Representative, 23rd District - DEM",
    69: "State Representative, 24th District - DEM",
    70: "State Representative, 25th District - DEM",
    71: "State Representative, 26th District - DEM",
    72: "State Representative, 27th District - DEM",
    73: "State Representative, 28th District - DEM",
    74: "State Representative, 29th District - DEM",
    75: "State Representative, 31st District - DEM",
    76: "State Representative, 32nd District - DEM",
    77: "State Representative, 33rd District - DEM",
    78: "State Representative, 34th District - DEM",
    79: "State Representative, 35th District - DEM",
    80: "State Representative, 36th District - DEM",
    81: "State Representative, 39th District - DEM",
    82: "State Representative, 40th District - DEM",
    83: "State Representative, 55th District - DEM",
    84: "State Representative, 78th District - DEM",
    85: "Commissioner, Water Reclamation Dist - DEM",
    86: "Commissioner, Water Reclamation Dist 2 yr - DEM",
    87: "Board President, Cook County - DEM",
    88: "Clerk, Cook County - DEM",
    89: "Sheriff, Cook County - DEM",
    90: "Treasurer, Cook County - DEM",
    91: "Assessor, Cook County - DEM",
    92: "Commissioner, County Board 1st District - DEM",
    93: "Commissioner, County Board 2nd District - DEM",
    94: "Commissioner, County Board 3rd District - DEM",
    95: "Commissioner, County Board 4th District - DEM",
    96: "Commissioner, County Board 5th District - DEM",
    97: "Commissioner, County Board 7th District - DEM",
    98: "Commissioner, County Board 8th District - DEM",
    99: "Commissioner, County Board 9th District - DEM",
    100: "Commissioner, County Board 10th District - DEM",
    101: "Commissioner, County Board 11th District - DEM",
    102: "Commissioner, County Board 12th District - DEM",
    103: "Commissioner, County Board 13th District - DEM",
    104: "Commissioner, County Board 16th District - DEM",
    105: "Board of Review, 1st District - DEM",
    106: "Board of Review, 2nd District - DEM",
    107: "Appellate Court Judge (Vacancy of Hoffman) - DEM",
    108: "Circuit Court Judge (Vacancy of Burke) - DEM",
    109: "Circuit Court Judge (Vacancy of Cobbs) - DEM",
    110: "Circuit Court Judge (Vacancy of Coghlan) - DEM",
    111: "Circuit Court Judge (Vacancy of Hooks) - DEM",
    112: "Circuit Court Judge (Vacancy of Karkula) - DEM",
    113: "Judge, 1st Subcircuit (Vacancy of Balanoff) - DEM",
    114: "Judge, 1st Subcircuit (Vacancy of Walker) - DEM",
    115: "Judge, 3rd Subcircuit (Vacancy of Murphy) - DEM",
    116: "Judge, 3rd Subcircuit (Vacancy of Sherlock) - DEM",
    117: "Judge, 5th Subcircuit (Vacancy of Ross) - DEM",
    118: "Judge, 8th Subcircuit (Vacancy of Gamrath) - DEM",
    119: "Judge, 8th Subcircuit (Vacancy of Mikva) - DEM",
    120: "Judge, 11th Subcircuit (Vacancy of McLean Meyerson) - DEM",
    121: "Judge, 11th Subcircuit (Vacancy of Roberts) - DEM",
    122: "Judge, 16th Subcircuit (Vacancy of Baird) - DEM",
    123: "Judge, 16th Subcircuit (Vacancy of Mendoza) - DEM",
    124: "Judge, 17th Subcircuit (Vacancy of Brooks) - DEM",
    125: "Judge, 17th Subcircuit (Vacancy of Carroll) - DEM",
    126: "Judge, 19th Subcircuit (Vacancy of Fairman) - DEM",
    127: "Judge, 19th Subcircuit (Vacancy of Kane) - DEM",
    128: "Judge, 20th Subcircuit (Vacancy of Haracz) - DEM",
    129: "Judge, 20th Subcircuit (Vacancy of Miller) - DEM",
}

REP_CONTESTS = {
    130: "Senator, U.S. - REP", 131: "Governor & Lieutenant Governor, Illinois - REP",
    132: "Attorney General, State of Illinois - REP", 133: "Secretary of State, State of Illinois - REP",
    134: "Comptroller, State of Illinois - REP", 135: "Treasurer, State of Illinois - REP",
    136: "U.S. Representative, 1st District - REP", 137: "U.S. Representative, 2nd District - REP",
    138: "U.S. Representative, 3rd District - REP", 139: "U.S. Representative, 4th District - REP",
    140: "U.S. Representative, 5th District - REP", 141: "U.S. Representative, 6th District - REP",
    142: "U.S. Representative, 7th District - REP", 143: "U.S. Representative, 8th District - REP",
    144: "U.S. Representative, 9th District - REP",
    145: "State Senator, 2nd District - REP", 146: "State Senator, 3rd District - REP",
    147: "State Senator, 5th District - REP", 148: "State Senator, 6th District - REP",
    149: "State Senator, 8th District - REP", 150: "State Senator, 9th District - REP",
    151: "State Senator, 11th District - REP", 152: "State Senator, 12th District - REP",
    153: "State Senator, 14th District - REP", 154: "State Senator, 15th District - REP",
    155: "State Senator, 17th District - REP", 156: "State Senator, 18th District - REP",
    157: "State Senator, 20th District - REP", 158: "State Senator, 39th District - REP",
    159: "State Representative, 1st District - REP", 160: "State Representative, 3rd District - REP",
    161: "State Representative, 4th District - REP", 162: "State Representative, 5th District - REP",
    163: "State Representative, 6th District - REP", 164: "State Representative, 8th District - REP",
    165: "State Representative, 9th District - REP", 166: "State Representative, 10th District - REP",
    167: "State Representative, 11th District - REP", 168: "State Representative, 12th District - REP",
    169: "State Representative, 13th District - REP", 170: "State Representative, 14th District - REP",
    171: "State Representative, 15th District - REP", 172: "State Representative, 16th District - REP",
    173: "State Representative, 18th District - REP", 174: "State Representative, 19th District - REP",
    175: "State Representative, 20th District - REP", 176: "State Representative, 21st District - REP",
    177: "State Representative, 22nd District - REP", 178: "State Representative, 23rd District - REP",
    179: "State Representative, 24th District - REP", 180: "State Representative, 25th District - REP",
    181: "State Representative, 26th District - REP", 182: "State Representative, 27th District - REP",
    183: "State Representative, 28th District - REP", 184: "State Representative, 29th District - REP",
    185: "State Representative, 31st District - REP", 186: "State Representative, 32nd District - REP",
    187: "State Representative, 33rd District - REP", 188: "State Representative, 34th District - REP",
    189: "State Representative, 35th District - REP", 190: "State Representative, 36th District - REP",
    191: "State Representative, 39th District - REP", 192: "State Representative, 40th District - REP",
    193: "State Representative, 55th District - REP", 194: "State Representative, 78th District - REP",
    195: "Commissioner, Water Reclamation Dist - REP", 196: "Commissioner, Water Reclamation Dist 2 yr - REP",
    197: "Board President, Cook County - REP", 198: "Clerk, Cook County - REP",
    199: "Sheriff, Cook County - REP", 200: "Treasurer, Cook County - REP",
    201: "Assessor, Cook County - REP",
    202: "Commissioner, County Board 1st District - REP", 203: "Commissioner, County Board 2nd District - REP",
    204: "Commissioner, County Board 3rd District - REP", 205: "Commissioner, County Board 4th District - REP",
    206: "Commissioner, County Board 5th District - REP", 207: "Commissioner, County Board 7th District - REP",
    208: "Commissioner, County Board 8th District - REP", 209: "Commissioner, County Board 9th District - REP",
    210: "Commissioner, County Board 10th District - REP", 211: "Commissioner, County Board 11th District - REP",
    212: "Commissioner, County Board 12th District - REP", 213: "Commissioner, County Board 13th District - REP",
    214: "Commissioner, County Board 16th District - REP",
    215: "Board of Review, 1st District - REP", 216: "Board of Review, 2nd District - REP",
    217: "Appellate Court Judge (Vacancy of Hoffman) - REP",
    218: "Circuit Court Judge (Vacancy of Burke) - REP", 219: "Circuit Court Judge (Vacancy of Cobbs) - REP",
    220: "Circuit Court Judge (Vacancy of Coghlan) - REP", 221: "Circuit Court Judge (Vacancy of Hooks) - REP",
    222: "Circuit Court Judge (Vacancy of Karkula) - REP",
    223: "Judge, 1st Subcircuit (Vacancy of Balanoff) - REP", 224: "Judge, 1st Subcircuit (Vacancy of Walker) - REP",
    225: "Judge, 3rd Subcircuit (Vacancy of Murphy) - REP", 226: "Judge, 3rd Subcircuit (Vacancy of Sherlock) - REP",
    227: "Judge, 5th Subcircuit (Vacancy of Ross) - REP",
    228: "Judge, 8th Subcircuit (Vacancy of Gamrath) - REP", 229: "Judge, 8th Subcircuit (Vacancy of Mikva) - REP",
    230: "Judge, 11th Subcircuit (Vacancy of McLean Meyerson) - REP", 231: "Judge, 11th Subcircuit (Vacancy of Roberts) - REP",
    232: "Judge, 16th Subcircuit (Vacancy of Baird) - REP", 233: "Judge, 16th Subcircuit (Vacancy of Mendoza) - REP",
    234: "Judge, 17th Subcircuit (Vacancy of Brooks) - REP", 235: "Judge, 17th Subcircuit (Vacancy of Carroll) - REP",
    236: "Judge, 19th Subcircuit (Vacancy of Fairman) - REP", 237: "Judge, 19th Subcircuit (Vacancy of Kane) - REP",
    238: "Judge, 20th Subcircuit (Vacancy of Haracz) - REP", 239: "Judge, 20th Subcircuit (Vacancy of Miller) - REP",
}

# Turnout is a special "contest" with empty value
TURNOUT_ID = ''  # empty string for turnout


def download_turnout(session, election_id, form_build_id):
    """Download turnout data (contest=empty)."""
    cache_file = os.path.join(OUTPUT_DIR, f'turnout_{election_id}.json')
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            cached = json.load(f)
        if cached.get('results'):
            print(f"  [CACHE] Turnout: {len(cached['results'])} rows")
            return cached['results'], form_build_id
    
    data = {
        'election_id': str(election_id),
        'contest': '',
        'ward': '',
        'precinct': '',
        'form_build_id': form_build_id,
        'form_id': 'election_results_form',
        '_triggering_element_name': 'submit',
        '_triggering_element_value': 'Submit',
    }
    
    resp = session.post(
        f'https://chicagoelections.gov/elections/results/{election_id}?ajax_form=1',
        data=data,
        headers={
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        },
        timeout=60,
    )
    
    ajax = resp.json()
    new_fbid = form_build_id
    html_data = ''
    
    for cmd in ajax:
        if cmd.get('command') == 'update_build_id':
            new_fbid = cmd.get('new', form_build_id)
        elif cmd.get('command') == 'openDialog':
            html_data = cmd.get('data', '')
    
    if html_data:
        parsed = parse_turnout_html(html_data)
        with open(cache_file, 'w') as f:
            json.dump({'results': parsed, 'count': len(parsed)}, f)
        print(f"  [OK] Turnout: {len(parsed)} rows")
        return parsed, new_fbid
    else:
        print(f"  [EMPTY] Turnout")
        return [], new_fbid


if __name__ == '__main__':
    # Download DEM
    print("CBOE 2026 Primary - Full Download via AJAX")
    print("=" * 60)
    
    dem_results = download_election(76, DEM_CONTESTS, 'DEM')
    
    # Download REP
    rep_results = download_election(77, REP_CONTESTS, 'REP')
    
    # Combine
    all_results = dem_results + rep_results
    
    # Save combined CSV
    if all_results:
        outfile = os.path.join(OUTPUT_DIR, 'cboe_2026_all.csv')
        fieldnames = ['election_id', 'party', 'contest_id', 'contest_name',
                      'ward', 'precinct', 'candidate', 'votes', 'total_voters', 'record_type']
        with open(outfile, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nCombined CSV: {len(all_results)} rows -> {outfile}")
    
    # Summary
    parties = {}
    for r in all_results:
        p = r.get('party', 'UNK')
        parties[p] = parties.get(p, 0) + 1
    print(f"\nBy party: {parties}")
    
    print("\nDone!")
