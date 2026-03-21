#!/usr/bin/env python3
"""
Race name normalizer for the D4D Election Heatmap Platform.

Converts race names from any source (SBOE, Cook County Clerk, Lake County Clerk, etc.)
into canonical forms so that MD5-based race_ids match across jurisdictions.

Canonical forms:
  Congressional:        "10TH CONGRESS"
  State Representative: "58TH STATE REPRESENTATIVE"
  State Senate:         "29TH STATE SENATE"
  Other:                cleaned up, party/vote-for suffixes stripped

Usage:
  from normalize_race import normalize_race_name
  canonical = normalize_race_name("Representative in Congress Tenth Congressional District (Vote For 1)")
  # => "10TH CONGRESS"
"""

import re

# ── Ordinal word → number mapping ────────────────────────────────────────────

_ONES = {
    'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5,
    'sixth': 6, 'seventh': 7, 'eighth': 8, 'ninth': 9,
}
_TEENS = {
    'tenth': 10, 'eleventh': 11, 'twelfth': 12, 'thirteenth': 13,
    'fourteenth': 14, 'fifteenth': 15, 'sixteenth': 16, 'seventeenth': 17,
    'eighteenth': 18, 'nineteenth': 19,
}
_TENS = {
    'twentieth': 20, 'thirtieth': 30, 'fortieth': 40, 'fiftieth': 50,
    'sixtieth': 60, 'seventieth': 70, 'eightieth': 80, 'ninetieth': 90,
    'hundredth': 100,
}
_TENS_PREFIX = {
    'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
    'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
    'hundred': 100,
}

# Simple ordinal words (no hyphen)
_SIMPLE_ORDINALS = {}
_SIMPLE_ORDINALS.update(_ONES)
_SIMPLE_ORDINALS.update(_TEENS)
_SIMPLE_ORDINALS.update(_TENS)


def _ordinal_suffix(n):
    """Return '1ST', '2ND', '3RD', '4TH', etc."""
    if 11 <= (n % 100) <= 13:
        return f"{n}TH"
    last = n % 10
    if last == 1:
        return f"{n}ST"
    elif last == 2:
        return f"{n}ND"
    elif last == 3:
        return f"{n}RD"
    else:
        return f"{n}TH"


def _word_to_number(word):
    """Convert an ordinal word like 'fifty-eighth' to an integer, or None."""
    w = word.lower().strip()
    # Simple single-word ordinal
    if w in _SIMPLE_ORDINALS:
        return _SIMPLE_ORDINALS[w]
    # Compound ordinal: "fifty-eighth", "twenty-first", "hundred-twentieth"
    if '-' in w:
        parts = w.split('-', 1)
        prefix = parts[0].strip()
        suffix = parts[1].strip()
        tens_val = _TENS_PREFIX.get(prefix, 0)
        ones_val = _SIMPLE_ORDINALS.get(suffix, 0)
        if tens_val and ones_val:
            return tens_val + ones_val
        # "hundred-twentieth" etc.
        if prefix == 'hundred' and suffix in _TENS:
            return 100 + _TENS[suffix]
        if prefix == 'hundred' and suffix in _SIMPLE_ORDINALS:
            return 100 + _SIMPLE_ORDINALS[suffix]
    return None


# Regex to match ordinal words (including hyphenated compounds)
_ORDINAL_WORDS = sorted(
    list(_SIMPLE_ORDINALS.keys()) + list(_TENS_PREFIX.keys()),
    key=len, reverse=True
)
# Pattern: "Fifty-Eighth" or "Tenth" etc.
_ORDINAL_PATTERN = re.compile(
    r'\b(' + '|'.join(_TENS_PREFIX.keys()) + r')[-\s](' + '|'.join(_SIMPLE_ORDINALS.keys()) + r')\b'
    r'|'
    r'\b(' + '|'.join(_SIMPLE_ORDINALS.keys()) + r')\b',
    re.IGNORECASE
)

# Numeric ordinal pattern: "10th", "1st", "58TH" etc.
_NUMERIC_ORDINAL = re.compile(r'\b(\d+)\s*(?:st|nd|rd|th)\b', re.IGNORECASE)


