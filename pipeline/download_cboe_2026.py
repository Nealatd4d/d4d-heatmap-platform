#!/usr/bin/env python3
"""
Download all Chicago Board of Election Commissioners (CBOE) 2026 Primary results
via AJAX endpoint, parse HTML tables, and save as CSV files.

Election IDs:
  76 = DEM (contests 11-129)
  77 = REP (contests 130-239)
  
Turnout is contest_id=10 on election_id=76
"""

import csv
import json
import os
import re
import sys
import time
import requests
from html import unescape

OUTPUT_DIR = '/tmp/cboe_all_csv'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# CBOE contest mapping
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
    130: "Senator, U.S. - REP",
    131: "Governor & Lieutenant Governor, Illinois - REP",
    132: "Attorney General, State of Illinois - REP",
    133: "Secretary of State, State of Illinois - REP",
    134: "Comptroller, State of Illinois - REP",
    135: "Treasurer, State of Illinois - REP",
    136: "U.S. Representative, 1st District - REP",
    137: "U.S. Representative, 2nd District - REP",
    138: "U.S. Representative, 3rd District - REP",
    139: "U.S. Representative, 4th District - REP",
    140: "U.S. Representative, 5th District - REP",
    141: "U.S. Representative, 6th District - REP",
    142: "U.S. Representative, 7th District - REP",
    143: "U.S. Representative, 8th District - REP",
    144: "U.S. Representative, 9th District - REP",
    145: "State Senator, 2nd District - REP",
    146: "State Senator, 3rd District - REP",
    147: "State Senator, 5th District - REP",
    148: "State Senator, 6th District - REP",
    149: "State Senator, 8th District - REP",
    150: "State Senator, 9th District - REP",
    151: "State Senator, 11th District - REP",
    152: "State Senator, 12th District - REP",
    153: "State Senator, 14th District - REP",
    154: "State Senator, 15th District - REP",
    155: "State Senator, 17th District - REP",
    156: "State Senator, 18th District - REP",
    157: "State Senator, 20th District - REP",
    158: "State Senator, 39th District - REP",
    159: "State Representative, 1st District - REP",
    160: "State Representative, 3rd District - REP",
    161: "State Representative, 4th District - REP",
    162: "State Representative, 5th District - REP",
    163: "State Representative, 6th District - REP",
    164: "State Representative, 8th District - REP",
    165: "State Representative, 9th District - REP",
    166: "State Representative, 10th District - REP",
    167: "State Representative, 11th District - REP",
    168: "State Representative, 12th District - REP",
    169: "State Representative, 13th District - REP",
    170: "State Representative, 14th District - REP",
    171: "State Representative, 15th District - REP",
    172: "State Representative, 16th District - REP",
    173: "State Representative, 18th District - REP",
    174: "State Representative, 19th District - REP",
    175: "State Representative, 20th District - REP",
    176: "State Representative, 21st District - REP",
    177: "State Representative, 22nd District - REP",
    178: "State Representative, 23rd District - REP",
    179: "State Representative, 24th District - REP",
    180: "State Representative, 25th District - REP",
    181: "State Representative, 26th District - REP",
    182: "State Representative, 27th District - REP",
    183: "State Representative, 28th District - REP",
    184: "State Representative, 29th District - REP",
    185: "State Representative, 31st District - REP",
    186: "State Representative, 32nd District - REP",
    187: "State Representative, 33rd District - REP",
    188: "State Representative, 34th District - REP",
    189: "State Representative, 35th District - REP",
    190: "State Representative, 36th District - REP",
    191: "State Representative, 39th District - REP",
    192: "State Representative, 40th District - REP",
    193: "State Representative, 55th District - REP",
    194: "State Representative, 78th District - REP",
    195: "Commissioner, Water Reclamation Dist - REP",
    196: "Commissioner, Water Reclamation Dist 2 yr - REP",
    197: "Board President, Cook County - REP",
    198: "Clerk, Cook County - REP",
    199: "Sheriff, Cook County - REP",
    200: "Treasurer, Cook County - REP",
    201: "Assessor, Cook County - REP",
    202: "Commissioner, County Board 1st District - REP",
    203: "Commissioner, County Board 2nd District - REP",
    204: "Commissioner, County Board 3rd District - REP",
    205: "Commissioner, County Board 4th District - REP",
    206: "Commissioner, County Board 5th District - REP",
    207: "Commissioner, County Board 7th District - REP",
    208: "Commissioner, County Board 8th District - REP",
    209: "Commissioner, County Board 9th District - REP",
    210: "Commissioner, County Board 10th District - REP",
    211: "Commissioner, County Board 11th District - REP",
    212: "Commissioner, County Board 12th District - REP",
    213: "Commissioner, County Board 13th District - REP",
    214: "Commissioner, County Board 16th District - REP",
    215: "Board of Review, 1st District - REP",
    216: "Board of Review, 2nd District - REP",
    217: "Appellate Court Judge (Vacancy of Hoffman) - REP",
    218: "Circuit Court Judge (Vacancy of Burke) - REP",
    219: "Circuit Court Judge (Vacancy of Cobbs) - REP",
    220: "Circuit Court Judge (Vacancy of Coghlan) - REP",
    221: "Circuit Court Judge (Vacancy of Hooks) - REP",
    222: "Circuit Court Judge (Vacancy of Karkula) - REP",
    223: "Judge, 1st Subcircuit (Vacancy of Balanoff) - REP",
    224: "Judge, 1st Subcircuit (Vacancy of Walker) - REP",
    225: "Judge, 3rd Subcircuit (Vacancy of Murphy) - REP",
    226: "Judge, 3rd Subcircuit (Vacancy of Sherlock) - REP",
    227: "Judge, 5th Subcircuit (Vacancy of Ross) - REP",
    228: "Judge, 8th Subcircuit (Vacancy of Gamrath) - REP",
    229: "Judge, 8th Subcircuit (Vacancy of Mikva) - REP",
    230: "Judge, 11th Subcircuit (Vacancy of McLean Meyerson) - REP",
    231: "Judge, 11th Subcircuit (Vacancy of Roberts) - REP",
    232: "Judge, 16th Subcircuit (Vacancy of Baird) - REP",
    233: "Judge, 16th Subcircuit (Vacancy of Mendoza) - REP",
    234: "Judge, 17th Subcircuit (Vacancy of Brooks) - REP",
    235: "Judge, 17th Subcircuit (Vacancy of Carroll) - REP",
    236: "Judge, 19th Subcircuit (Vacancy of Fairman) - REP",
    237: "Judge, 19th Subcircuit (Vacancy of Kane) - REP",
    238: "Judge, 20th Subcircuit (Vacancy of Haracz) - REP",
    239: "Judge, 20th Subcircuit (Vacancy of Miller) - REP",
}


