"""
Unified race_type classifier for all D4D election data loaders.
Single source of truth — all loaders should import from here.

Usage:
    from classify_race import classify_race_type

Returns: (race_type, district_number) tuple
    race_type: str matching the DB CHECK constraint
    district_number: int (0 if N/A)
"""

import re

# ─── Valid race_types (must match DB CHECK constraint on races table) ───
VALID_RACE_TYPES = {
    # Federal
    'president', 'us_senate', 'congress',
    # State executive
    'governor', 'lt_governor', 'attorney_general', 'secretary_of_state',
    'comptroller', 'treasurer_state',
    # State legislature
    'state_senate', 'state_rep',
    # State party
    'state_central_comm', 'delegate',
    # Judicial
    'supreme_court', 'appellate_court', 'circuit_court', 'subcircuit', 'judge',
    # Cook County
    'cook_commissioner', 'cook_president', 'cook_assessor', 'cook_clerk',
    'cook_treasurer', 'cook_sheriff', 'board_of_review', 'mwrd',
    # Chicago municipal
    'mayor', 'aldermanic_ward', 'city_clerk', 'city_treasurer',
    # Suburban municipal
    'municipal', 'municipal_ward',
    # Township
    'township_office', 'township_committeeperson',
    # Education
    'school_board', 'school_district',
    # District
    'park_district', 'library', 'fire_district', 'water_reclamation',
    # Other
    'referendum', 'other',
}