def _replace_ordinal_words(text):
    """Replace ordinal words with numeric ordinals: 'Tenth' → '10TH'."""
    def _repl(m):
        full = m.group(0)
        num = _word_to_number(full)
        if num is not None:
            return _ordinal_suffix(num)
        return full
    return _ORDINAL_PATTERN.sub(_repl, text)


# ── Party suffix stripping ───────────────────────────────────────────────────

_PARTY_SUFFIX = re.compile(
    r'\s*-\s*(?:DEM|REP|LIB|GRN|IND|NPA|CON|Democratic|Republican|Libertarian|Green)\s*$',
    re.IGNORECASE
)

# Vote For suffix
_VOTE_FOR = re.compile(r'\s*\(Vote\s+For\s+\d+\)\s*$', re.IGNORECASE)


# ── Office type patterns ─────────────────────────────────────────────────────

# Congressional patterns
_CONGRESS_PATTERNS = [
    # "Representative in Congress Tenth Congressional District" (Lake County)
    re.compile(r'Representative\s+in\s+Congress\s+.*?(\d+)\w*\s+Congressional', re.IGNORECASE),
    # "U.S. Representative, 10th District" (Cook Clerk)
    re.compile(r'U\.?S\.?\s+Representative[,\s]+(\d+)\w*\s+District', re.IGNORECASE),
    # "10TH CONGRESS" or "10TH CONGRESSIONAL DISTRICT" (SBOE)
    re.compile(r'(\d+)\w*\s+CONGRESS(?:IONAL)?(?:\s+DISTRICT)?$', re.IGNORECASE),
    # "Member of Congress, 10th District"
    re.compile(r'Member\s+of\s+Congress[,\s]+(\d+)\w*\s+District', re.IGNORECASE),
    # Generic: contains "congress" + a district number
    re.compile(r'(\d+)\w*\s+(?:Congressional\s+District|Congress)', re.IGNORECASE),
]

# State Representative patterns
_STATE_REP_PATTERNS = [
    # "Representative in the General Assembly Fifty-Eighth Representative District" (Lake County)
    re.compile(r'Representative\s+in\s+(?:the\s+)?General\s+Assembly\s+.*?(\d+)\w*\s+Representative', re.IGNORECASE),
    # "State Representative, 58th District" (Cook Clerk)
    re.compile(r'State\s+Representative[,\s]+(\d+)\w*\s+District', re.IGNORECASE),
    # "58TH STATE REPRESENTATIVE" (canonical/SBOE new)
    re.compile(r'(\d+)\w*\s+STATE\s+REPRESENTATIVE', re.IGNORECASE),
    # "58TH REPRESENTATIVE" (SBOE existing short form — no "STATE" prefix)
    re.compile(r'^(\d+)\w*\s+REPRESENTATIVE$', re.IGNORECASE),
    # "Representative, 58th District" (without "State" prefix but no "Congress")
    re.compile(r'^Representative[,\s]+(\d+)\w*\s+District$', re.IGNORECASE),
    # "58th Representative District"
    re.compile(r'(\d+)\w*\s+Representative\s+District$', re.IGNORECASE),
]

# State Senate patterns
_STATE_SENATE_PATTERNS = [
    # "Senator in the General Assembly Twenty-Ninth Legislative District" (Lake County)
    re.compile(r'Senator\s+in\s+(?:the\s+)?General\s+Assembly\s+.*?(\d+)\w*\s+Legislative', re.IGNORECASE),
    # "State Senator Twenty-Ninth Legislative District" (Lake County alt)
    re.compile(r'State\s+Senator\s+.*?(\d+)\w*\s+Legislative\s+District', re.IGNORECASE),
    # "State Senator, 29th District" (Cook Clerk)
    re.compile(r'State\s+Senator[,\s]+(\d+)\w*\s+District', re.IGNORECASE),
    # "29TH STATE SENATE" (canonical/SBOE new)
    re.compile(r'(\d+)\w*\s+STATE\s+SENATE', re.IGNORECASE),
    # "29TH SENATE" (SBOE existing short form — no "STATE" prefix)
    re.compile(r'^(\d+)\w*\s+SENATE$', re.IGNORECASE),
    # "State Senate, 29th District"
    re.compile(r'State\s+Senate[,\s]+(\d+)\w*\s+District', re.IGNORECASE),
    # "29th Legislative District" (Lake County without "Senator" context)
    re.compile(r'(\d+)\w*\s+Legislative\s+District$', re.IGNORECASE),
    # "29th Senate District"
    re.compile(r'(\d+)\w*\s+Senate\s+District$', re.IGNORECASE),
]


