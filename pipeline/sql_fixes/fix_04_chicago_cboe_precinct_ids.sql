-- D4D Data Integrity Fix
-- Generated: 2026-03-24 22:42:23
-- Chicago CBOE precinct normalization — 71 IDs to fix
-- 
-- Run this against the Supabase database:
--   psql "$DATABASE_URL" -f fix_04_chicago_cboe_precinct_ids.sql
--
-- Or via Supabase SQL Editor.
-- ALWAYS verify row counts before and after.
--
-- BEGIN;   ← Uncomment to wrap in transaction
-- COMMIT;  ← Uncomment to commit

-- Fix 4: Chicago CBOE Precinct ID Normalization
-- Converts unpadded (Ward 4 Precinct 1) to padded (Ward 04 Precinct 01)

CREATE TEMP TABLE IF NOT EXISTS chicago_pid_mapping (
    old_id    TEXT PRIMARY KEY,
    new_id    TEXT NOT NULL,
    raw_name  TEXT,
    norm_name TEXT,
    election_id TEXT
);

INSERT INTO chicago_pid_mapping (old_id, new_id, raw_name, norm_name, election_id) VALUES
    ('02bd01dffb0ebdd9', 'c2c607cd83a05b86', 'Ward 33 Precinct 8', 'Ward 33 Precinct 08', '2024_general'),
    ('02f5ddf4d7804633', '8a1c15739ff5bf28', 'Ward 29 Precinct 2', 'Ward 29 Precinct 02', '2024_general'),
    ('058fdbd084bb1ad9', '525950d8331d032e', 'Ward 39 Precinct 6', 'Ward 39 Precinct 06', '2024_general'),
    ('078a3cea8a5d9cb2', 'c6275a708cf6f4a1', 'Ward 38 Precinct 7', 'Ward 38 Precinct 07', '2024_general'),
    ('0b70d86af238b65d', '22695f1efb281204', 'Ward 45 Precinct 8', 'Ward 45 Precinct 08', '2024_general'),
    ('14f8d79ae23f3c14', '2d1967be3b3b108d', 'Ward 45 Precinct 7', 'Ward 45 Precinct 07', '2024_general'),
    ('199a9aecd4b1db59', '3838dc0cc4016103', 'Ward 30 Precinct 5', 'Ward 30 Precinct 05', '2024_general'),
    ('1bb4456e6c0a3bc5', '257c7f87e7e8ecc0', 'Ward 41 Precinct 3', 'Ward 41 Precinct 03', '2024_general'),
    ('21fa482138e9f046', '983bf3ec228ec9d4', 'Ward 39 Precinct 4', 'Ward 39 Precinct 04', '2024_general'),
    ('220e64e3dd7727dd', 'a8affd996392b466', 'Ward 40 Precinct 1', 'Ward 40 Precinct 01', '2024_general'),
    ('2745d0eb66549b0e', '09aae33ff429b397', 'Ward 38 Precinct 5', 'Ward 38 Precinct 05', '2024_general'),
    ('27f01db60acdb997', 'aca6fa0af6526291', 'Ward 40 Precinct 5', 'Ward 40 Precinct 05', '2024_general'),
    ('2af261dee845e8f0', 'b66bca79a02a2ea6', 'Ward 47 Precinct 3', 'Ward 47 Precinct 03', '2024_general'),
    ('2be8dc8e90230acf', 'e94a00f90d0dce2e', 'Ward 38 Precinct 3', 'Ward 38 Precinct 03', '2024_general'),
    ('3a24d9c53d16aeae', '070e18456f8454a5', 'Ward 36 Precinct 2', 'Ward 36 Precinct 02', '2024_general'),
    ('4047c2f996e660b9', 'f5146b479b6022b6', 'Ward 38 Precinct 2', 'Ward 38 Precinct 02', '2024_general'),
    ('440068170bbdc364', '6217ecba0a3c1684', 'Ward 30 Precinct 6', 'Ward 30 Precinct 06', '2024_general'),
    ('50458e7c8d3309b7', 'ee16840b65597d0a', 'Ward 47 Precinct 2', 'Ward 47 Precinct 02', '2024_general'),
    ('51804fbe443ee7a3', 'ae1c17c8e3a83339', 'Ward 39 Precinct 9', 'Ward 39 Precinct 09', '2024_general'),
    ('57f0332a1a05369f', 'd021c933015adfb5', 'Ward 29 Precinct 1', 'Ward 29 Precinct 01', '2024_general'),
    ('59ecc1c28c6ba60f', '9cf17da9fc5ea87b', 'Ward 30 Precinct 4', 'Ward 30 Precinct 04', '2024_general'),
    ('5b9ccb4ed7202f97', 'ccff391e499fc04f', 'Ward 36 Precinct 7', 'Ward 36 Precinct 07', '2024_general'),
    ('5d8ac7d15b6fbc73', 'e31abf8a7d18493b', 'Ward 29 Precinct 3', 'Ward 29 Precinct 03', '2024_general'),
    ('5f0e0ec9afb138df', '7b3c7ba687166374', 'Ward 40 Precinct 8', 'Ward 40 Precinct 08', '2024_general'),
    ('652c0fa92aab734c', '23d7057bd4edc483', 'Ward 36 Precinct 5', 'Ward 36 Precinct 05', '2024_general'),
    ('677a3f52cb446e4c', '5ad29e6ff49c068b', 'Ward 38 Precinct 8', 'Ward 38 Precinct 08', '2024_general'),
    ('69d1e6eed0a71e18', '8395a22fb480557a', 'Ward 40 Precinct 2', 'Ward 40 Precinct 02', '2024_general'),
    ('6c15cc86b1ce96c4', '5977f230c52a77f2', 'Ward 47 Precinct 6', 'Ward 47 Precinct 06', '2024_general'),
    ('706918da4d4aea1a', 'b6ca551340f40e4c', 'Ward 38 Precinct 6', 'Ward 38 Precinct 06', '2024_general'),
    ('72ec26a02f3b33ae', 'cf9597e4183b9a6a', 'Ward 41 Precinct 5', 'Ward 41 Precinct 05', '2024_general'),
    ('7a9d65b9081724f6', '1a56f2361510f38d', 'Ward 45 Precinct 9', 'Ward 45 Precinct 09', '2024_general'),
    ('7af4d9b3e26e7128', '45f6ac2c952bd775', 'Ward 47 Precinct 1', 'Ward 47 Precinct 01', '2024_general'),
    ('8909c989f4cd6a26', 'de84df2dcca1f12e', 'Ward 41 Precinct 8', 'Ward 41 Precinct 08', '2024_general'),
    ('890e66e4bc0ae883', '2ae08b269c391e43', 'Ward 39 Precinct 5', 'Ward 39 Precinct 05', '2024_general'),
    ('8e48ca41fc0505be', 'a2ab4050db6173f3', 'Ward 47 Precinct 4', 'Ward 47 Precinct 04', '2024_general'),
    ('8e5e21dd17655960', '609cb0f137628c66', 'Ward 36 Precinct 4', 'Ward 36 Precinct 04', '2024_general'),
    ('8fc8adebfe2ac981', 'd2ceb4376a4c048e', 'Ward 40 Precinct 7', 'Ward 40 Precinct 07', '2024_general'),
    ('909a863e3170f1c5', 'babae57266422214', 'Ward 41 Precinct 9', 'Ward 41 Precinct 09', '2024_general'),
    ('979ff9af12c38bce', 'f07bd3d26cf5a142', 'Ward 33 Precinct 2', 'Ward 33 Precinct 02', '2024_general'),
    ('99f9840c29cd4543', 'f7e83c668a62e9b4', 'Ward 39 Precinct 1', 'Ward 39 Precinct 01', '2024_general'),
    ('9c72d8acb7f35da1', 'cb671ea2917b1207', 'Ward 45 Precinct 3', 'Ward 45 Precinct 03', '2024_general'),
    ('9dd7f360b7de2480', '6edc89fbae1875e1', 'Ward 36 Precinct 3', 'Ward 36 Precinct 03', '2024_general'),
    ('a2a48b3c8ab1b7f0', 'dfe9b1553064660f', 'Ward 41 Precinct 1', 'Ward 41 Precinct 01', '2024_general'),
    ('a405738608d4a84c', '77249ec1f9c13d01', 'Ward 40 Precinct 3', 'Ward 40 Precinct 03', '2024_general'),
    ('a4bfe8b04e6b620d', '577f46d198d0aea7', 'Ward 38 Precinct 9', 'Ward 38 Precinct 09', '2024_general'),
    ('a4f40e533679e245', '67bc5c8d96426cbc', 'Ward 41 Precinct 6', 'Ward 41 Precinct 06', '2024_general'),
    ('ac4fa6cb2e90116c', '8db80d6193d98e22', 'Ward 41 Precinct 4', 'Ward 41 Precinct 04', '2024_general'),
    ('aff085789a95f24e', '063b60f9df999ea9', 'Ward 38 Precinct 4', 'Ward 38 Precinct 04', '2024_general'),
    ('b511147eb14b9596', '547b729ba1ad7818', 'Ward 41 Precinct 7', 'Ward 41 Precinct 07', '2024_general'),
    ('b56f28b700891653', '0be9dc17ec87fb2f', 'Ward 40 Precinct 4', 'Ward 40 Precinct 04', '2024_general'),
    ('b5ae51ae4046bca3', '9630b5bff0e6e16d', 'Ward 36 Precinct 1', 'Ward 36 Precinct 01', '2024_general'),
    ('bb603456ca3d1e9a', '19efc9bc32cfb545', 'Ward 47 Precinct 5', 'Ward 47 Precinct 05', '2024_general'),
    ('bdad90df5695b8ea', '38630e8258f8393a', 'Ward 36 Precinct 6', 'Ward 36 Precinct 06', '2024_general'),
    ('c024a66a9a76e1cc', '2e5a31344ac76db4', 'Ward 40 Precinct 6', 'Ward 40 Precinct 06', '2024_general'),
    ('c0a995cf6d710d8c', '10fc4b184d56a027', 'Ward 45 Precinct 4', 'Ward 45 Precinct 04', '2024_general'),
    ('c11384ae506d9919', 'e8dd3f47a7ee5980', 'Ward 39 Precinct 3', 'Ward 39 Precinct 03', '2024_general'),
    ('c50bdbd501c3ed6b', 'c938cf45667c8dac', 'Ward 39 Precinct 7', 'Ward 39 Precinct 07', '2024_general'),
    ('c7952585e0578d14', '6a0e6949e14f3070', 'Ward 40 Precinct 9', 'Ward 40 Precinct 09', '2024_general'),
    ('ce081379e0d00b9c', '2ff6547b210e40de', 'Ward 45 Precinct 1', 'Ward 45 Precinct 01', '2024_general'),
    ('d0838a61f73cf6ab', '346149cbccdc057f', 'Ward 45 Precinct 6', 'Ward 45 Precinct 06', '2024_general'),
    ('d2a75cbc3d4042df', '388e20227c8452cb', 'Ward 38 Precinct 1', 'Ward 38 Precinct 01', '2024_general'),
    ('d2ba87906171adab', '34332fe32196ea9d', 'Ward 30 Precinct 2', 'Ward 30 Precinct 02', '2024_general'),
    ('d46b89ea1c67e548', '22f1d98dd225362d', 'Ward 30 Precinct 9', 'Ward 30 Precinct 09', '2024_general'),
    ('da15199c078c0b6f', '298f822e3c18a3f4', 'Ward 39 Precinct 2', 'Ward 39 Precinct 02', '2024_general'),
    ('dde15f37300df268', 'a86c3a37edbdcd80', 'Ward 45 Precinct 2', 'Ward 45 Precinct 02', '2024_general'),
    ('e063e94ba336da66', 'f135deea79c838a8', 'Ward 39 Precinct 8', 'Ward 39 Precinct 08', '2024_general'),
    ('e7e880a718ab3e17', 'ac1ea0fb85341d15', 'Ward 30 Precinct 3', 'Ward 30 Precinct 03', '2024_general'),
    ('ea2437cf80616d2c', '3defcc03b3ed142c', 'Ward 41 Precinct 2', 'Ward 41 Precinct 02', '2024_general'),
    ('f54c4e241cbed551', '7d6c23293af3cfb1', 'Ward 50 Precinct 4', 'Ward 50 Precinct 04', '2024_general'),
    ('fc3ed192998f3f01', '1b23329a7d2a094f', 'Ward 45 Precinct 5', 'Ward 45 Precinct 05', '2024_general'),
    ('fe0f0705af257728', 'e9644ca90fe67f41', 'Ward 30 Precinct 1', 'Ward 30 Precinct 01', '2024_general');

-- Update results
UPDATE results r
SET precinct_id = m.new_id
FROM chicago_pid_mapping m
WHERE r.precinct_id = m.old_id;

-- Update turnout
UPDATE turnout t
SET precinct_id = m.new_id
FROM chicago_pid_mapping m
WHERE t.precinct_id = m.old_id;