def parse_html_table(html_data):
    """Parse the CBOE HTML table into structured rows.
    
    Returns:
        list of dicts with keys: ward, precinct, candidate, votes, pct
    """
    results = []
    
    # Clean HTML entities
    html = unescape(html_data)
    
    # Extract candidate names from <th> headers
    th_matches = re.findall(r'<th>([^<]+)</th>', html)
    if not th_matches:
        return results
    
    # Headers pattern: Total Votes, Candidate1, %, Candidate2, %, ...
    # or for precinct rows: Precinct, Total Voters, Candidate1, %, Candidate2, %, ...
    candidates = []
    for i, h in enumerate(th_matches):
        h = h.strip()
        if h in ('Total Votes', '%', 'Precinct', 'Total Voters', ''):
            continue
        candidates.append(h)
    
    # Remove duplicates (headers appear twice - summary and detail)
    # The unique candidates appear in first half
    if len(candidates) >= 2:
        half = len(candidates) // 2
        if candidates[:half] == candidates[half:]:
            candidates = candidates[:half]
    
    # Find ward sections and precinct rows
    # Ward headers: <td colspan="...">Ward XX</td>
    # Precinct rows: <td>precinct_num</td><td>total_voters</td><td>cand1_votes</td><td>pct</td>...
    
    current_ward = None
    
    # Split into rows
    row_pattern = r'<tr[^>]*>(.*?)</tr>'
    rows = re.findall(row_pattern, html, re.DOTALL)
    
    for row_html in rows:
        # Check for ward header
        ward_match = re.search(r'Ward\s+(\d+)', row_html)
        td_values = re.findall(r'<td[^>]*>([^<]*)</td>', row_html)
        
        if not td_values:
            continue
            
        # Ward header row (has colspan)
        if 'colspan' in row_html and ward_match:
            current_ward = int(ward_match.group(1))
            continue
        
        # Precinct data row: first cell is precinct number
        if current_ward and td_values and re.match(r'^\d+$', td_values[0].strip()):
            precinct = int(td_values[0].strip())
            # td_values: [precinct, total_voters, cand1_votes, pct1, cand2_votes, pct2, ...]
            total_voters_str = td_values[1].replace(',', '').strip() if len(td_values) > 1 else '0'
            total_voters = int(total_voters_str) if total_voters_str.isdigit() else 0
            
            # Parse candidate votes (starting at index 2, every other value is votes/pct)
            for ci, cand_name in enumerate(candidates):
                vote_idx = 2 + ci * 2  # votes at even positions after total_voters
                pct_idx = vote_idx + 1
                
                votes_str = td_values[vote_idx].replace(',', '').strip() if vote_idx < len(td_values) else '0'
                votes = int(votes_str) if votes_str.isdigit() else 0
                
                pct_str = td_values[pct_idx].replace('%', '').strip() if pct_idx < len(td_values) else '0'
                
                results.append({
                    'ward': current_ward,
                    'precinct': precinct,
                    'candidate': cand_name,
                    'votes': votes,
                    'pct': pct_str,
                    'total_voters': total_voters,
                })
    
    return results