def normalize_race_name(raw_name):
    """
    Normalize a race name from any source into a canonical form.

    Canonical forms:
      Congressional:        "10TH CONGRESS"
      State Representative: "58TH STATE REPRESENTATIVE"
      State Senate:         "29TH STATE SENATE"
      Other races:          uppercased, stripped of party/vote-for suffixes

    Idempotent: running on an already-normalized name returns the same name.
    """
    if not raw_name:
        return raw_name

    name = raw_name.strip()

    # Step 1: Strip party suffixes (e.g. " - DEM", " - REP")
    name = _PARTY_SUFFIX.sub('', name)

    # Step 2: Strip "(Vote For N)" suffixes
    name = _VOTE_FOR.sub('', name)

    # Step 3: Clean up whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    # Step 4: Replace ordinal words with numbers ("Tenth" → "10TH")
    name = _replace_ordinal_words(name)

    # Step 5: Normalize numeric ordinal formatting ("10 th" → "10TH")
    name = re.sub(r'(\d+)\s*(?:st|ST|nd|ND|rd|RD|th|TH)\b', lambda m: _ordinal_suffix(int(m.group(1))), name)

    # Step 6: Try to match office type patterns and canonicalize

    # Congressional
    for pattern in _CONGRESS_PATTERNS:
        m = pattern.search(name)
        if m:
            district = int(m.group(1))
            return f"{_ordinal_suffix(district)} CONGRESS"

    # State Representative — must check BEFORE generic "Representative" match
    # But skip if name clearly contains "Congress" or "U.S."
    name_upper = name.upper()
    if 'CONGRESS' not in name_upper and 'U.S.' not in name_upper:
        for pattern in _STATE_REP_PATTERNS:
            m = pattern.search(name)
            if m:
                district = int(m.group(1))
                return f"{_ordinal_suffix(district)} STATE REPRESENTATIVE"

    # State Senate
    for pattern in _STATE_SENATE_PATTERNS:
        m = pattern.search(name)
        if m:
            district = int(m.group(1))
            return f"{_ordinal_suffix(district)} STATE SENATE"

    # Step 7: For non-matched races, uppercase and clean
    name = name.upper().strip()

    # Remove redundant "DISTRICT" at end if there's already a number
    # e.g. "COOK COUNTY COMMISSIONER 6TH DISTRICT" stays as-is (specificity)

    return name


# ── Unit tests ───────────────────────────────────────────────────────────────

