-- D4D Data Integrity Fix
-- Generated: 2026-03-24 22:37:03
-- Backfill NULL source_file in turnout table (4,367 rows across 3 elections)
-- 
-- Run this against the Supabase database:
--   psql "$DATABASE_URL" -f fix_05_null_source_files.sql
--
-- Or via Supabase SQL Editor.
-- ALWAYS verify row counts before and after.
--
-- BEGIN;   ← Uncomment to wrap in transaction
-- COMMIT;  ← Uncomment to commit

-- Fix 5: NULL source_file / source_precinct_name backfill

-- cook_2021_consolidated: 1601 rows with NULL source_file
-- Source label: 'Cook County Clerk'
UPDATE turnout
SET source_file = 'Cook County Clerk'
WHERE election_id = 'cook_2021_consolidated'
  AND source_file IS NULL;

-- Also backfill source_precinct_name for cook_2021_consolidated
-- (Cook precincts use numeric IDs stored in precincts table)
UPDATE turnout t
SET source_precinct_name = p.source_name
FROM precincts p
WHERE t.election_id = 'cook_2021_consolidated'
  AND t.source_precinct_name IS NULL
  AND t.precinct_id = p.id
  AND p.jurisdiction_id = 'cook_suburban';

-- cook_2023_consolidated: 1661 rows with NULL source_file
-- Source label: 'Cook County Clerk'
UPDATE turnout
SET source_file = 'Cook County Clerk'
WHERE election_id = 'cook_2023_consolidated'
  AND source_file IS NULL;

-- Also backfill source_precinct_name for cook_2023_consolidated
-- (Cook precincts use numeric IDs stored in precincts table)
UPDATE turnout t
SET source_precinct_name = p.source_name
FROM precincts p
WHERE t.election_id = 'cook_2023_consolidated'
  AND t.source_precinct_name IS NULL
  AND t.precinct_id = p.id
  AND p.jurisdiction_id = 'cook_suburban';

-- 2026_primary: 1105 rows with NULL source_file
-- Source label: 'cboe_2026_ajax'
UPDATE turnout
SET source_file = 'cboe_2026_ajax'
WHERE election_id = '2026_primary'
  AND source_file IS NULL;

-- 2026_primary: These are cboe_2026_ajax Chicago turnout rows
-- source_precinct_name is NULL — try to backfill from Chicago precincts
UPDATE turnout t
SET source_precinct_name = p.source_name
FROM precincts p
WHERE t.election_id = '2026_primary'
  AND t.source_precinct_name IS NULL
  AND t.precinct_id = p.id
  AND p.jurisdiction_id = 'chicago';

-- Verification: should return 0 rows after fix
SELECT election_id, COUNT(*) as null_source_rows
FROM turnout
WHERE election_id IN ('cook_2021_consolidated', 'cook_2023_consolidated', '2026_primary')
  AND source_file IS NULL
GROUP BY election_id;