def fetch_contest_ajax(session, election_id, contest_id, form_build_id):
    """Fetch contest data via CBOE AJAX endpoint.
    
    Returns: (html_data, new_form_build_id)
    """
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
        timeout=30,
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


def download_all_contests(election_id, contests, party_label):
    """Download all contests for an election via AJAX."""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    })
    
    # Get initial form_build_id
    print(f"\n{'='*60}")
    print(f"Loading {party_label} results page (election_id={election_id})...")
    resp = session.get(f'https://chicagoelections.gov/elections/results/{election_id}')
    fbid_match = re.search(r'name="form_build_id"\s+value="([^"]+)"', resp.text)
    if not fbid_match:
        print("ERROR: Could not get form_build_id")
        return
    
    form_build_id = fbid_match.group(1)
    print(f"form_build_id: {form_build_id}")
    
    all_results = []
    success = 0
    fail = 0
    
    for contest_id, contest_name in sorted(contests.items()):
        outfile = os.path.join(OUTPUT_DIR, f'contest_{contest_id}.csv')
        if os.path.exists(outfile):
            # Load existing
            with open(outfile, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            if rows:
                print(f"  [SKIP] Contest {contest_id}: {contest_name} ({len(rows)} rows already)")
                all_results.extend(rows)
                success += 1
                continue
        
        try:
            html_data, form_build_id = fetch_contest_ajax(
                session, election_id, contest_id, form_build_id
            )
            
            rows = parse_html_table(html_data)
            
            if rows:
                # Add contest metadata
                for row in rows:
                    row['contest_id'] = contest_id
                    row['contest_name'] = contest_name
                    row['election_id'] = election_id
                    row['party'] = party_label
                
                # Save individual CSV
                with open(outfile, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        'election_id', 'party', 'contest_id', 'contest_name',
                        'ward', 'precinct', 'candidate', 'votes', 'pct', 'total_voters'
                    ])
                    writer.writeheader()
                    writer.writerows(rows)
                
                all_results.extend(rows)
                success += 1
                print(f"  [OK] Contest {contest_id}: {contest_name} -> {len(rows)} rows")
            else:
                print(f"  [EMPTY] Contest {contest_id}: {contest_name} -> no precinct data")
                success += 1  # Not a failure, just no data
            
            time.sleep(0.5)  # Be polite
            
        except Exception as e:
            fail += 1
            print(f"  [FAIL] Contest {contest_id}: {contest_name} -> {e}")
            time.sleep(2)
    
    print(f"\n{party_label} Summary: {success} OK, {fail} FAIL, {len(all_results)} total rows")
    return all_results


if __name__ == '__main__':
    # Check which contests to download
    skip_existing = '--skip-existing' not in sys.argv
    
    # Download DEM contests (39-129) - we already have 11-38 from Neal's XLS files
    # But let's download ALL to have a clean dataset from one source
    print("Downloading DEM contests...")
    dem_results = download_all_contests(76, DEM_CONTESTS, 'DEM')
    
    print("\nDownloading REP contests...")
    rep_results = download_all_contests(77, REP_CONTESTS, 'REP')
    
    # Combine all
    all_results = (dem_results or []) + (rep_results or [])
    
    # Save combined CSV
    combined_file = os.path.join(OUTPUT_DIR, 'cboe_2026_all.csv')
    if all_results:
        with open(combined_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'election_id', 'party', 'contest_id', 'contest_name',
                'ward', 'precinct', 'candidate', 'votes', 'pct', 'total_voters'
            ])
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nCombined: {len(all_results)} rows -> {combined_file}")
    
    print("\nDone!")
