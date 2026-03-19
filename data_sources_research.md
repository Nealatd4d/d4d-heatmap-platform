# Cook County Election Data Sources Research
**Compiled:** March 19, 2026  
**Purpose:** Finding downloadable election results data for ALL of Cook County, IL (suburban + Chicago), consolidated elections, precinct shapefiles, and 2026 primary status.

---

## CRITICAL NOTE: The SBOE Cook/Chicago Split

Illinois State Board of Elections (SBOE) separates Cook County into **two distinct files**:
- **COOK** = Suburban Cook County (administered by Cook County Clerk)  
- **CITY OF CHICAGO COOK** = Chicago (administered by Chicago Board of Elections)

**To get ALL of Cook County precinct data, you must download BOTH files and combine them.**

This explains why your existing SBOE CSV files were Chicago-filtered — you likely only had the "CITY OF CHICAGO COOK" file.

---

## 1. SBOE — Full Cook County Precinct-Level Data

### Primary Portal
- **Vote Totals Search:** https://www.elections.il.gov/electionoperations/votetotalsearch.aspx
- **Precinct Downloads Hub:** https://www.elections.il.gov/electionoperations/ElectionVoteTotalsPrecinct.aspx

### How to Download Precinct CSVs
The SBOE precinct page works via a **JavaScript-driven POST request**. The download links are generated dynamically when you:

1. Go to: https://www.elections.il.gov/electionoperations/ElectionVoteTotalsPrecinct.aspx  
   *(Note: You need a valid election `?ID=` parameter — use the election dropdown on the page or navigate from the main results page)*
2. Select the election from the dropdown (e.g., **2024 GENERAL ELECTION**)
3. Click **"Precinct Downloads by Jurisdiction"**
4. Scroll to find **COOK** and **CITY OF CHICAGO COOK**
5. Click both download links — each generates a CSV file

### Elections Available (as of March 2026)
The SBOE precinct page has these elections in its dropdown:
- **2025 CONSOLIDATED ELECTION** ✅ (April 1, 2025)
- **2024 GENERAL ELECTION** ✅
- **2024 GENERAL PRIMARY** ✅
- **2023 CONSOLIDATED ELECTION** ✅ (April 4, 2023)
- **2022 GENERAL ELECTION** ✅
- **2022 GENERAL PRIMARY** ✅
- 2021 CONSOLIDATED ELECTION
- 2020 GENERAL ELECTION / PRIMARY
- 2019 CONSOLIDATED ELECTION
- *(and back to 1998)*

### Known Precinct Page URLs (with Election IDs)
These are confirmed working URLs with specific elections pre-loaded:
- **2024 General Primary:** https://www.elections.il.gov/electionoperations/ElectionVoteTotalsPrecinct.aspx?ID=rfZ%2BuidMSDY%3D
- **2022 General Election:** https://www.elections.il.gov/electionoperations/ElectionVoteTotalsPrecinct.aspx?ID=MVJQPFIDZQo%3D
- **2024 General Election:** https://www.elections.il.gov/electionoperations/ElectionVoteTotalsPrecinct.aspx?ID=%2Fs5hiMEB5JU%3D

**For each election, navigate to the Precinct tab and download both COOK and CITY OF CHICAGO COOK files.**

### Aggregate (Non-Precinct) County-Level Download
- **2024 General Election by County:** https://www.elections.il.gov/electionoperations/ElectionVoteTotalsCounty.aspx?ID=9huvqbsiUWA%3D
- **2025 Consolidated Election by County:** https://www.elections.il.gov/electionoperations/ElectionVoteTotalsCounty.aspx?ID=1nCmQ5aV324%3D
- **Search/Filter by Jurisdiction:** https://www.elections.il.gov/electionoperations/votetotalsearch.aspx  
  *(Select "COOK" in the Jurisdiction dropdown to filter to Cook County results only)*

### What the SBOE CSVs Contain
- Precinct name/number
- Office/contest name
- Candidate names
- Party
- Vote totals per precinct
- Format: CSV

### SBOE Limitations for Consolidated Elections
**Important:** For consolidated (municipal) elections, the SBOE data covers state legislative, judicial, and county-wide races. However, **hyper-local races** (village trustees, school boards, township offices) in suburban Cook County are primarily reported through the **Cook County Clerk**, not SBOE.

---

## 2. Cook County Clerk — Suburban Cook Election Results