def classify_race_type(contest_name, source='auto'):
    """
    Classify a contest/race name into our race_type taxonomy.

    Args:
        contest_name: The raw contest name from the data source
        source: 'sboe' | 'cook_clerk' | 'suburban' | 'school_board' | 'auto'
                Helps disambiguate source-specific naming conventions.

    Returns:
        (race_type, district_number) — e.g. ('congress', 9) or ('mayor', 0)
    """
    if not contest_name or not contest_name.strip():
        return ('other', 0)

    name = contest_name.strip()
    upper = name.upper()
    lower = name.lower()

    # ═══════════════════════════════════════════════════════════════
    # 1. FEDERAL
    # ═══════════════════════════════════════════════════════════════

    # President
    if 'PRESIDENT' in upper and (
        'UNITED STATES' in upper or 'PRESIDENT AND' in upper or
        upper.strip() == 'PRESIDENT' or 'VICE PRESIDENT' in upper
    ):
        return ('president', 0)

    # U.S. Senate
    if any(x in upper for x in ['U.S. SENATOR', 'UNITED STATES SENATOR',
                                   'SENATOR, U.S.']):
        return ('us_senate', 0)

    # Congress / U.S. Representative
    m = re.match(r'(\d+)\w*\s+CONGRESS', upper)
    if m:
        return ('congress', int(m.group(1)))
    if any(x in lower for x in ['representative in congress',
                                  'u.s. representative']):
        m = re.search(r'(\d+)', upper)
        return ('congress', int(m.group(1)) if m else 0)
    if 'congress' in lower and 'u.s.' not in lower:
        m = re.search(r'(\d+)', upper)
        return ('congress', int(m.group(1)) if m else 0)

    # ═══════════════════════════════════════════════════════════════
    # 2. STATE EXECUTIVE
    # ═══════════════════════════════════════════════════════════════

    # Governor (must check BEFORE lt_governor)
    if 'GOVERNOR AND LIEUTENANT GOVERNOR' in upper:
        return ('governor', 0)
    if re.match(r'^GOVERNOR\b', upper) and 'LT' not in upper and 'LIEUTENANT' not in upper:
        return ('governor', 0)
    if 'governor' in lower and 'lt' not in lower and 'lieutenant' not in lower:
        return ('governor', 0)

    # Lt. Governor
    if 'LIEUTENANT GOVERNOR' in upper or 'LT. GOVERNOR' in upper:
        return ('lt_governor', 0)

    # Attorney General
    if 'ATTORNEY GENERAL' in upper:
        return ('attorney_general', 0)

    # Secretary of State
    if 'SECRETARY OF STATE' in upper:
        return ('secretary_of_state', 0)

    # Comptroller
    if 'COMPTROLLER' in upper:
        return ('comptroller', 0)

    # State Treasurer (not city/county)
    if any(x in lower for x in ['treasurer, state', 'state treasurer']):
        return ('treasurer_state', 0)
    if 'TREASURER' in upper and 'CITY' not in upper and 'COUNTY' not in upper and 'VILLAGE' not in upper:
        # SBOE context: treasurer at state level
        if source in ('sboe', 'suburban'):
            return ('treasurer_state', 0)

    # ═══════════════════════════════════════════════════════════════
    # 3. STATE LEGISLATURE
    # ═══════════════════════════════════════════════════════════════

    # State Senate
    m = re.match(r'(\d+)\w*\s+SENATE', upper)
    if m:
        return ('state_senate', int(m.group(1)))
    if 'STATE SENATOR' in upper:
        m = re.search(r'(\d+)', upper)
        return ('state_senate', int(m.group(1)) if m else 0)
    if 'senate' in lower and 'u.s.' not in lower and 'state central' not in lower:
        m = re.search(r'(\d+)', upper)
        return ('state_senate', int(m.group(1)) if m else 0)

    # State Representative
    m = re.match(r'(\d+)\w*\s+REPRESENTATIVE', upper)
    if m:
        return ('state_rep', int(m.group(1)))
    if 'STATE REPRESENTATIVE' in upper:
        m = re.search(r'(\d+)', upper)
        return ('state_rep', int(m.group(1)) if m else 0)
    if 'representative' in lower and 'congress' not in lower and 'u.s.' not in lower:
        m = re.search(r'(\d+)', upper)
        return ('state_rep', int(m.group(1)) if m else 0)

    # ═══════════════════════════════════════════════════════════════
    # 4. STATE PARTY OFFICES
    # ═══════════════════════════════════════════════════════════════

    # State Central Committeeperson
    if any(x in upper for x in ['STATE CENTRAL', 'COMMITTEEMAN', 'COMMITTEEWOMAN']):
        if 'DEM STATE CENTRAL' in upper or 'REP STATE CENTRAL' in upper or \
           'COMMITTEEMAN' in upper or 'COMMITTEEWOMAN' in upper or 'STATE CENTRAL' in upper:
            m = re.search(r'(\d+)', upper)
            return ('state_central_comm', int(m.group(1)) if m else 0)

    # Delegate
    if 'DELEGATE' in upper:
        m = re.search(r'(\d+)', upper)
        return ('delegate', int(m.group(1)) if m else 0)

    # ═══════════════════════════════════════════════════════════════
    # 5. JUDICIAL
    # ═══════════════════════════════════════════════════════════════

    # Supreme Court
    if 'SUPREME' in upper:
        m = re.search(r'(\d+)', upper)
        return ('supreme_court', int(m.group(1)) if m else 1)

    # Appellate Court
    if 'APPELLATE' in upper:
        m = re.search(r'(\d+)', upper)
        return ('appellate_court', int(m.group(1)) if m else 1)

    # Subcircuit (must check BEFORE circuit_court)
    if 'SUBCIRCUIT' in upper or 'SUB-CIRCUIT' in upper or 'SUB CIRCUIT' in upper:
        m = re.search(r'(\d+)\w*\s+SUB', upper)
        if m:
            return ('subcircuit', int(m.group(1)))
        m = re.search(r'(\d+)', upper)
        if m:
            return ('subcircuit', int(m.group(1)))
        return ('subcircuit', 0)

    # Circuit Court (not subcircuit)
    if 'CIRCUIT' in upper and 'SUB' not in upper:
        return ('circuit_court', 0)

    # Generic judge/judicial/justice (Cook Clerk format)
    # Exclude place names like "Village of Justice" or "Justice Library"
    if 'judicial' in lower:
        return ('judge', 0)
    if 'judge' in lower and 'village' not in lower:
        return ('judge', 0)
    if 'justice' in lower and 'village' not in lower and 'library' not in lower and 'park' not in lower:
        return ('judge', 0)

    # ═══════════════════════════════════════════════════════════════
    # 6. COOK COUNTY
    # ═══════════════════════════════════════════════════════════════

    # Board President
    if 'BOARD PRESIDENT' in upper or 'COUNTY PRESIDENT' in upper:
        return ('cook_president', 0)
    if 'board president, cook county' in lower:
        return ('cook_president', 0)

    # County Commissioner
    if 'commissioner' in lower and ('county board' in lower or 'cook county' in lower):
        m = re.search(r'(\d+)', upper)
        return ('cook_commissioner', int(m.group(1)) if m else 0)
    m = re.search(r'(\d+)\w*\s+(COUNTY\s+)?COMMISSIONER', upper)
    if m and 'VILLAGE' not in upper and 'CITY' not in upper and 'PARK' not in upper:
        return ('cook_commissioner', int(m.group(1)))

    # Cook County specific offices
    if 'assessor, cook county' in lower or 'cook county assessor' in lower:
        return ('cook_assessor', 0)
    if 'clerk, cook county' in lower or 'cook county clerk' in lower:
        return ('cook_clerk', 0)
    if 'treasurer, cook county' in lower or 'cook county treasurer' in lower:
        return ('cook_treasurer', 0)
    if 'sheriff, cook county' in lower or 'cook county sheriff' in lower:
        return ('cook_sheriff', 0)
    if 'board of review' in lower:
        return ('board_of_review', 0)

    # MWRD
    if any(x in upper for x in ['WATER RECLAMATION', 'MWRD']):
        return ('mwrd', 0)

    # ═══════════════════════════════════════════════════════════════
    # 7. CHICAGO MUNICIPAL
    # ═══════════════════════════════════════════════════════════════

    # Chicago-specific: only exact Chicago offices get chicago types
    # "Mayor, City of Chicago" → mayor; "Mayor, City of Palos Hills" → municipal
    if 'mayor' in lower:
        if 'chicago' in lower or source in ('sboe', 'school_board'):
            return ('mayor', 0)
        # Suburban mayors from cook_clerk are 'municipal'
        if source == 'cook_clerk' or source == 'suburban':
            return ('municipal', 0)
        # Auto: check if it says "city of" (suburban) vs just "mayor"
        if 'city of' in lower and 'chicago' not in lower:
            return ('municipal', 0)
        return ('mayor', 0)

    # "Alderperson, City of X" = suburban municipal_ward (not Chicago aldermanic_ward)
    if 'alderperson' in lower and 'city of' in lower and 'chicago' not in lower:
        return ('municipal_ward', 0)
    if 'alderman' in lower or 'alderperson' in lower:
        m = re.search(r'(\d+)', upper)
        return ('aldermanic_ward', int(m.group(1)) if m else 0)

    if 'city clerk' in lower or 'clerk, city' in lower:
        if 'chicago' in lower or source in ('sboe', 'school_board'):
            return ('city_clerk', 0)
        if source == 'cook_clerk' or source == 'suburban':
            return ('municipal', 0)
        if 'city of' in lower and 'chicago' not in lower:
            return ('municipal', 0)
        return ('city_clerk', 0)

    if 'city treasurer' in lower or 'treasurer, city' in lower:
        if 'chicago' in lower or source in ('sboe', 'school_board'):
            return ('city_treasurer', 0)
        if source == 'cook_clerk' or source == 'suburban':
            return ('municipal', 0)
        if 'city of' in lower and 'chicago' not in lower:
            return ('municipal', 0)
        return ('city_treasurer', 0)

    # ═══════════════════════════════════════════════════════════════
    # 8. TOWNSHIP
    # ═══════════════════════════════════════════════════════════════

    # Township offices
    if 'township' in lower and any(x in lower for x in [
        'supervisor', 'assessor', 'highway commissioner', 'collector',
        'clerk', 'trustee'
    ]):
        return ('township_office', 0)

    # Township committeeperson (party)
    if re.match(r'(dem|rep|lib)\s+committeeperson', lower):
        return ('township_committeeperson', 0)
    if 'committeeperson' in lower and 'state central' not in lower:
        return ('township_committeeperson', 0)

    # Township referendum
    if 'township' in lower and any(x in lower for x in [
        'pension reform', 'unfunded mandates', 'redistricting', 'mental health'
    ]):
        return ('referendum', 0)

    # ═══════════════════════════════════════════════════════════════
    # 9. SUBURBAN MUNICIPAL
    # ═══════════════════════════════════════════════════════════════

    if any(x in lower for x in [
        'president, village', 'mayor,', 'clerk, village', 'clerk, city',
        'trustee, village', 'trustee, city', 'treasurer, village',
        'treasurer, city', 'commissioner, village', 'commissioner, city'
    ]):
        return ('municipal', 0)

    # Ward-level municipal
    if 'ward' in lower and ('alderman' in lower or 'council' in lower):
        return ('municipal_ward', 0)
    if 'alderperson' in lower:
        return ('municipal_ward', 0)
    if 'council member' in lower or 'councilmember' in lower:
        return ('municipal_ward', 0)

    # ═══════════════════════════════════════════════════════════════
    # 10. EDUCATION
    # ═══════════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════════
    # 11. SPECIAL DISTRICTS (must check BEFORE education to avoid
    #     "trustee" in FPD/park matching school_district)
    # ═══════════════════════════════════════════════════════════════

    # Fire district (FPD = Fire Protection District)
    if any(x in lower for x in ['fpd', 'fire protection', 'fire district']):
        return ('fire_district', 0)
    if 'fire' in lower and any(x in lower for x in [
        'trustee', 'commissioner', 'president'
    ]):
        return ('fire_district', 0)

    # Park district
    if 'park' in lower and any(x in lower for x in [
        'commissioner', 'trustee', 'president', 'board', 'cmsnr.'
    ]):
        return ('park_district', 0)

    # Library
    if 'library' in lower:
        return ('library', 0)

    # Water/sanitary
    if any(x in lower for x in ['water reclamation', 'sanitary', 'water district']):
        return ('water_reclamation', 0)

    # ═══════════════════════════════════════════════════════════════
    # 10. EDUCATION (after special districts)
    # ═══════════════════════════════════════════════════════════════

    if source == 'school_board':
        return ('school_board', 0)

    if any(x in lower for x in [
        'school b.m.', 'school board', 'school district', 'school trustee',
        'hsd ', 'elementary', 'high school', 'community college',
        'unit school', 'trustee of schools'
    ]):
        return ('school_district', 0)
    if 'college' in lower and 'trustee' in lower:
        return ('school_district', 0)

    # ═══════════════════════════════════════════════════════════════
    # 12. REFERENDUMS
    # ═══════════════════════════════════════════════════════════════

    if any(x in lower for x in [
        'referendum', 'issue bonds', 'increase limiting rate',
        'proposition', 'advisory', 'ballot question', 'shall'
    ]):
        return ('referendum', 0)

    # ═══════════════════════════════════════════════════════════════
    # FALLBACK
    # ═══════════════════════════════════════════════════════════════

    # For SBOE/suburban sources, unmatched items are often referendums
    if source in ('sboe', 'suburban'):
        return ('referendum', 0)

    return ('other', 0)


