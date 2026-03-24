"""
Campaign Finance Pipeline — Configuration
Target: HD-18 (Gabel vs Hutchinson, 2022 & 2024 generals)
"""

import os

# ── Supabase ──
# IMPORTANT: Set these as environment variables. Never hardcode credentials.
# Export SUPA_SERVICE_KEY and PG_CONN in your shell or Replit Secrets.
SUPA_URL = "https://nfjfqdffulhqhszhlymo.supabase.co"
SUPA_KEY = os.environ.get("SUPA_SERVICE_KEY")
PG_CONN = os.environ.get("PG_CONN")

if not SUPA_KEY:
    raise EnvironmentError("SUPA_SERVICE_KEY environment variable is required. Set it in Replit Secrets or your shell.")
if not PG_CONN:
    raise EnvironmentError("PG_CONN environment variable is required. Set it in Replit Secrets or your shell.")

# ── IL SBE bulk data ──
SBE_RECEIPTS_URL = "https://www.elections.il.gov/Downloads/CampaignDisclosure/CampaignDisclosureDataFiles/Receipts.txt"

# ── Target committees (HD-18) ──
COMMITTEES = {
    "gabel_22260": {
        "sbe_id": 22260,
        "committee_name": "Friends of Robyn Gabel",
        "candidate_name": "Robyn Gabel",
        "party": "D",
        "status": "active",
    },
    "hutchinson_37092": {
        "sbe_id": 37092,
        "committee_name": "People for Charles Hutchinson",
        "candidate_name": "Charles Hutchinson",
        "party": "R",
        "status": "final",
    },
    "hutchinson_37331": {
        "sbe_id": 37331,
        "committee_name": "NT For Charles Hutchinson",
        "candidate_name": "Charles Hutchinson",
        "party": "R",
        "status": "final",
    },
}

TARGET_SBE_IDS = {str(c["sbe_id"]) for c in COMMITTEES.values()}

# ── Election cycles ──
# Contributions assigned by RcvDate ranges
FINANCE_ELECTIONS = {
    "2022_general_hd18": {
        "name": "HD-18 2022 General",
        "race_label": "IL House District 18",
        "year": 2022,
        "type": "general",
        "cycle_start": "2021-01-01",
        "cycle_end": "2022-11-08",
    },
    "2024_general_hd18": {
        "name": "HD-18 2024 General",
        "race_label": "IL House District 18",
        "year": 2024,
        "type": "general",
        "cycle_start": "2022-11-09",
        "cycle_end": "2024-11-05",
    },
}

# ── Receipts.txt column layout (tab-delimited) ──
RECEIPT_COLUMNS = [
    "ID", "CommitteeID", "FiledDocID", "ETransID",
    "LastOnlyName", "FirstName", "RcvDate", "Amount",
    "AggregateAmount", "LoanAmount", "Occupation", "Employer",
    "Address1", "Address2", "City", "State", "Zip",
    "D2Part", "Description",
    "VendorLastOnlyName", "VendorFirstName",
    "VendorAddress1", "VendorAddress2", "VendorCity", "VendorState", "VendorZip",
    "Archived", "Country", "RedactionRequested",
]

# ── Paths ──
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finance_data")
RECEIPTS_RAW = os.path.join(DATA_DIR, "receipts_raw.txt")
CONTRIBUTIONS_CSV = os.path.join(DATA_DIR, "contributions.csv")
GEOCODED_CSV = os.path.join(DATA_DIR, "contributions_geocoded.csv")
SUMMARY_CSV = os.path.join(DATA_DIR, "precinct_summary.csv")
RACE_SUMMARY_CSV = os.path.join(DATA_DIR, "precinct_race_summary.csv")

# ── GeoJSON for point-in-polygon ──
GEOJSON_CHICAGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "precincts_chicago.geojson")
GEOJSON_SUBURBAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "precincts_suburban.geojson")
