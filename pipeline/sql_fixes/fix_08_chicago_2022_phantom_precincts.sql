-- D4D Data Integrity Fix
-- Generated: 2026-03-24 22:42:27
-- Chicago 2022 Primary phantom precinct documentation — 779 precincts
-- 
-- Run this against the Supabase database:
--   psql "$DATABASE_URL" -f fix_08_chicago_2022_phantom_precincts.sql
--
-- Or via Supabase SQL Editor.
-- ALWAYS verify row counts before and after.
--
-- BEGIN;   ← Uncomment to wrap in transaction
-- COMMIT;  ← Uncomment to commit

-- Fix 8: Chicago 2022 Primary Phantom Precincts
-- These 778 precincts are from the pre-redistricting ward map
-- They cannot be displayed on the current GeoJSON
-- Action: No deletion — data is correct, just unmappable.
-- Document them for future pre-redistricting GeoJSON work.

-- View the phantom precincts:
SELECT DISTINCT t.precinct_id, t.source_precinct_name
FROM turnout t
WHERE t.election_id = '2022_primary'
  AND t.source_file LIKE 'SBOE 2022 Primary - Chicago%'
  AND t.precinct_id NOT IN (
      SELECT DISTINCT precinct_id FROM turnout
      WHERE election_id = '2022_general'
        AND source_file LIKE 'SBOE 2022 General - Chicago%'
  )
ORDER BY source_precinct_name;

-- Total phantom count: 779

-- These precincts need a pre-redistricting Chicago GeoJSON
-- Source: City of Chicago Data Portal (boundaries vintage 2022-06)
-- URL: https://data.cityofchicago.org/Facilities-Geographic-Boundaries/
--      Ward-Precincts-2015-2023/uvpq-qeem