def validate_race_type(race_type):
    """Check if a race_type is in our valid set."""
    return race_type in VALID_RACE_TYPES


if __name__ == '__main__':
    # Quick self-test with known names
    tests = [
        ("9TH CONGRESSIONAL DISTRICT", 'sboe', 'congress', 9),
        ("Ward 42 Precinct 1", 'sboe', 'referendum', 0),  # SBOE fallback for unmatched
        ("GOVERNOR AND LIEUTENANT GOVERNOR", 'sboe', 'governor', 0),
        ("Alderman, 25th Ward", 'cook_clerk', 'aldermanic_ward', 25),
        ("Judge, Circuit Court of Cook County", 'cook_clerk', 'circuit_court', 0),  # 'circuit' keyword triggers circuit_court
        ("3RD SUBCIRCUIT COOK COUNTY", 'sboe', 'subcircuit', 3),
        ("COMMISSIONER, COUNTY BOARD 1ST DISTRICT", 'cook_clerk', 'cook_commissioner', 1),
        ("13TH REPRESENTATIVE", 'sboe', 'state_rep', 13),
        ("State Senator, 5th District", 'cook_clerk', 'state_senate', 5),
        ("Mayor, City of Chicago", 'cook_clerk', 'mayor', 0),
        ("Dem Committeeperson, Niles Township", 'cook_clerk', 'township_committeeperson', 0),
        ("Chicago School Board District 1", 'school_board', 'school_board', 0),
    ]

    passed = 0
    for contest, source, expected_type, expected_num in tests:
        rt, num = classify_race_type(contest, source)
        ok = rt == expected_type and num == expected_num
        status = "✓" if ok else "✗"
        if not ok:
            print(f"  {status} '{contest}' → ({rt}, {num}) expected ({expected_type}, {expected_num})")
        else:
            print(f"  {status} '{contest}' → ({rt}, {num})")
        if ok:
            passed += 1

    print(f"\n{passed}/{len(tests)} tests passed")