### Main Elections Page
https://www.cookcountyclerkil.gov/elections

The Cook County Clerk (now Monica Gordon) administers elections for **120+ towns and villages in suburban Cook County** — everything outside Chicago city limits.

### Election Results & Data Portal
The Clerk's site describes multiple data resources:
- **"Results and Election Data"** section: Official results, data, analysis & Post-Election Reports
- **"Election Data"** section: Precinct-level election results, Early Voting turnout, voter registration statistics, turnout history — **all downloadable**

> *Note: The Cook County Clerk's website underwent a redesign. Several older URL patterns (e.g., `/elections/election-results`, `/elections/election-results-and-statistics`) return 404 errors as of March 2026. Navigate from the main elections page.*

### Active URL for Results
The Clerk's elections page currently shows: **"Click here for the March 17, 2026 Election Results"** banner.

The primary elections results portal appears to be:
https://www.cookcountyclerkil.gov/elections

Navigate to **"Results and Election Data"** from there.

### Election Viewer (GIS Map-Based)
- **Election Viewer Map:** https://maps.cookcountyil.gov/electionVwrLite/  
  (Interactive map by Cook County Clerk — precinct-level visualization)
- **Historic Election Results Gallery:** https://maps.cookcountyil.gov/electionresults/  
  (Older elections: 2016 Presidential, 2017 Consolidated, 2018 Gubernatorial)

### Elections Available from Cook County Clerk
| Election | Date | Notes |
|---|---|---|
| 2026 Gubernatorial Primary | March 17, 2026 | Results available — 94.62% precincts reporting as of election night; official results certified by ~April 7 |
| 2025 Consolidated Election | April 1, 2025 | Mayors, trustees, school boards, township offices |
| 2024 General Election | November 5, 2024 | Full suburban Cook precinct results |
| 2024 General Primary | March 19, 2024 | |
| 2023 Consolidated Election | April 4, 2023 | Suburban municipal races |
| 2022 General Election | November 8, 2022 | |
| 2022 General Primary | June 28, 2022 | |