def _run_tests():
    """Run unit tests. Execute with: python3 normalize_race.py"""
    import sys

    tests = [
        # ── Congressional ──
        ("10TH CONGRESS", "10TH CONGRESS"),  # idempotent
        ("Representative in Congress Tenth Congressional District (Vote For 1)",
         "10TH CONGRESS"),
        ("U.S. Representative, 10th District - DEM", "10TH CONGRESS"),
        ("U.S. Representative, 10th District - REP", "10TH CONGRESS"),
        ("1ST CONGRESS", "1ST CONGRESS"),
        ("2ND CONGRESS", "2ND CONGRESS"),
        ("3RD CONGRESS", "3RD CONGRESS"),
        ("Representative in Congress First Congressional District (Vote For 1)",
         "1ST CONGRESS"),
        ("Representative in Congress Ninth Congressional District (Vote For 1)",
         "9TH CONGRESS"),
        ("Representative in Congress Fourteenth Congressional District (Vote For 1)",
         "14TH CONGRESS"),
        ("9TH CONGRESSIONAL DISTRICT", "9TH CONGRESS"),

        # ── State Representative ──
        ("58TH STATE REPRESENTATIVE", "58TH STATE REPRESENTATIVE"),  # idempotent
        ("State Representative, 58th District - DEM", "58TH STATE REPRESENTATIVE"),
        ("Representative in the General Assembly Fifty-Eighth Representative District (Vote For 1)",
         "58TH STATE REPRESENTATIVE"),
        ("1ST STATE REPRESENTATIVE", "1ST STATE REPRESENTATIVE"),
        ("Representative in the General Assembly Twenty-First Representative District (Vote For 1)",
         "21ST STATE REPRESENTATIVE"),
        ("State Representative, 1st District - REP", "1ST STATE REPRESENTATIVE"),
        # SBOE short form (no "STATE" prefix)
        ("58TH REPRESENTATIVE", "58TH STATE REPRESENTATIVE"),
        ("41ST REPRESENTATIVE", "41ST STATE REPRESENTATIVE"),
        ("82ND REPRESENTATIVE", "82ND STATE REPRESENTATIVE"),

        # ── State Senate ──
        ("29TH STATE SENATE", "29TH STATE SENATE"),  # idempotent
        ("State Senator, 29th District - DEM", "29TH STATE SENATE"),
        ("Senator in the General Assembly Twenty-Ninth Legislative District (Vote For 1)",
         "29TH STATE SENATE"),
        ("State Senate, 1st District", "1ST STATE SENATE"),
        # SBOE short form (no "STATE" prefix)
        ("29TH SENATE", "29TH STATE SENATE"),
        ("21ST SENATE", "21ST STATE SENATE"),
        ("41ST SENATE", "41ST STATE SENATE"),
        # Lake County alt format
        ("State Senator Thirty-First Legislative District (Vote For 1)",
         "31ST STATE SENATE"),

        # ── Ordinal word conversion ──
        ("Representative in the General Assembly Sixty-Second Representative District (Vote For 1)",
         "62ND STATE REPRESENTATIVE"),
        ("Representative in the General Assembly Thirty-Third Representative District (Vote For 1)",
         "33RD STATE REPRESENTATIVE"),
        ("Representative in Congress Eleventh Congressional District (Vote For 1)",
         "11TH CONGRESS"),
        ("Representative in Congress Twelfth Congressional District (Vote For 1)",
         "12TH CONGRESS"),
        ("Representative in Congress Thirteenth Congressional District (Vote For 1)",
         "13TH CONGRESS"),

        # ── Party suffix stripping ──
        ("U.S. Representative, 5th District - DEM", "5TH CONGRESS"),
        ("State Representative, 77th District - REP", "77TH STATE REPRESENTATIVE"),
        ("State Senator, 15th District - LIB", "15TH STATE SENATE"),
        ("State Senator, 15th District - GRN", "15TH STATE SENATE"),

        # ── Vote For stripping ──
        ("Some Municipal Race (Vote For 3)", "SOME MUNICIPAL RACE"),

        # ── Edge cases: already-normalized ──
        ("PRESIDENT", "PRESIDENT"),
        ("GOVERNOR", "GOVERNOR"),

        # ── Large district numbers ──
        ("118TH STATE REPRESENTATIVE", "118TH STATE REPRESENTATIVE"),
        ("State Representative, 120th District - DEM", "120TH STATE REPRESENTATIVE"),

        # ── Empty/None ──
        ("", ""),
        (None, None),
    ]

    passed = 0
    failed = 0
    for raw, expected in tests:
        result = normalize_race_name(raw)
        if result == expected:
            passed += 1
        else:
            failed += 1
            print(f"FAIL: normalize_race_name({raw!r})")
            print(f"  Expected: {expected!r}")
            print(f"  Got:      {result!r}")

    print(f"\n{'='*60}")
    print(f"Tests: {passed + failed} total, {passed} passed, {failed} failed")
    print(f"{'='*60}")

    if failed > 0:
        sys.exit(1)
    else:
        print("All tests passed!")


if __name__ == "__main__":
    _run_tests()
