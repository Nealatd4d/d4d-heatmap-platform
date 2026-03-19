# D4D Heatmap Frontend - Supabase Wire-Up Spec

## Architecture
Single-page static HTML/CSS/JS app. No build tools. Leaflet for maps.
Fetches all data from Supabase REST API (PostgREST).

## Supabase Config
- URL: `https://nfjfqdffulhqhszhlymo.supabase.co`
- Anon key: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5mamZxZGZmdWxocWhzemhseW1vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5NTAzMDgsImV4cCI6MjA4OTUyNjMwOH0.vNrXz0iCwA4scUCP2O75KWaLyh7LVQrYmUdnEGMnnCE`
- Max rows: 5000

## RPC Endpoints (POST to /rest/v1/rpc/{name})
Headers: `apikey`, `Authorization: Bearer <key>`, `Content-Type: application/json`

### get_elections()
Returns: `[{id, election_name, election_date, election_type, election_year, state, race_count}]`
Sample: `{id: "2024_general", election_name: "2024 General Election", election_date: "2024-11-05", election_type: "general", election_year: 2024, state: "IL", race_count: 228}`

### get_races(p_election_id)
Returns: `[{id, race_name, race_type, district_id, election_id, election_name, election_date}]`
race_type values in DB: aldermanic_ward, appellate_court, attorney_general, circuit_court, city_clerk, city_treasurer, comptroller, congress, cook_commissioner, cook_president, delegate, governor, mayor, mwrd, president, referendum, school_board, secretary_of_state, state_central_comm, state_rep, state_senate, subcircuit, supreme_court, treasurer_state, us_senate

### get_race_map(p_race_id) — NEW, pre-aggregated
Returns: `[{precinct_id, total_votes, candidates: [{n, v, p}]}]`
- One row per precinct (max ~4000 rows for countywide races)
- candidates is JSONB array sorted by votes DESC
- Excludes Over/Under/Write-in votes
- p = vote_share_pct (rounded to 1 decimal)

### get_race_turnout(p_election_id)
Returns: `[{precinct_id, source_precinct_name, ward, registered_voters, ballots_cast, turnout_pct}]`
- Up to ~3500 rows per election

## GeoJSON Files (load via fetch)
### data/precincts_chicago.geojson (5.2 MB, 1291 features)
Properties: `{ward: 2, precinct: 15, name: "Ward 2 Precinct 15", jur: "chicago"}`

### data/precincts_suburban.geojson (10.3 MB, 1430 features)
Properties: `{precinctid: "7000011", name: "BARRINGTON 11", jur: "suburban"}`

## Precinct ID Mapping (GeoJSON → DB)
The DB uses MD5 hash IDs. Frontend must compute them to join GeoJSON features with API data.

**Formula:** `md5(jurisdiction + "|" + source_precinct_name).substring(0, 16)`
All inputs lowercased.

**Chicago:** 
- jurisdiction = "chicago"
- source_precinct_name = `"Ward " + pad2(ward) + " Precinct " + pad2(precinct)` (from GeoJSON properties)
- Example: ward=2, precinct=15 → md5("chicago|ward 02 precinct 15")[:16] = "24c08119aad80244"

**Suburban:**
- jurisdiction = "cook_suburban"  
- source_precinct_name = precinctid (from GeoJSON)
- Example: precinctid="7000011" → md5("cook_suburban|7000011")[:16] = "a25a6c9a826b5574"

**Use SparkMD5 (CDN)** for fast MD5 in browser: https://cdn.jsdelivr.net/npm/spark-md5@3.0.2/spark-md5.min.js

## District Type Selector (toolbar dropdown)
Map DB race_type values to user-friendly groups:

| Group | Label | DB race_type(s) | Mode |
|-------|-------|-----------------|------|
| Legislative | State House | state_rep | Filter by district_id |
| Legislative | State Senate | state_senate | Filter by district_id |
| Legislative | Congressional | congress | Filter by district_id |
| Municipal | Mayor | mayor | Countywide (city) |
| Municipal | Alderman | aldermanic_ward | Filter by district_id |
| Municipal | City Clerk | city_clerk | Countywide (city) |
| Municipal | City Treasurer | city_treasurer | Countywide (city) |
| Cook County | Commissioner | cook_commissioner | Filter by district_id |
| Cook County | Board President | cook_president | Countywide |
| Cook County | MWRD | mwrd | Countywide |
| Judicial | Circuit Court | circuit_court | Countywide |
| Judicial | Subcircuit | subcircuit | Filter by district_id |
| Judicial | Appellate Court | appellate_court | Countywide |
| Judicial | Supreme Court | supreme_court | Countywide |
| Education | School Board | school_board | Filter by district_id |
| State-wide | Governor | governor | Countywide |
| State-wide | U.S. Senate | us_senate | Countywide |
| State-wide | President | president | Countywide |
| State-wide | Attorney General | attorney_general | Countywide |
| State-wide | Secretary of State | secretary_of_state | Countywide |
| State-wide | Comptroller | comptroller | Countywide |
| State-wide | State Treasurer | treasurer_state | Countywide |

## Flow
1. On page load: fetch elections + load both GeoJSON files + compute ID lookup maps
2. User selects election → fetch races for that election
3. User picks district type → filter race list to matching race_type(s)
4. User picks specific race → fetch get_race_map(race_id)
5. Join precinct_id from API → GeoJSON features using pre-computed lookup
6. Color features based on current view mode
7. Show turnout data from get_race_turnout (cached per election)

## View Modes (8 total — keep all from current site)
1. **Turnout** — precinct turnout % heatmap (yellow=high, dark=low)
2. **Winner** — color each precinct by winning candidate
3. **Margin** — #1 vote% minus #2 vote% (red scale)
4. **Candidate** — single candidate's vote% (purple scale)
5. **Vs** — candidate A% minus candidate B% (blue/red diverging)
6. **Turnout Δ** — turnout change vs another election (green/red)
7. **Swing** — candidate % change vs another election (green/red)
8. **Votes** — total vote volume (blue scale)

## Critical Requirements
- Controls/election picker must be OFF the map (in toolbar, not floating overlay)
- Precincts with no data = gray (#333)
- Data via fetch() not inline
- Dark theme matching current design
- Info panel on hover showing precinct details
- Legend updates per view mode
- Header stats (registered, ballots, turnout, winner)
- Footer with data attribution + Perplexity attribution
- Mobile responsive
