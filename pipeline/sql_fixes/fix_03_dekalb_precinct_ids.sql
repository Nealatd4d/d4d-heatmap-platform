-- D4D Data Integrity Fix
-- Generated: 2026-03-24 22:37:10
-- DeKalb precinct_id rewrite — 47 zero-padded IDs to fix
-- 
-- Run this against the Supabase database:
--   psql "$DATABASE_URL" -f fix_03_dekalb_precinct_ids.sql
--
-- Or via Supabase SQL Editor.
-- ALWAYS verify row counts before and after.
--
-- BEGIN;   ← Uncomment to wrap in transaction
-- COMMIT;  ← Uncomment to commit

-- Fix 3: DeKalb Precinct ID Rewrite (zero-padding removal)
-- Maps old (zero-padded) precinct_ids to GeoJSON-canonical ids

CREATE TEMP TABLE IF NOT EXISTS dekalb_pid_mapping (
    old_id    TEXT PRIMARY KEY,
    new_id    TEXT NOT NULL,
    raw_name  TEXT,
    norm_name TEXT
);

INSERT INTO dekalb_pid_mapping (old_id, new_id, raw_name, norm_name) VALUES
    ('03244199ba197810', '3aa41b7b44710746', 'SYCAMORE 01', 'SYCAMORE 1'),
    ('0444b0507080f9de', 'fe8fc994a5707d46', 'SANDWICH 02', 'SANDWICH 2'),
    ('0ca9684e01826d17', 'efddb3fd6a5f8c2b', 'GENOA 02', 'GENOA 2'),
    ('10d8850d6a476ed8', '9ebe70a94f88103c', 'DEKALB 07', 'DEKALB 7'),
    ('113e4ebdc9d419fe', '659a37784f977693', 'SANDWICH 03', 'SANDWICH 3'),
    ('15c7c1f814e474c7', '67ab0a87fd8d668b', 'MAYFIELD 01', 'MAYFIELD 1'),
    ('191f351183b2a2c7', '5a4869a325f89f7c', 'CORTLAND 06', 'CORTLAND 6'),
    ('274e5027a79686e5', '4ea41e0ccb2fa4ea', 'SYCAMORE 08', 'SYCAMORE 8'),
    ('284512c9242a6d18', 'caa6b2332ec4fe18', 'DEKALB 02', 'DEKALB 2'),
    ('2b13bf9683d445b7', '4404f1800d4a4300', 'DEKALB 05', 'DEKALB 5'),
    ('3e82631c45920c45', 'eb9f50d60bf9ed8d', 'DEKALB 01', 'DEKALB 1'),
    ('42526b078e7253ff', '8dbd088adf6d5a82', 'CORTLAND 05', 'CORTLAND 5'),
    ('484d0f776271b1dc', '93227fac65fcddb8', 'CORTLAND 04', 'CORTLAND 4'),
    ('4b90dccb66d2e954', '804eb66e7b589230', 'SYCAMORE 03', 'SYCAMORE 3'),
    ('54b1278a9f79a745', 'a6951a71c3d93668', 'PIERCE 01', 'PIERCE 1'),
    ('5a7f3856b6dac316', '7e5c2a23239241d1', 'SANDWICH 01', 'SANDWICH 1'),
    ('5b333d983cd730fa', 'be1e515a0784a38e', 'SYCAMORE 09', 'SYCAMORE 9'),
    ('67187da4d7836eb7', '3663731fed9f18ff', 'SOMONAUK 01', 'SOMONAUK 1'),
    ('68e2f61e3d0abdf5', '9fb53271128972e2', 'SANDWICH 04', 'SANDWICH 4'),
    ('7082507539058daf', '74868fce2dc9a1bd', 'SHABBONA 01', 'SHABBONA 1'),
    ('713fbf8cb9faad54', '46e56575e563840b', 'DEKALB 08', 'DEKALB 8'),
    ('73cecd11d1065bf2', '915d2cc170fa287f', 'VICTOR 01', 'VICTOR 1'),
    ('74b1787fa24d9b25', 'a6f43af4e4fa66c0', 'CORTLAND 07', 'CORTLAND 7'),
    ('79a125b2562d64bf', 'fa428ddb307adb8c', 'SYCAMORE 06', 'SYCAMORE 6'),
    ('7ed6fd8addd5bf90', 'b78dd3231f57893d', 'SYCAMORE 07', 'SYCAMORE 7'),
    ('8c98860c724c0d16', 'e888160c09863280', 'MILAN 01', 'MILAN 1'),
    ('96d6cdb0dab25bc4', '64b2b802b38f945f', 'KINGSTON 01', 'KINGSTON 1'),
    ('9a3df029e6a42543', 'dacf03620ed1cdbc', 'DEKALB 04', 'DEKALB 4'),
    ('9a815eeef161d5de', 'cbe5dfc76c694687', 'SANDWICH 05', 'SANDWICH 5'),
    ('a2af4bb1b17e19ed', 'e258412ccd3f2c42', 'SOUTH GROVE 01', 'SOUTH GROVE 1'),
    ('ac19582150c5dc30', 'e1243b09ea90c0bc', 'FRANKLIN 01', 'FRANKLIN 1'),
    ('b61c2e03cf8d9524', 'e253f62ddd1930ca', 'GENOA 01', 'GENOA 1'),
    ('b8241f2389247a47', '1b873061034114b1', 'AFTON 01', 'AFTON 1'),
    ('be295f8e1f7d57fd', '6120b58ad1e1bee0', 'CORTLAND 01', 'CORTLAND 1'),
    ('c414af8e6ba85126', 'f1e7ed3c6084cde6', 'DEKALB 06', 'DEKALB 6'),
    ('c47ab2aafb66a5f2', '805f2597d04baad7', 'DEKALB 09', 'DEKALB 9'),
    ('ccf3c2da68824528', '1d6eed300eadd31d', 'SYCAMORE 02', 'SYCAMORE 2'),
    ('d133dbb41b3a8b4f', 'eb60380905b49d3c', 'DEKALB 03', 'DEKALB 3'),
    ('d43f5d5035a2de8c', '643fe8c44b1a9880', 'CLINTON 01', 'CLINTON 1'),
    ('da87bf6c651513a3', '326b55253ae62a75', 'CORTLAND 03', 'CORTLAND 3'),
    ('e20ecb9300fb3eaa', '44b32fc7c8573a78', 'SYCAMORE 04', 'SYCAMORE 4'),
    ('e43eb68fb58c163c', '38796d56811e9699', 'MALTA 01', 'MALTA 1'),
    ('ed01fb88302bf534', '038eda21359d1fe2', 'CORTLAND 08', 'CORTLAND 8'),
    ('f2e79d1eef613607', '78008cc62a001db4', 'PAW PAW 01', 'PAW PAW 1'),
    ('f55d5f0d6cc517a9', '01eda78d1290ce9f', 'CORTLAND 02', 'CORTLAND 2'),
    ('fc3f6dccdf9957f0', '00baaad6989fc894', 'SQUAW GROVE 01', 'SQUAW GROVE 1'),
    ('ffa1698e65cb9bdd', '587faec68f831fb7', 'SYCAMORE 05', 'SYCAMORE 5');

-- Update results
UPDATE results r
SET precinct_id = m.new_id,
    source_precinct_name = m.norm_name
FROM dekalb_pid_mapping m
WHERE r.precinct_id = m.old_id
  AND r.election_id IN ('2018_primary', '2018_general', '2020_primary', '2020_general');

-- Update turnout
UPDATE turnout t
SET precinct_id = m.new_id,
    source_precinct_name = m.norm_name
FROM dekalb_pid_mapping m
WHERE t.precinct_id = m.old_id
  AND t.election_id IN ('2018_primary', '2018_general', '2020_primary', '2020_general');

-- Verify: should see 65 precincts per election matching GeoJSON
SELECT election_id, COUNT(DISTINCT precinct_id) as dekalb_precincts
FROM results
WHERE election_id IN ('2018_primary', '2018_general', '2020_primary', '2020_general')
  AND source_file LIKE 'SBOE DeKalb%'
GROUP BY election_id;