### What Cook County Clerk Data Contains
Per the Crestwood, IL city website (which links directly to the Clerk's data portal):
- **Precinct-level election results** for all elections
- **Early Voting turnout** data
- **Voter registration statistics**
- **Turnout history**
- **Post-Election Reports** (analysis, close races, historical comparisons, turnout maps)

---

## 3. 2025 & 2023 Consolidated Election Data

### 2025 Consolidated Election (April 1, 2025)

**What was on ballot:** Mayors, village presidents, trustees, aldermen, township supervisors/assessors/collectors/highway commissioners, school board members, park boards, library boards, and other special district offices across suburban Cook County.

**Sources:**
1. **SBOE Precinct Downloads:**  
   https://www.elections.il.gov/electionoperations/ElectionVoteTotalsPrecinct.aspx  
   → Select "2025 CONSOLIDATED ELECTION" → Download COOK + CITY OF CHICAGO COOK files  
   *(Note: SBOE coverage of consolidated elections is limited to county-wide and state races; most hyperlocal municipal races go directly through the Clerk)*

2. **Cook County Clerk (primary source for suburban municipal races):**  
   https://www.cookcountyclerkil.gov/elections  
   → Navigate to "Results and Election Data"

3. **SBOE Vote Total Search (filterable):**  
   https://www.elections.il.gov/electionoperations/votetotalsearch.aspx  
   Select "2025 CONSOLIDATED ELECTION" + Jurisdiction = COOK

**Sample results coverage confirmed:**  
- South Cook County mayoral results sourced from Cook County Clerk website: Blue Island, Burbank, Calumet City, Calumet Park, Crestwood, Dolton, Flossmoor, Hometown, Markham, Oak Forest, Palos Heights, Palos Hills, Robbins, Sauk Village (reported April 1, 2025)

### 2023 Consolidated Election (April 4, 2023)

**Sources:**
1. **SBOE:** https://www.elections.il.gov/electionoperations/votetotalsearch.aspx  
   → Select "2023 CONSOLIDATED ELECTION"
2. **Cook County Clerk:** https://www.cookcountyclerkil.gov/elections  
   → Results and Election Data section

---

## 4. Suburban Cook County Precinct GeoJSON / Shapefile

### Primary Source: Cook County Open Data Hub (ArcGIS)

**Dataset: "Suburban Cook Election Precincts - Current"**
- **Dataset Page:** https://hub-cookcountyil.opendata.arcgis.com/datasets/0e91b48d49744346be343f0cb99d25bd_0/about
- **Maintained by:** Cook County Clerk's Election Department
- **Coverage:** All suburban Cook County precincts (EXCLUDES Chicago precincts)
- **Note:** "Not included are the City of Chicago Election Precincts which are maintained by the Chicago Board of Elections."

**Direct Download Options** (standard ArcGIS Hub patterns for dataset ID `0e91b48d49744346be343f0cb99d25bd_0`):
- **GeoJSON:** https://hub-cookcountyil.opendata.arcgis.com/datasets/0e91b48d49744346be343f0cb99d25bd_0.geojson
- **Shapefile (ZIP):** https://hub-cookcountyil.opendata.arcgis.com/datasets/0e91b48d49744346be343f0cb99d25bd_0.zip
- **CSV:** https://hub-cookcountyil.opendata.arcgis.com/datasets/0e91b48d49744346be343f0cb99d25bd_0.csv
- **API (JSON):** https://services1.arcgis.com/RojCNP3jFWQAb97P/arcgis/rest/services/ElectionPrecinct_Current/FeatureServer/0/query?where=1%3D1&outFields=*&f=json

> **Verify these URLs** by visiting the dataset page directly — ArcGIS Hub provides download buttons for all formats.

### Additional/Historical Precinct Datasets on Cook County Open Data
From data.gov catalog:
- **ElectionPrecinct_Current** (2015 precincts for 2016+): https://datacatalog.cookcountyil.gov — search "election precinct"
- **Election Precincts - 2011** (for 2012–2015 elections)
- **Election Precinct - 2009** (for 2010–2011 elections)

These older datasets matter if you need to join precinct boundaries to pre-2016 results.

### Chicago Precinct Shapefile (Chicago Board of Elections)
For the Chicago portion of Cook County, precinct boundaries are maintained by the **Chicago Board of Elections**. Check:
- https://chicagoelections.gov/en/election-results.html
- The Chicago Data Portal: https://data.cityofchicago.org — search "precinct"

### Combined/Academic Sources for Precinct Boundaries + Election Results
If you need precinct boundaries already joined to election results:
- **Redistricting Data Hub:** https://redistrictingdatahub.org — Illinois page has 2016, 2018, 2020, and some 2022 precinct boundary + results shapefiles
- **MIT Election Data Science Lab:** https://github.com/MEDSL — 2022 and 2024 Illinois precinct data available on GitHub
- **VEST (Voting and Election Science Team):** https://election.lab.ufl.edu/data-archive/ — Illinois precinct shapefiles with results

---

## 5. March 2026 Illinois Primary (Gubernatorial Primary)

### Status: YES — Already Occurred on March 17, 2026

The Illinois Gubernatorial Primary (also called the "Gubernatorial Primary Election") was held **Tuesday, March 17, 2026**. This was NOT a consolidated election — it was the statewide partisan primary covering:
- Governor (Pritzker D uncontested; Bailey won GOP)
- U.S. Senate (Stratton won Dem; Tracy won GOP)
- All 17 U.S. House seats
- Cook County offices (Board President, Assessor, etc.)
- Cook County Circuit Court judgeships

### Key Results
- **Governor (D):** JB Pritzker (uncontested)
- **Governor (R):** Darren Bailey defeated Ted Dabrowski (~50% vs. 32%)
- **U.S. Senate (D):** Juliana Stratton projected winner (~39%) over Raja Krishnamoorthi (~34%) and Robin Kelly (~18%)
- **Cook County Board President (D):** Toni Preckwinkle defeated Brendan Reilly (~68% vs. ~32%)
- **Cook County Assessor (D):** Fritz Kaegi vs. Pat Hynes (contested)
- **Suburban Cook turnout:** Record-breaking early voting — 122,000+ early voters before Election Day; 244,837 total ballots cast as of election night (14.2% turnout)

### Where to Get 2026 Primary Results

**Cook County Clerk (suburban Cook):**
https://www.cookcountyclerkil.gov/elections  
→ "Click here for the March 17, 2026 Election Results" (link visible on homepage)

**Chicago Board of Elections (Chicago precincts):**
https://chicagoelections.gov/en/election-results.html

**SBOE (state-level, all jurisdictions):**
https://www.elections.il.gov/electionoperations/votetotalsearch.aspx  
*(2026 GENERAL PRIMARY should appear in the dropdown once certified — official results certified by ~April 7, 2026)*

**Note:** As of March 19, 2026 (2 days after the election), results are **unofficial**. Outstanding mail-in ballots postmarked by March 17 can still be counted through March 31. **Official certification is expected around April 7, 2026.** Some judicial races were still too close to call. SBOE precinct-level CSV download will be available after certification.

---

## 6. Summary Action Plan

### To Get Full Cook County Data (All 5 Elections)

| Election | Primary Source | Secondary Source | Notes |
|---|---|---|---|
| **2024 General** | SBOE Precinct: COOK + CITY OF CHICAGO COOK | Cook County Clerk portal | Both files needed |
| **2024 Primary** | SBOE Precinct: COOK + CITY OF CHICAGO COOK | Cook County Clerk portal | Both files needed |
| **2022 General** | SBOE Precinct: COOK + CITY OF CHICAGO COOK | Cook County Clerk portal | Both files needed |
| **2022 Primary** | SBOE Precinct: COOK + CITY OF CHICAGO COOK | Cook County Clerk portal | Both files needed |
| **2025 Consolidated** | Cook County Clerk (primary for municipal) | SBOE for judicial/county races | Two-source approach needed |
| **2023 Consolidated** | Cook County Clerk (primary for municipal) | SBOE for judicial/county races | Two-source approach needed |
| **2026 Primary** | Not yet certified — check after ~April 7 | Cook County Clerk (unofficial) | |

### Step-by-Step SBOE Download Process
1. Navigate to: https://www.elections.il.gov/electionoperations/ElectionVoteTotalsPrecinct.aspx
2. **If you get an error**, go via the main results page: https://www.elections.il.gov/electionoperations/votetotalsearch.aspx → click "Precinct" tab
3. Select the election in the dropdown
4. Click **"Precinct Downloads by Jurisdiction"**
5. Download **COOK** → saves as a CSV (suburban Cook only)
6. Download **CITY OF CHICAGO COOK** → saves as a CSV (Chicago only)
7. Combine both CSVs for full Cook County

### For 2025/2023 Consolidated Municipal Races
The SBOE does NOT have precinct-level data for individual village/township offices. You must use the **Cook County Clerk** directly. The Clerk's election data section (https://www.cookcountyclerkil.gov/elections) provides:
- Precinct-level results downloadable
- Complete coverage of all 120+ suburban Cook municipalities
- Including mayors, trustees, school boards, park boards, etc.

---

## 7. Known Gaps & Limitations

1. **SBOE consolidated election coverage is partial** — only includes races where the state-level authority certifies results (county, judicial, some township races). Village/municipal-only races are NOT in SBOE precinct files.

2. **Cook County Clerk website URLs have changed** — the old `/elections/election-results-and-statistics` URL returns 404. Navigate from the main elections page. The underlying data portal may be at a different path now.

3. **Precinct shapefile vintage** — The "current" precinct dataset on the Cook County Open Data hub was last updated for 2016 primary/general elections. Precinct boundaries change between elections. For 2022–2025 elections, verify whether more recent boundary data is available, or use the election viewer map tool.

4. **2026 Primary data not yet certified** — Official SBOE precinct downloads will be available after April 7, 2026.

5. **SBOE download process is JavaScript-dependent** — You cannot directly construct a static URL to download precinct CSVs. The download is triggered by clicking a button that submits a form. You must visit the page in a browser (or use browser automation) to trigger the download.

---

## 8. Additional Resources

### OpenElections Project (GitHub)
Free, cleaned Illinois precinct data in CSV format:
- **Illinois OpenElections:** https://github.com/openelections/openelections-data-il
- Covers general, primary, and special elections by precinct, generally 2000–present
- Data is in CSV format
- **2022 and 2024 may already be available here** — check the repository

### MIT Election Data Science Lab
- Precinct-level returns for 2016–2024 Illinois general elections
- GitHub: https://github.com/MEDSL/2024-elections-official
- Includes joined precinct shapefiles for presidential years

### Redistricting Data Hub
- https://redistrictingdatahub.org/state/illinois/
- Precinct boundaries + election results shapefiles (2016, 2018, 2020, 2022)

---

*Research conducted March 19, 2026. All URLs verified active as of research date unless otherwise noted.*
