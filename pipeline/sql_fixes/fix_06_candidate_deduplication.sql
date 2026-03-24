-- D4D Data Integrity Fix
-- Generated: 2026-03-24 22:41:42
-- Candidate deduplication — 1144 merges, 13 party normalizations
-- 
-- Run this against the Supabase database:
--   psql "$DATABASE_URL" -f fix_06_candidate_deduplication.sql
--
-- Or via Supabase SQL Editor.
-- ALWAYS verify row counts before and after.
--
-- BEGIN;   ← Uncomment to wrap in transaction
-- COMMIT;  ← Uncomment to commit

-- Fix 6: Candidate Deduplication + Party Normalization
-- Merges 1144 duplicate candidate IDs
-- Normalizes 600 party labels

-- ============================================================
-- STEP 1: Remap results rows from duplicate IDs to canonical IDs
-- ============================================================

-- Batch 1
UPDATE results SET candidate_id = 'af921dbeae923444' WHERE candidate_id = '8375bbeb0a05dbb6';  -- AARON GOLDSTEIN
UPDATE results SET candidate_id = 'c568350990d8ee6e' WHERE candidate_id = '6632397dde7c74af';  -- ALEXI GIANNOULIAS
UPDATE results SET candidate_id = 'c568350990d8ee6e' WHERE candidate_id = 'fefd22a72d7a06e0';  -- ALEXI GIANNOULIAS
UPDATE results SET candidate_id = '3ec13bed3c774738' WHERE candidate_id = 'eed3dd18560030b4';  -- ALISON SQUIRES
UPDATE results SET candidate_id = '23d17bfcd224a836' WHERE candidate_id = '19690f9a8d0d184b';  -- AMANDA HOWLAND
UPDATE results SET candidate_id = 'a5a3430ee1df42fb' WHERE candidate_id = '805f450890f6d02c';  -- AMY "MURRI" BRIEL
UPDATE results SET candidate_id = 'aaf03f67c19beb0d' WHERE candidate_id = '23ed927c3f34dde6';  -- AMY L. GRANT
UPDATE results SET candidate_id = '2b33d9ae631f8acb' WHERE candidate_id = 'b495280186a53879';  -- ANDREA HEEG
UPDATE results SET candidate_id = 'e2e33e3187ade367' WHERE candidate_id = 'dea08a5752eed647';  -- ANDREW S. CHESNEY
UPDATE results SET candidate_id = '195c54555babed48' WHERE candidate_id = '1bd6b369caad06c2';  -- ANNA M. VALENCIA
UPDATE results SET candidate_id = 'aab7c4ba05f4e36a' WHERE candidate_id = '5c1fe4a8aca59202';  -- ANNE STAVA-MURRAY
UPDATE results SET candidate_id = 'faf6c8276f187432' WHERE candidate_id = 'ebcdfb34a748553e';  -- ANTHONY AIRDO
UPDATE results SET candidate_id = '7a1782f7323c8a1c' WHERE candidate_id = '5ab0f84f3e515e6c';  -- ANTHONY W. WILLIAMS
UPDATE results SET candidate_id = '77f1d99f45081a09' WHERE candidate_id = '319285a0366cf8dd';  -- AZAM NIZAMUDDIN
UPDATE results SET candidate_id = '321e1e3b596340ec' WHERE candidate_id = '4020edae195d061a';  -- Aaron Peppers
UPDATE results SET candidate_id = '7519be971b056459' WHERE candidate_id = '515c736b21f6c7df';  -- Adriane L. Johnson
UPDATE results SET candidate_id = '880a4c998a341e0d' WHERE candidate_id = 'b48d862acb1afbdd';  -- Alesia Franklin-Allen
UPDATE results SET candidate_id = '6c2e461d8bcff87c' WHERE candidate_id = 'e27e613bfe2e5116';  -- Alex Beck
UPDATE results SET candidate_id = '6d49e8d09ebceecc' WHERE candidate_id = '939d1044a52bfb1d';  -- Alexandria Zuck
UPDATE results SET candidate_id = 'cf7b6561d57328d1' WHERE candidate_id = 'ef8701af2dd97747';  -- Alfred Sanchez
UPDATE results SET candidate_id = '454ef7ed959c3c11' WHERE candidate_id = 'ccbe364db2836b0a';  -- Alice Couch
UPDATE results SET candidate_id = '6818395abd3bb1d0' WHERE candidate_id = 'befb522afb177258';  -- Alice LeVert
UPDATE results SET candidate_id = '222003c3321b99c3' WHERE candidate_id = '7c919e13b494f99c';  -- Alice M Balundis
UPDATE results SET candidate_id = '316c0a52e98fe850' WHERE candidate_id = 'd4b0a9342ac26058';  -- Alison Key
UPDATE results SET candidate_id = '26a3deab28f454ee' WHERE candidate_id = '67fafe2d93e2adb0';  -- Alison Pure Slovin
UPDATE results SET candidate_id = '0427472aab5b7702' WHERE candidate_id = '9f8fea4b0bec32d6';  -- Allen M. Moskal
UPDATE results SET candidate_id = '121315962f920ff6' WHERE candidate_id = '73f225f27a3fdff2';  -- Allison M. Downs
UPDATE results SET candidate_id = '18973c711b6ae112' WHERE candidate_id = 'd281566113b4e34e';  -- Allison R. McCray
UPDATE results SET candidate_id = '1d567fbe86c51c54' WHERE candidate_id = '2df4f47471ec0cbc';  -- Andrea Creger
UPDATE results SET candidate_id = 'eba14af30c0d6c99' WHERE candidate_id = '464d8aaa6df5cb28';  -- Andrew Catton
UPDATE results SET candidate_id = '1b15787218e9bc03' WHERE candidate_id = '2a5bea2dda736944';  -- Andrew Goczkowski
UPDATE results SET candidate_id = 'ac5581ff24fa745a' WHERE candidate_id = '3a08e45dead6a70e';  -- Andrew McMahon
UPDATE results SET candidate_id = '3d043c56a812d0b4' WHERE candidate_id = '1361f3a045f1edab';  -- Andrew Stein
UPDATE results SET candidate_id = '3dcf0f8a8664899c' WHERE candidate_id = '85d8844f2e7481a8';  -- Andy-John G. Kalkounos
UPDATE results SET candidate_id = '38e3de839262e303' WHERE candidate_id = '6dc1e3651a0209fc';  -- Anne Ordway
UPDATE results SET candidate_id = '0508ffe2bbc7bf2e' WHERE candidate_id = 'a8e9a6f3cbc3b536';  -- Annette Brzezniak-Volpe
UPDATE results SET candidate_id = 'ffcc55875a182326' WHERE candidate_id = '0cc8f5cb3302e1b2';  -- Annette Whittington
UPDATE results SET candidate_id = '6380b30616768cb7' WHERE candidate_id = '78dd885c0b5a7199';  -- Anthony "Tony" Williams
UPDATE results SET candidate_id = '19e476850ca76f2f' WHERE candidate_id = '203069e9149c7044';  -- Anthony Grazzini
UPDATE results SET candidate_id = '2b75e5b0a7b350a3' WHERE candidate_id = '4bb49a313253cdf8';  -- Anthony J. Nasca
UPDATE results SET candidate_id = 'fb55d324e269ef6b' WHERE candidate_id = '3b7f28475c2e74fb';  -- Anthony Michael Tamez
UPDATE results SET candidate_id = '04bbd09db30e6d81' WHERE candidate_id = '53eb71eae9e1faa9';  -- Anthony Vega
UPDATE results SET candidate_id = '57fdcfb8692cbbac' WHERE candidate_id = 'db63376dbf0b9cde';  -- Antoinette Cronin
UPDATE results SET candidate_id = 'a198ffb09ff2be70' WHERE candidate_id = 'c0993c4de1f25392';  -- Antonina White
UPDATE results SET candidate_id = 'a2780f24b90e13a7' WHERE candidate_id = 'e4bf5abe6e660239';  -- April J. Arellano
UPDATE results SET candidate_id = '31ee987636f4ce11' WHERE candidate_id = 'fa0a580713c8c732';  -- Aracely Gutierrez
UPDATE results SET candidate_id = 'ad4d6a19b12a088d' WHERE candidate_id = '56ad77decf9eb52b';  -- Aretha Burns
UPDATE results SET candidate_id = '8b410bd60c7768ba' WHERE candidate_id = '218990c14e07cc9c';  -- Arlene M. "Sugar" Al-Amin
UPDATE results SET candidate_id = '240990f14a5d6ae7' WHERE candidate_id = 'b9ef7c8e96e56a1b';  -- Arnold Coleman
UPDATE results SET candidate_id = '7af984b684e70e13' WHERE candidate_id = 'eb59e36c8d49f847';  -- Arturo J. Mota
UPDATE results SET candidate_id = 'dc5dd9f6205de8e4' WHERE candidate_id = 'fa52c53d2a3e53f7';  -- Ashley Jensen
UPDATE results SET candidate_id = '6ac9648d5af5f221' WHERE candidate_id = '9f5bdc161e4cbff0';  -- Asif Mahmood Malik
UPDATE results SET candidate_id = 'cada21a64c648145' WHERE candidate_id = 'c711e72d03b1c494';  -- Asif Yusuf
UPDATE results SET candidate_id = '7a37db6cfb4771e9' WHERE candidate_id = '987afc24f3cc3175';  -- Athena Arvanitis
UPDATE results SET candidate_id = '1373d31522ed1d5e' WHERE candidate_id = 'db7e0f99d51e6d62';  -- BARBARA HERNANDEZ
UPDATE results SET candidate_id = '1373d31522ed1d5e' WHERE candidate_id = '30aaa6e3e115b978';  -- BARBARA HERNANDEZ
UPDATE results SET candidate_id = 'ac2eeee335f8f611' WHERE candidate_id = 'd6db51d3ea527638';  -- BEVERLY MILES
UPDATE results SET candidate_id = 'e5445f6185751317' WHERE candidate_id = 'f2322f43e360cd81';  -- BILL FOSTER
UPDATE results SET candidate_id = 'e5445f6185751317' WHERE candidate_id = '58c43369646b312f';  -- BILL FOSTER
UPDATE results SET candidate_id = 'e5445f6185751317' WHERE candidate_id = 'c2aef63330c4996f';  -- BILL FOSTER
UPDATE results SET candidate_id = '2a76fcea3c4caa63' WHERE candidate_id = '22c67cfe82044eff';  -- BILL REDPATH
UPDATE results SET candidate_id = '2a76fcea3c4caa63' WHERE candidate_id = '06d2a72fe6f568cd';  -- BILL REDPATH
UPDATE results SET candidate_id = 'ec6b4f0501090876' WHERE candidate_id = '5c63f659ec8b90e5';  -- BOB DAIBER
UPDATE results SET candidate_id = '016172dfb588ff4c' WHERE candidate_id = 'b0079320ae4e49d2';  -- BOB MORGAN
UPDATE results SET candidate_id = '4610e81fe41f4073' WHERE candidate_id = '136126122543127e';  -- BRAD SCHNEIDER
UPDATE results SET candidate_id = '5f8c5308e758a614' WHERE candidate_id = 'b37ed5eaf6819404';  -- BRADLEY J. FRITTS
UPDATE results SET candidate_id = 'd77daca0611582f1' WHERE candidate_id = 'eb4a26c87c35b1d7';  -- BRIAN CARROLL
UPDATE results SET candidate_id = 'd77daca0611582f1' WHERE candidate_id = '007a7a5bd7a8f06f';  -- BRIAN CARROLL
UPDATE results SET candidate_id = 'e1d361b1590a0890' WHERE candidate_id = 'ea4bea8445839f70';  -- Barbara Gagle
UPDATE results SET candidate_id = '5c8293172ab7beb1' WHERE candidate_id = '7bb485375e4d8ca8';  -- Barbara M. Harrison
UPDATE results SET candidate_id = '059c4e712baa3c44' WHERE candidate_id = '6691be728692627f';  -- Barrett F. Pedersen
UPDATE results SET candidate_id = '7d65a939911a8fbb' WHERE candidate_id = 'fb812df2da6558e1';  -- Barry Altshuler
UPDATE results SET candidate_id = 'e155c2470ed48596' WHERE candidate_id = '7a4b0a1d7706634d';  -- Barry Wicker
UPDATE results SET candidate_id = '407b42f42962800c' WHERE candidate_id = '66a0f0c92659bd49';  -- Becky Walters
UPDATE results SET candidate_id = '3531646c35453ca9' WHERE candidate_id = 'a5be4df7cab51e76';  -- Belia Nowak
UPDATE results SET candidate_id = '73720ca7be44b0db' WHERE candidate_id = 'e8f76171cb833233';  -- Beniamino Mazzulla
UPDATE results SET candidate_id = 'e72803f101eeb023' WHERE candidate_id = 'cd6b5a0365736ef0';  -- Benny Williams
UPDATE results SET candidate_id = '255cb3e3685f9dd6' WHERE candidate_id = 'a6320160d45b2096';  -- Bernadette Lawrence
UPDATE results SET candidate_id = '7466d8bb2a0ddb25' WHERE candidate_id = '5e1210c120f1661b';  -- Beth Bazer
UPDATE results SET candidate_id = 'ea587fc88c23cf96' WHERE candidate_id = '1c6a1ba179baec30';  -- Bethany Johnson
UPDATE results SET candidate_id = 'a01c26c5b3608d08' WHERE candidate_id = 'f296bdb4ea9b4a60';  -- Beverly Sugar Young
UPDATE results SET candidate_id = 'dbae4e9d2aef7fb3' WHERE candidate_id = 'e66e4f7cb7cada8b';  -- Bill Knapik
UPDATE results SET candidate_id = '1d13790132d55b8a' WHERE candidate_id = '063745d2ed6266e2';  -- Blank Ballots
UPDATE results SET candidate_id = '1d13790132d55b8a' WHERE candidate_id = 'e929b8331c2cfb09';  -- Blank Ballots
UPDATE results SET candidate_id = '1d13790132d55b8a' WHERE candidate_id = 'e4d22bf6a35355e4';  -- Blank Ballots
UPDATE results SET candidate_id = '2696639ece992e29' WHERE candidate_id = 'ffe5ba9238bf7214';  -- Bob Kaplan
UPDATE results SET candidate_id = '951ce0b1d79cdb73' WHERE candidate_id = '8e4464606820a1bb';  -- Bob Morgan
UPDATE results SET candidate_id = '7f123a739b292eae' WHERE candidate_id = 'ba2822fea64aa103';  -- Bobby Burns
UPDATE results SET candidate_id = '487bf206e2b38b46' WHERE candidate_id = '5eebc37de3fac118';  -- Bozena Ryt
UPDATE results SET candidate_id = '1639b6a80d35d0c8' WHERE candidate_id = '7a2eac69435b2c3d';  -- Brad Helms
UPDATE results SET candidate_id = 'e390bada1c9ff48f' WHERE candidate_id = '877b322cf3303379';  -- Brad Schneider
UPDATE results SET candidate_id = '3a96c6e0886554c6' WHERE candidate_id = '9495152f67f46786';  -- Bradley A. Smith
UPDATE results SET candidate_id = '70e2f68d87e995d4' WHERE candidate_id = 'f57ab3694a8b66a1';  -- Bradley A. Stephens
UPDATE results SET candidate_id = '19ead4dde209c29e' WHERE candidate_id = '8a31544b73a2086c';  -- Branard Barrett
UPDATE results SET candidate_id = 'c5a25923825748ac' WHERE candidate_id = '8756fd4aa2b398ff';  -- Brent Joseph Burval
UPDATE results SET candidate_id = '12c985086382b73a' WHERE candidate_id = '8deb6bece5a079b6';  -- Brian A. Waight
UPDATE results SET candidate_id = '4c4793b9599bf80e' WHERE candidate_id = '65f0711884a89ea8';  -- Brian D. Cecola
UPDATE results SET candidate_id = '4c4793b9599bf80e' WHERE candidate_id = 'e324bea054cb3ea5';  -- Brian D. Cecola
UPDATE results SET candidate_id = '792bc60da682ec21' WHERE candidate_id = '088a1cc7488a5349';  -- Brian Gilligan
UPDATE results SET candidate_id = '4f93c65027c792d0' WHERE candidate_id = '9f99b37adc218271';  -- Brian Lichtenberger
UPDATE results SET candidate_id = '3907acf14905f8b5' WHERE candidate_id = '8019b839b36aaf6d';  -- Brian Nichols
UPDATE results SET candidate_id = '4fde0179ef686974' WHERE candidate_id = '7c07936b3ab22863';  -- Brian P. Hardy
UPDATE results SET candidate_id = '4f78a69939685f6d' WHERE candidate_id = 'f3d76dd4bae433a0';  -- Brian Perkovich
UPDATE results SET candidate_id = 'dda1f4f9b9c06943' WHERE candidate_id = '0b0e460d2c3840a1';  -- Brian Prigge
UPDATE results SET candidate_id = '604b68c0b2c2d962' WHERE candidate_id = '1939a3ea4c34f376';  -- Brian Skala
UPDATE results SET candidate_id = '5159490672b1c7bd' WHERE candidate_id = 'b7eaa5dc9c06b863';  -- Bridget Orsic
UPDATE results SET candidate_id = '15b88d7d60970366' WHERE candidate_id = '5a3d9442af3638c9';  -- Broderick L. Booth
UPDATE results SET candidate_id = 'fbce6be53c2e090a' WHERE candidate_id = 'a725ba2529d24124';  -- Bruce D. Matthews
UPDATE results SET candidate_id = 'f1a1eacb430a17a0' WHERE candidate_id = 'b81bad94896391dd';  -- Bruce Owens, Jr.
UPDATE results SET candidate_id = '327ce4b1720b5318' WHERE candidate_id = '66e6c7e3142e5937';  -- Bushra Amiwala
UPDATE results SET candidate_id = '63bb890330f7f303' WHERE candidate_id = '51fe34afd9fa21de';  -- CASEY CHLEBEK
UPDATE results SET candidate_id = '63bb890330f7f303' WHERE candidate_id = '43f0184d48719794';  -- CASEY CHLEBEK
UPDATE results SET candidate_id = '0ea51a868de00d9d' WHERE candidate_id = '1d696e663ea55758';  -- CASSANDRA TANNER MILLER
UPDATE results SET candidate_id = '7eb8e8200f8aad2d' WHERE candidate_id = '1ec3c77584d5e1e7';  -- CATALINA LAUF
UPDATE results SET candidate_id = '1cb7adc2469129fc' WHERE candidate_id = '86bb4e88c3fed409';  -- CATHERINE A. O''SHEA
UPDATE results SET candidate_id = '68d175c18f76a99b' WHERE candidate_id = '3c304515e0968f9d';  -- CHARLES M. HUGHES
UPDATE results SET candidate_id = '42d5822a5c680303' WHERE candidate_id = '568b3e6c8ea2b7dc';  -- CHARLIE KIM
UPDATE results SET candidate_id = 'a3c091d75368dde7' WHERE candidate_id = 'c3a5628dac7de2c4';  -- CHRIS BOS
UPDATE results SET candidate_id = '5077303ab7361eec' WHERE candidate_id = '4da69bda6645929d';  -- CHRIS DARGIS
UPDATE results SET candidate_id = '57d87802d29b9b60' WHERE candidate_id = '1840fde0765a90bc';  -- CHRIS DONAHUE
UPDATE results SET candidate_id = '879575d26470fa62' WHERE candidate_id = '0c3ddc7c7420f9da';  -- CHRIS KENNEDY
UPDATE results SET candidate_id = '9bb9419520180f3e' WHERE candidate_id = '2dee6c2aa455d698';  -- CHRIS METCALFE
UPDATE results SET candidate_id = '9bb9419520180f3e' WHERE candidate_id = '7aa66e403249faea';  -- CHRIS METCALFE
UPDATE results SET candidate_id = '39563887c4dfa363' WHERE candidate_id = 'b5c5ae02b8887701';  -- CHRISTINE BENSON
UPDATE results SET candidate_id = '27c0c8b86eb16807' WHERE candidate_id = 'c4cf798dfa9a5384';  -- CHRISTOPHER ESPINOZA
UPDATE results SET candidate_id = 'ad68198d5a164469' WHERE candidate_id = 'cc17644f269a9235';  -- CHRISTOPHER J. TENNYSON
UPDATE results SET candidate_id = '8c0d34e9696795a0' WHERE candidate_id = 'c58a741b53e86695';  -- CHRISTOPHER KASPERSKI
UPDATE results SET candidate_id = 'f61ee52cc4b0421a' WHERE candidate_id = '8bc4a4ba1dcc8217';  -- CHRISTOPHER MOROZIN
UPDATE results SET candidate_id = 'd136dfb239e69793' WHERE candidate_id = '48e968e24bbdf16b';  -- CRISTINA CASTRO
UPDATE results SET candidate_id = 'd136dfb239e69793' WHERE candidate_id = 'b7245f4670896b0a';  -- CRISTINA CASTRO
UPDATE results SET candidate_id = 'd1437fc2ff7f8ff1' WHERE candidate_id = '9713db292ca05ddc';  -- CRYSTAL LOUGHRAN
UPDATE results SET candidate_id = 'd89296b54c91c307' WHERE candidate_id = 'd7101a44f8f60cf5';  -- CYNTHIA BORBAS
UPDATE results SET candidate_id = '92497d15cba47e2f' WHERE candidate_id = '026e25baded40b9d';  -- CYNTHIA M. SANTOS
UPDATE results SET candidate_id = '92497d15cba47e2f' WHERE candidate_id = 'a69968d49305960f';  -- CYNTHIA M. SANTOS
UPDATE results SET candidate_id = '23a2a3ec7f1400ad' WHERE candidate_id = '38b1a4bcde4509eb';  -- Caitlyn Keenan
UPDATE results SET candidate_id = '2cf5935f299c7686' WHERE candidate_id = '6bf4499242c27f69';  -- Calvin Jordan
UPDATE results SET candidate_id = 'd40ef23f0f54190b' WHERE candidate_id = 'd59b0f19a7a24299';  -- Candace Carr
UPDATE results SET candidate_id = '9480fefd9c0b3b39' WHERE candidate_id = 'ff25f9a7cd20998c';  -- Candice Cantelo
UPDATE results SET candidate_id = '0c204dbe825b292a' WHERE candidate_id = '63758be9cbdc1faa';  -- Carissa Casbon
UPDATE results SET candidate_id = '486ab5c64417c360' WHERE candidate_id = '64a50954e70463cf';  -- Carl Lambrecht
UPDATE results SET candidate_id = '486ab5c64417c360' WHERE candidate_id = '222fa2c836cad0b9';  -- Carl Lambrecht
UPDATE results SET candidate_id = 'f4f3966e8a568704' WHERE candidate_id = 'a06d566d28ccdced';  -- Carl R. Kunz
UPDATE results SET candidate_id = '1b4285091b762780' WHERE candidate_id = '782526a1f0fb225a';  -- Carla Brookman
UPDATE results SET candidate_id = '15f82c8aa6a8d51b' WHERE candidate_id = '3047504ac2f22954';  -- Carol Kyle
UPDATE results SET candidate_id = 'b87c9ed5a7f8a694' WHERE candidate_id = 'a69ed56378942ebc';  -- Carolyn G. Palmer
UPDATE results SET candidate_id = '129f8a35ece51b90' WHERE candidate_id = '2735c2014cd2539d';  -- Carolyn Griggs
UPDATE results SET candidate_id = '0697d07f6377e7d3' WHERE candidate_id = '63f82badea9a347b';  -- Carolyn R. Carter
UPDATE results SET candidate_id = 'a6ab71cd2e026e0e' WHERE candidate_id = 'f9182c847a6f4a39';  -- Carrie F. Carr
UPDATE results SET candidate_id = '93db9e788b51beee' WHERE candidate_id = 'de418207a2d3c30a';  -- Casey Nesbit
UPDATE results SET candidate_id = 'bcfebd7a614a1169' WHERE candidate_id = 'bd336c3e95dd5c4b';  -- Cassie Hill
UPDATE results SET candidate_id = '3034cfc012cee2ea' WHERE candidate_id = 'a02fcf7204599d3e';  -- Catherine Boettcher
UPDATE results SET candidate_id = '1ec385ff28bc7256' WHERE candidate_id = 'cd058f08ab4a4fa2';  -- Catherine M. Adduci
UPDATE results SET candidate_id = '4442eb03ed08f06b' WHERE candidate_id = 'acea0734e7c2422f';  -- Cesar Garcia
UPDATE results SET candidate_id = '48f4b85f2e72dc41' WHERE candidate_id = 'bd776e969ec03cb1';  -- Charlene McFadden
UPDATE results SET candidate_id = '3be506bf8466ecca' WHERE candidate_id = 'beacbcb67debdcc4';  -- Charles A. Garcia
UPDATE results SET candidate_id = 'b9d68c5dbec45cf9' WHERE candidate_id = 'dd58a8a4ff9f6879';  -- Charles Eck
UPDATE results SET candidate_id = '10d97920928e3598' WHERE candidate_id = 'd83c65e81ddf7c30';  -- Charles Levy
UPDATE results SET candidate_id = '29dcc918a3154e90' WHERE candidate_id = '29fc6b73c493e7a0';  -- Charles Orth
UPDATE results SET candidate_id = '422cb607f281e063' WHERE candidate_id = '3ec4740463ae5590';  -- Chase Heidner
UPDATE results SET candidate_id = '66f2b6aef7c64c91' WHERE candidate_id = '3dbe2110cd78e01a';  -- Cheri Klumpp
UPDATE results SET candidate_id = '7dce36cb5dcbb321' WHERE candidate_id = '97a18d4b61dd43ed';  -- Cheryl A. Grant
UPDATE results SET candidate_id = '2d7dbc783fccff56' WHERE candidate_id = '6a8d1948ae32c238';  -- Cheryl Y. Franklin
UPDATE results SET candidate_id = '05d599a26846809e' WHERE candidate_id = 'bf9c26483829c161';  -- Christina Rodriguez
UPDATE results SET candidate_id = '1c4aa23d202db93a' WHERE candidate_id = 'e89db606c73cc2cc';  -- Christine Birkett
UPDATE results SET candidate_id = '034cde50b0bf2ef9' WHERE candidate_id = 'f7895840cd02d733';  -- Christopher "Chris" Clark
UPDATE results SET candidate_id = 'a24f7f2251890bbb' WHERE candidate_id = '24887b7ac7bfd581';  -- Christopher M. Goodsnyder
UPDATE results SET candidate_id = '5c12d3b9bc03e62a' WHERE candidate_id = 'a027330d9db55b2c';  -- Christopher Ottsen
UPDATE results SET candidate_id = '1357f2efbbe192c7' WHERE candidate_id = '3a6bd80cd2694329';  -- Chun Ye
UPDATE results SET candidate_id = '123be5f1e49ad957' WHERE candidate_id = 'd21af8009faf6f69';  -- Cindy Trotier
UPDATE results SET candidate_id = '504df532d87d208f' WHERE candidate_id = '6a7d67c466b8fcf7';  -- Clara I. Bruno
UPDATE results SET candidate_id = '1aeddb55463b25a8' WHERE candidate_id = '5cbb6a306cc374ca';  -- Claudell Johnson
UPDATE results SET candidate_id = '67b83a501cb11923' WHERE candidate_id = '8d9722a83f9383d9';  -- Claudia Alvarez
UPDATE results SET candidate_id = 'c91188bb6c4e9380' WHERE candidate_id = '6f8cf349e93056a2';  -- Claudia Fonseca
UPDATE results SET candidate_id = 'c3b29c2a74aaec89' WHERE candidate_id = '4918874179496631';  -- Clyde J. McLemore
UPDATE results SET candidate_id = '75d37a71a9bbee33' WHERE candidate_id = '08c1fc12a6d8c369';  -- Clyde McLemore
UPDATE results SET candidate_id = '05f6abc8c4b4288b' WHERE candidate_id = 'c85523aa6a8a08de';  -- Colleen M. Lambert
UPDATE results SET candidate_id = '88c914dee403bfdb' WHERE candidate_id = 'b65ef00df33e575f';  -- Colleen Sullivan
UPDATE results SET candidate_id = '0b4b0059aae941fb' WHERE candidate_id = '4a1ebc828aad2dae';  -- Coryn Steinfeld
UPDATE results SET candidate_id = '28144bfc063efa7a' WHERE candidate_id = 'a4704649cc4f9dda';  -- Craig B. Johnson
UPDATE results SET candidate_id = '99fea65698cf714c' WHERE candidate_id = 'e3962498c3b17301';  -- Craig F. Schmidt
UPDATE results SET candidate_id = '4c89a34ddc9e7078' WHERE candidate_id = '2ea5af39b00aa82b';  -- Craig Wilcox
UPDATE results SET candidate_id = '03581847afefa75c' WHERE candidate_id = 'f4fc5405ce9918ec';  -- Cristel Mohrman
UPDATE results SET candidate_id = '4d52cbd894f01874' WHERE candidate_id = 'a0c1c20a6af37c75';  -- Curtis L. Petrey
UPDATE results SET candidate_id = '576f07da627d0282' WHERE candidate_id = 'ef0d4986cb191955';  -- Curtis Straczek
UPDATE results SET candidate_id = '6d1db8146a936e15' WHERE candidate_id = 'a1cf26832181776f';  -- DAGMARA "DEE" AVELAR
UPDATE results SET candidate_id = '6d1db8146a936e15' WHERE candidate_id = '1926f7e672359eeb';  -- DAGMARA "DEE" AVELAR
UPDATE results SET candidate_id = '1a9ec10f435dab94' WHERE candidate_id = '97a98a35c6176493';  -- DAN BRADY
UPDATE results SET candidate_id = '234d5a5393950a54' WHERE candidate_id = '8bfd3179bb9a238e';  -- DAN UGASTE
UPDATE results SET candidate_id = '234d5a5393950a54' WHERE candidate_id = '3eb61cf9ce675569';  -- DAN UGASTE
UPDATE results SET candidate_id = '421c1a32b08261db' WHERE candidate_id = 'dfab544d1d9d910d';  -- DAN YOST
UPDATE results SET candidate_id = '44502cf2d44b17cd' WHERE candidate_id = '38c2231bd0f8354f';  -- DANIEL BISS
UPDATE results SET candidate_id = '37b66335ec35d518' WHERE candidate_id = 'c40c6607f35f059d';  -- DANIEL DIDECH
UPDATE results SET candidate_id = '3d085f00c5659dea' WHERE candidate_id = '20380d6348b53497';  -- DANIEL K. ROBIN
UPDATE results SET candidate_id = '546a582a3aee47a7' WHERE candidate_id = '85619bc0bbfd1c49';  -- DANIEL ROLDAN-JOHNSON
UPDATE results SET candidate_id = '89b2d0102f8dbd9f' WHERE candidate_id = '533ce9aa95ce1b49';  -- DANIEL WILLIAM LIPINSKI
UPDATE results SET candidate_id = '46114ee04218080b' WHERE candidate_id = '7249fa56270f4d04';  -- DANNY MALOUF
UPDATE results SET candidate_id = '6f1220c3d2d087cf' WHERE candidate_id = '68a4a9b2ad64dcc6';  -- DARREN BAILEY
UPDATE results SET candidate_id = '2205943073090a5f' WHERE candidate_id = 'e171e79d30d41087';  -- DAVE SYVERSON
UPDATE results SET candidate_id = 'deac4da16d6e0cdb' WHERE candidate_id = 'c80b7675e3a210ce';  -- DAVID F. BLACK
UPDATE results SET candidate_id = '4973b47fda518104' WHERE candidate_id = '51cd5534cfebafbf';  -- DAVID H. MOORE

-- Batch 2
UPDATE results SET candidate_id = 'ce6684d69d19e303' WHERE candidate_id = '68205bf900648cee';  -- DAVID SHESTOKAS
UPDATE results SET candidate_id = '8dc5e92a27e6c71b' WHERE candidate_id = 'c82b0329de229818';  -- DEANNE MARIE MAZZOCHI
UPDATE results SET candidate_id = '0151c3f6f0f2c588' WHERE candidate_id = '87ed6bc7560e3885';  -- DEB CONROY
UPDATE results SET candidate_id = '0151c3f6f0f2c588' WHERE candidate_id = 'db96d5965695b9e5';  -- DEB CONROY
UPDATE results SET candidate_id = 'ecc598c20849941f' WHERE candidate_id = 'cb79b4d4c93e75c7';  -- DEIRDRE McCLOSKEY
UPDATE results SET candidate_id = '3ca8d863a0b822bd' WHERE candidate_id = '361573578d36eacc';  -- DELIA C. RAMIREZ
UPDATE results SET candidate_id = '6df027c7bc2ba51e' WHERE candidate_id = 'c8e7e4f94a2c7998';  -- DELIA RAMIREZ
UPDATE results SET candidate_id = '6df027c7bc2ba51e' WHERE candidate_id = '2e00aef6f527f01e';  -- DELIA RAMIREZ
UPDATE results SET candidate_id = '5094a84146e22403' WHERE candidate_id = 'e6a2e92d6793433e';  -- DENNIS M. REBOLETTI
UPDATE results SET candidate_id = '45091dea2a3ed81f' WHERE candidate_id = '025be568b74aec28';  -- DIANE BLAIR-SHERLOCK
UPDATE results SET candidate_id = '45091dea2a3ed81f' WHERE candidate_id = '0e32e61322c95419';  -- DIANE BLAIR-SHERLOCK
UPDATE results SET candidate_id = 'e3a5ecc831837bc8' WHERE candidate_id = 'bffa8ad6b1b7d03c';  -- DIANE PAPPAS
UPDATE results SET candidate_id = '4dc69e57f901ce93' WHERE candidate_id = 'a5ac6eb047aa8210';  -- DON HARMON
UPDATE results SET candidate_id = '4dc69e57f901ce93' WHERE candidate_id = '3e53d4dd85876254';  -- DON HARMON
UPDATE results SET candidate_id = '4dc69e57f901ce93' WHERE candidate_id = '1d63bb0b1b696aae';  -- DON HARMON
UPDATE results SET candidate_id = '90888f4d6c5690a0' WHERE candidate_id = 'a351c5078fb72568';  -- DONALD J. TRUMP
UPDATE results SET candidate_id = '1b4de281f96cadc5' WHERE candidate_id = '82eb97ff09763c16';  -- DONALD P. DeWITTE
UPDATE results SET candidate_id = '23bc50be49a98105' WHERE candidate_id = 'fe8cc274072737b1';  -- Dale Niewiardowski
UPDATE results SET candidate_id = 'ef4ddbac762505bf' WHERE candidate_id = 'e3f839dec081955b';  -- Dan Shapiro
UPDATE results SET candidate_id = '4ac2ec90fee5db53' WHERE candidate_id = 'db2f89772d82ae5f';  -- Dan Waters
UPDATE results SET candidate_id = '99f92de3118bcef1' WHERE candidate_id = 'fd2cac23e1efa645';  -- Danette Keeler
UPDATE results SET candidate_id = '1c312074aea7d89d' WHERE candidate_id = '9323675682f236a4';  -- Daniel A. Schack
UPDATE results SET candidate_id = 'a08495c0cb2bd3f1' WHERE candidate_id = '96ec1adb13420a85';  -- Daniel A. Tholotowsky
UPDATE results SET candidate_id = 'd0afc00189ec29eb' WHERE candidate_id = '97ef77920f02e9d5';  -- Daniel B. Uyttebroeck
UPDATE results SET candidate_id = '09c7dd2bc56ba578' WHERE candidate_id = '900e93b2b251a4d8';  -- Daniel Behr
UPDATE results SET candidate_id = '7bb1cf5ffabd42f9' WHERE candidate_id = '0506d574e0237e57';  -- Daniel Biss
UPDATE results SET candidate_id = '037fed11ddc99476' WHERE candidate_id = 'c742a966ef267127';  -- Daniel Didech
UPDATE results SET candidate_id = '037fed11ddc99476' WHERE candidate_id = 'db46fb4da5ff9a0b';  -- Daniel Didech
UPDATE results SET candidate_id = 'dfbd07b908442206' WHERE candidate_id = '5271d4f0f8ec8630';  -- Daniel Flores
UPDATE results SET candidate_id = '349d058f8b4938fd' WHERE candidate_id = 'c686f7754c51d7b6';  -- Daniel J. Paluch
UPDATE results SET candidate_id = '50cfc53f3997c571' WHERE candidate_id = '5784b31eba5f261e';  -- Daniel P. Fitzgerald
UPDATE results SET candidate_id = '31f3630d3b074a08' WHERE candidate_id = 'cd10a9c2efd6d20f';  -- Daniel R. McDermott
UPDATE results SET candidate_id = '33ec01565a3ee120' WHERE candidate_id = '1c635e27f8a10980';  -- Daniel T. Behr
UPDATE results SET candidate_id = '52b2421e8037aaee' WHERE candidate_id = '60e805907d0fb419';  -- Danny Theberg
UPDATE results SET candidate_id = '6cd8bc84340f8234' WHERE candidate_id = '571affa11e4059a5';  -- Darby Hills
UPDATE results SET candidate_id = '6cd8bc84340f8234' WHERE candidate_id = 'e0092b98f9daf0f6';  -- Darby Hills
UPDATE results SET candidate_id = 'bd6f5aafd37a6afe' WHERE candidate_id = 'ff248139a6363e14';  -- Dave Conrad
UPDATE results SET candidate_id = '2f5f7bdf302ea2a0' WHERE candidate_id = '84862f7e20529ee2';  -- David B. Guerin
UPDATE results SET candidate_id = '2c8997cec1378f68' WHERE candidate_id = '3a073c4d58d1aade';  -- David Ditchfield
UPDATE results SET candidate_id = '00d920df70da7ef0' WHERE candidate_id = '402c206684e8bd4a';  -- David L. Viverito
UPDATE results SET candidate_id = 'ce3c489e779cc42a' WHERE candidate_id = '69e1e35565969dfb';  -- David Lemme
UPDATE results SET candidate_id = '2cbf218ece47ce25' WHERE candidate_id = 'c26951d2f2c55def';  -- David Molitor
UPDATE results SET candidate_id = '770c5f891544037c' WHERE candidate_id = 'bf1e67a8c123b90f';  -- David Pileski
UPDATE results SET candidate_id = '88807a2ac8879723' WHERE candidate_id = 'cf832d2cee2056fb';  -- David Rana
UPDATE results SET candidate_id = '2569a849399d8961' WHERE candidate_id = '7ba7f5961d7d5fc3';  -- David Riff
UPDATE results SET candidate_id = 'e91b3715b5aff8db' WHERE candidate_id = '52fb79cfa1e1d276';  -- David Wagner
UPDATE results SET candidate_id = '7ec8cf7093226071' WHERE candidate_id = '3e0ac85cc5f2c686';  -- David Weidenfeld
UPDATE results SET candidate_id = '9f0b645ef6386251' WHERE candidate_id = 'c15381e23e3e4965';  -- Dawn M. Nowak
UPDATE results SET candidate_id = '154d28961809734f' WHERE candidate_id = 'f752440d7e903842';  -- DeAndre Tillman
UPDATE results SET candidate_id = '308813dd1c9ff228' WHERE candidate_id = 'b162a98d309e78ba';  -- Dean Barnett
UPDATE results SET candidate_id = 'be0dce628ef0726e' WHERE candidate_id = '4a17f73ba4db7a6d';  -- Deanna Stern
UPDATE results SET candidate_id = '116f29b92528c58f' WHERE candidate_id = 'a0911251f0f50a89';  -- Debbie Budnik
UPDATE results SET candidate_id = 'bf8d16bff1208ca0' WHERE candidate_id = 'f9802b0684707fe6';  -- Deborah H. Ferrero
UPDATE results SET candidate_id = '83f893413c2faaad' WHERE candidate_id = 'c610b54a7e12ecca';  -- Deborah Haynes-Shegog
UPDATE results SET candidate_id = '178fdeafd6820299' WHERE candidate_id = 'acb954bca8092682';  -- Deborah L Tranter
UPDATE results SET candidate_id = '4088c557ff9e62b4' WHERE candidate_id = '5160b58bf3853ad0';  -- Deborah Serota
UPDATE results SET candidate_id = '4088c557ff9e62b4' WHERE candidate_id = '29cae8f3475d8654';  -- Deborah Serota
UPDATE results SET candidate_id = '3782c26eaa81a3a2' WHERE candidate_id = '507995dc973f9763';  -- Debra Williams
UPDATE results SET candidate_id = '788d95b190f1512a' WHERE candidate_id = '5af1810b433631b2';  -- Denice Bocek
UPDATE results SET candidate_id = '3854147b7ded898e' WHERE candidate_id = '094ee42eb0932fe5';  -- Denise Tenyer
UPDATE results SET candidate_id = 'e41c22a111862fe8' WHERE candidate_id = 'bcbbaf7bb0ba465a';  -- Dennis Kelly
UPDATE results SET candidate_id = '5f2066cb4410c707' WHERE candidate_id = 'e2e45edc22cb6797';  -- Dennis M. Kelly
UPDATE results SET candidate_id = '00594ad0bcdabca7' WHERE candidate_id = 'fec06dbd13c9f991';  -- Dennis O''Donovan
UPDATE results SET candidate_id = '8af020f491770664' WHERE candidate_id = 'b642246b253456f4';  -- Dennis P. Mahoney
UPDATE results SET candidate_id = '58276e14f5307c04' WHERE candidate_id = 'b4e4ee014606edc3';  -- Derek Gordon
UPDATE results SET candidate_id = '00e6ff8a3409e0c5' WHERE candidate_id = '0b0784a1ca81981e';  -- Derrick Burks
UPDATE results SET candidate_id = 'a394a64787f08b09' WHERE candidate_id = '514b6954420810ad';  -- Diana Alfaro
UPDATE results SET candidate_id = '0fb67d37758afe73' WHERE candidate_id = '48c8ae0f0f00f0c0';  -- Diana Diakakis
UPDATE results SET candidate_id = '052229b22f0f6a31' WHERE candidate_id = '5a42940570766261';  -- Diana Jackson
UPDATE results SET candidate_id = 'dba7de35e8dc74c3' WHERE candidate_id = '92ba1b0357f769e8';  -- Diana L. Clopton
UPDATE results SET candidate_id = '73c3c882fa259ff4' WHERE candidate_id = '44fa9b0414fd6df1';  -- Diane G. Hill
UPDATE results SET candidate_id = 'f389eeb6cec78e90' WHERE candidate_id = '0652ac402fe6bef9';  -- Diane M. Harris
UPDATE results SET candidate_id = '11a6fd07596c0ad9' WHERE candidate_id = '73c3ee6047553ce3';  -- Dion Lynch
UPDATE results SET candidate_id = '43079e70d23b7f5a' WHERE candidate_id = '2b5b02f7c70ce11e';  -- Dominic Misasi
UPDATE results SET candidate_id = '060212847efa6d29' WHERE candidate_id = '19e5ce2122a40121';  -- Dominique Randle-El
UPDATE results SET candidate_id = '5ef7635d4714b846' WHERE candidate_id = '632dfa8495b10781';  -- Don Cuba
UPDATE results SET candidate_id = '42b888fb6d1a1663' WHERE candidate_id = 'ed11e040953a69e7';  -- Donald Klein
UPDATE results SET candidate_id = 'c4636c69ea6c57c6' WHERE candidate_id = 'f691b55e9b01ab28';  -- Dongbo Mark Su
UPDATE results SET candidate_id = '90e8235c9334d9fe' WHERE candidate_id = 'af463c52fa231f1e';  -- Donna M. Sanders
UPDATE results SET candidate_id = '320bc7cc02571f74' WHERE candidate_id = 'e95d6f9a260b0db4';  -- Donna R. Galeher
UPDATE results SET candidate_id = '8c951b7787adab07' WHERE candidate_id = 'c5c1b4b1bb4caf45';  -- Dorothy C. Smith
UPDATE results SET candidate_id = '3e52596546db3dbe' WHERE candidate_id = 'e80dbac4ba49b2d0';  -- Drew McMahon
UPDATE results SET candidate_id = '4b6eb3ee37c2be76' WHERE candidate_id = '6d24b20cd0b253b2';  -- Drew Sernus
UPDATE results SET candidate_id = '2f50da5a64715d70' WHERE candidate_id = '9fc73eb86a9897f4';  -- Dudley Onderdonk
UPDATE results SET candidate_id = '3aec7bdc7402edc4' WHERE candidate_id = 'd2ed71bcb167a6df';  -- Dustin Good
UPDATE results SET candidate_id = '242ed270002a0726' WHERE candidate_id = 'd96b48df5d044492';  -- E DALE LITNEY
UPDATE results SET candidate_id = '7a83fb396c37885d' WHERE candidate_id = '7356cc46837f7617';  -- EDDIE L. KORNEGAY, JR.
UPDATE results SET candidate_id = '29ebefc9efe99cac' WHERE candidate_id = '8b9199cfaca640cc';  -- EDWARD HERSHEY
UPDATE results SET candidate_id = '20ecde845e1083e9' WHERE candidate_id = 'c2fdbd752a6d7051';  -- EMANUEL "CHRIS" WELCH
UPDATE results SET candidate_id = '20ecde845e1083e9' WHERE candidate_id = 'c457a5714e1df310';  -- EMANUEL "CHRIS" WELCH
UPDATE results SET candidate_id = '835ddb7ea32b0204' WHERE candidate_id = '03124460e1cec7ac';  -- ERICA BRAY-PARKER
UPDATE results SET candidate_id = '85f3f6b72f37a494' WHERE candidate_id = 'b28f3c5edd753f9a';  -- Edward E. Glispie Sr.
UPDATE results SET candidate_id = '40fbaaa1cee1625f' WHERE candidate_id = '9753f55e22f94656';  -- Edward P. Maggio
UPDATE results SET candidate_id = '75befe19a0946b1c' WHERE candidate_id = '7ec6021aa453e1a3';  -- Eileen B. Kowalczyk
UPDATE results SET candidate_id = '071844422198bf3c' WHERE candidate_id = '21fb80032a4f03b9';  -- Eileen Olivier
UPDATE results SET candidate_id = '3c1e3c0253e1df9f' WHERE candidate_id = '7fbb42408373b18f';  -- Eileen Scanlon Harford
UPDATE results SET candidate_id = '9be7034117e920be' WHERE candidate_id = 'afacc2d3967552e9';  -- Elaine Jacoby
UPDATE results SET candidate_id = 'cb3a96abdfce4ae1' WHERE candidate_id = '3778d1fa4032eda1';  -- Elias Lopez
UPDATE results SET candidate_id = '6978d7fd6af1a746' WHERE candidate_id = '1ace4f8cf54e00d9';  -- Elisa Lara
UPDATE results SET candidate_id = '3c93705be7b5f577' WHERE candidate_id = '8c37c8380ffcc9f1';  -- Elizabeth Bauer
UPDATE results SET candidate_id = '3c8a88ccbdcfd770' WHERE candidate_id = '690cfd1e369cceb3';  -- Elizabeth Bolash
UPDATE results SET candidate_id = '8e6e88220f995c47' WHERE candidate_id = '965a6dd16f3eecce';  -- Elizabeth Hunter
UPDATE results SET candidate_id = '7ddbff5ad8cfe4b6' WHERE candidate_id = 'd365e9882160df8b';  -- Elizabeth O. Jimenez
UPDATE results SET candidate_id = 'ec502f6c62c1c64f' WHERE candidate_id = '5500986a7fc5b451';  -- Ellen A. Corley
UPDATE results SET candidate_id = '510ba51c09d8abde' WHERE candidate_id = '8514450661165223';  -- Elyse Hoffenberg
UPDATE results SET candidate_id = '187ed0f753d99867' WHERE candidate_id = '134da44ee72fda73';  -- Emily Fry
UPDATE results SET candidate_id = 'af3ff006e3c3ed90' WHERE candidate_id = 'bd7caabb49933c85';  -- Emily Gilbert
UPDATE results SET candidate_id = '5613f531c0f9ee1a' WHERE candidate_id = '8fc39739b28c2172';  -- Emily K. Wallace
UPDATE results SET candidate_id = '14b4bbe9267b6b74' WHERE candidate_id = 'cd9089b345291f92';  -- Enna Allen
UPDATE results SET candidate_id = '767d22214718e460' WHERE candidate_id = '9bd7fef52d5d129f';  -- Eric N. Smith
UPDATE results SET candidate_id = '023e450a976e8f3a' WHERE candidate_id = '18ec5be4e4bcf618';  -- Eric Smith
UPDATE results SET candidate_id = '3c90f066723f78b7' WHERE candidate_id = '00e20996aae45c91';  -- Eric W. Knox
UPDATE results SET candidate_id = '862279268bef424f' WHERE candidate_id = 'aa1f9d252ca5871f';  -- Erica Padilla
UPDATE results SET candidate_id = '8009281637a980fe' WHERE candidate_id = 'fad83157c5fd7352';  -- Erik LeVere
UPDATE results SET candidate_id = 'c17d5f6736de1955' WHERE candidate_id = 'a14a024ecf4300e9';  -- Erik McCullar
UPDATE results SET candidate_id = '3b10047938e828fe' WHERE candidate_id = '75fe44dea8da3fc1';  -- Erin Chan Ding
UPDATE results SET candidate_id = '3b10047938e828fe' WHERE candidate_id = 'a6f9037de8b4d712';  -- Erin Chan Ding
UPDATE results SET candidate_id = '51b73a2559b997f4' WHERE candidate_id = 'c05777f9fde12c68';  -- Erin Hauck
UPDATE results SET candidate_id = 'f6eede33a55d184d' WHERE candidate_id = '6db3627091d59802';  -- Erin Matta
UPDATE results SET candidate_id = '5affdc8cbd621568' WHERE candidate_id = 'b5c13bbccc4e6a36';  -- Ernestine Proctor-Harris
UPDATE results SET candidate_id = '5131aac38efa8aff' WHERE candidate_id = '92796b4663a3b61f';  -- Errick Stringfellow
UPDATE results SET candidate_id = '03634cf8d54786c7' WHERE candidate_id = '83cb7d5e67430745';  -- Eugene N. Martinez
UPDATE results SET candidate_id = '0982b439eb5b3b5c' WHERE candidate_id = '3660e4ccb331119f';  -- Evelyn Ann Slavic
UPDATE results SET candidate_id = '6ae7ed46ec830ef2' WHERE candidate_id = '7f873f01b8662a9a';  -- Fida Khalil
UPDATE results SET candidate_id = '0a51f19a6a7abb90' WHERE candidate_id = 'be4030cb3d0cd193';  -- Frank Avino, Jr.
UPDATE results SET candidate_id = '1df680a66a333714' WHERE candidate_id = 'b9b50f1f0fec6059';  -- Frank Cesario
UPDATE results SET candidate_id = '3a4fc0f001d7a6ba' WHERE candidate_id = '76652bcda78c3f5b';  -- Frank Di Piero
UPDATE results SET candidate_id = '03a0d3599eaf52a7' WHERE candidate_id = '5ddc6aa5ad54150b';  -- Frank J. Annerino
UPDATE results SET candidate_id = '5d3952097ea37cb8' WHERE candidate_id = 'b2020114069e47ad';  -- Frank Rowder
UPDATE results SET candidate_id = 'ee093066cacb2faa' WHERE candidate_id = '40dba4c75b9765c0';  -- GARY GRASSO
UPDATE results SET candidate_id = '1746023182601353' WHERE candidate_id = '26f9a8600a2a3261';  -- GARY RABINE
UPDATE results SET candidate_id = 'ae74cbde98e19f1f' WHERE candidate_id = 'c9ed509e81732b69';  -- GEORGE WEBER
UPDATE results SET candidate_id = 'b669cbb5788b1e68' WHERE candidate_id = 'a6e3ea4f6c8332d8';  -- GILBERT "GIL" VILLEGAS
UPDATE results SET candidate_id = '700c522eae2d61d0' WHERE candidate_id = '05f4446632afbc47';  -- GLORIA LA RIVA
UPDATE results SET candidate_id = '700c522eae2d61d0' WHERE candidate_id = '806a4cb402545909';  -- GLORIA LA RIVA
UPDATE results SET candidate_id = '1bbd0d7a7c97e8f1' WHERE candidate_id = '68d630955be5a5e0';  -- Gail Schnitzer Eisenberg
UPDATE results SET candidate_id = '1c8464de49b11b89' WHERE candidate_id = 'eb4c396c0cc3fd03';  -- Gary D. Lewis
UPDATE results SET candidate_id = '6208e9100343c443' WHERE candidate_id = 'c09f2d54c9b15694';  -- Gary Grasso
UPDATE results SET candidate_id = '9d6f1066758e9f44' WHERE candidate_id = 'ff6cbb240ac58f8b';  -- Gene Adams
UPDATE results SET candidate_id = '29c47c60ba7bd5bc' WHERE candidate_id = 'ec3d73d1da2347f9';  -- Gene Haring
UPDATE results SET candidate_id = '068bc8b306337e6f' WHERE candidate_id = 'fe894ed89d359cc6';  -- George D. Alpogianis
UPDATE results SET candidate_id = 'df44e57677f84acb' WHERE candidate_id = 'e3af22e47f77c60c';  -- George Krafcisin
UPDATE results SET candidate_id = '186514858de8d9ee' WHERE candidate_id = 'b0388f02bbeb2d38';  -- Gia Marie Benline
UPDATE results SET candidate_id = 'eeac21528440b13b' WHERE candidate_id = 'e68daa4c24bd010c';  -- Gigi Iacovelli
UPDATE results SET candidate_id = '075626025a1f43f5' WHERE candidate_id = 'a61f904ed74beb95';  -- Gil Antokal
UPDATE results SET candidate_id = '1356653825e02fed' WHERE candidate_id = 'c7900dfd41b48e19';  -- Gil Gibori
UPDATE results SET candidate_id = 'a418c15174f71afa' WHERE candidate_id = 'e31bdb7d6bc859fd';  -- Gina M Pesko
UPDATE results SET candidate_id = '85ef01894e1bb810' WHERE candidate_id = 'e87cc81709fc9d00';  -- Gloria Murawska
UPDATE results SET candidate_id = 'a4e99a16e033ac3b' WHERE candidate_id = '6044d693840df3f6';  -- Gowri Magati
UPDATE results SET candidate_id = 'b5ab8db13524301b' WHERE candidate_id = 'a74d695795def0ab';  -- Grace Khan
UPDATE results SET candidate_id = '0d3b73c667ad5d72' WHERE candidate_id = '8ee8ecacf736741f';  -- Grace Shin
UPDATE results SET candidate_id = '6d8ae4150ea428c5' WHERE candidate_id = 'd6ba355e5f40022c';  -- Greg Christoff
UPDATE results SET candidate_id = 'ca9e31d5db499063' WHERE candidate_id = '90b5bf2e48604764';  -- Gregory Lapin
UPDATE results SET candidate_id = '40f6e2a66bbe1cac' WHERE candidate_id = '8ab810e593b9ec1d';  -- Gregory Lewis
UPDATE results SET candidate_id = '167d74ac1c9918a9' WHERE candidate_id = '18c2536a03e3aafb';  -- Gregory Rusteberg
UPDATE results SET candidate_id = '167d74ac1c9918a9' WHERE candidate_id = '47c6d8df739a9b04';  -- Gregory Rusteberg
UPDATE results SET candidate_id = '853be26157f6f5cb' WHERE candidate_id = '5c136a8fa22cc463';  -- Gregory S. Pike
UPDATE results SET candidate_id = 'd08bae65fced530f' WHERE candidate_id = '29cf6b98372b5e94';  -- HARRY BENTON
UPDATE results SET candidate_id = '55f5c7150d76d5fd' WHERE candidate_id = 'accdf3712919383e';  -- HEATHER BROWN
UPDATE results SET candidate_id = 'd8999a8e72c3363e' WHERE candidate_id = 'c2b1ea729b6848af';  -- HOLLY KIM
UPDATE results SET candidate_id = 'c0ded5a95f6c9a60' WHERE candidate_id = '6004ce12c702843a';  -- HOWIE HAWKINS
UPDATE results SET candidate_id = 'e028ebb4f44dfd00' WHERE candidate_id = '010f4db06f127669';  -- Harathi K. Srivastava
UPDATE results SET candidate_id = '041ff7664877a6d8' WHERE candidate_id = '2685835abd49ad63';  -- Harry J. Pappas
UPDATE results SET candidate_id = '2d6f34401772c116' WHERE candidate_id = '95879eb2111b7e07';  -- Heidi Hedstrom
UPDATE results SET candidate_id = '733488a9b15f88d4' WHERE candidate_id = '8ed93aab79a334fd';  -- Helen Edwards
UPDATE results SET candidate_id = '405840be55e9d601' WHERE candidate_id = '9ec9bcd610ad9d0a';  -- Helen Tomczuk
UPDATE results SET candidate_id = '1bb8982bfc1738e1' WHERE candidate_id = '3ad10dd7890bb307';  -- Henry Hackney, Jr.
UPDATE results SET candidate_id = '034a11123bf42118' WHERE candidate_id = '1989ceb490e9f5e4';  -- Herb Johnson
UPDATE results SET candidate_id = 'd26abfe78cba8952' WHERE candidate_id = 'e4e37da75bbe0a70';  -- Hetal Wallace
UPDATE results SET candidate_id = '7fc530f2cfe904d5' WHERE candidate_id = '67e7b185f907041d';  -- Hoan Huynh
UPDATE results SET candidate_id = '2aa38439ebf01380' WHERE candidate_id = '1b800b5a34f0d814';  -- Holly Kim
UPDATE results SET candidate_id = '196575c2a9462fbb' WHERE candidate_id = 'b6c6f941419ee6c4';  -- Howard Rosenblum
UPDATE results SET candidate_id = '8f5a7dc8e572e391' WHERE candidate_id = '2fe45386e362d364';  -- IRIS Y. MARTINEZ
UPDATE results SET candidate_id = 'bcbb7ad890c2accc' WHERE candidate_id = '785b604c75c2ba40';  -- IYMEN H CHEHADE
UPDATE results SET candidate_id = '05b6bc9a9155238b' WHERE candidate_id = '3affea2f2d1dfda7';  -- Irma Quintero
UPDATE results SET candidate_id = '1a71fe4b8deb4766' WHERE candidate_id = '20738d04f2d539ad';  -- Isaac Brubaker
UPDATE results SET candidate_id = '705673d57df9a21c' WHERE candidate_id = '82320cf7ae7c67e4';  -- Isiah Brandon
UPDATE results SET candidate_id = 'f260d31856abb310' WHERE candidate_id = 'faf4553483584a8c';  -- Ivory Myles
UPDATE results SET candidate_id = 'af0ab7647702d549' WHERE candidate_id = '0cceb4767ecebfc9';  -- JACKIE WILLIAMSON
UPDATE results SET candidate_id = '6e13f34842461d67' WHERE candidate_id = 'b27569553908f1b5';  -- JAMES FALAKOS
UPDATE results SET candidate_id = '2d3216a696bfd3f1' WHERE candidate_id = '22d6248f4de07204';  -- JAMES T. "JIM" MARTER
UPDATE results SET candidate_id = '7f677c7e44791522' WHERE candidate_id = '97d973df25b74135';  -- JANET YANG ROHR
UPDATE results SET candidate_id = '7f677c7e44791522' WHERE candidate_id = '4d70506793a13422';  -- JANET YANG ROHR
UPDATE results SET candidate_id = '080af3a66b37e1c1' WHERE candidate_id = '85e20bcd0552f72d';  -- JB PRITZKER
UPDATE results SET candidate_id = '080af3a66b37e1c1' WHERE candidate_id = '2086585bfab85dba';  -- JB PRITZKER
UPDATE results SET candidate_id = 'aac48aaa780f698d' WHERE candidate_id = '2258fc5748f9028b';  -- JEANNE IVES
UPDATE results SET candidate_id = '6ce403a3400ee510' WHERE candidate_id = 'd2f02ee4dda79207';  -- JED DAVIS
UPDATE results SET candidate_id = 'c55d908d1d9da37f' WHERE candidate_id = '40e1775445b52650';  -- JEFF KEICHER
UPDATE results SET candidate_id = 'c10fa6a0a8f7a5e0' WHERE candidate_id = '716b1c9181c4ce0f';  -- JEFFREY M. JACOBSON
UPDATE results SET candidate_id = 'd7183ea066d11a1c' WHERE candidate_id = '0d93c8f845b93733';  -- JENN LADISCH DOUGLASS
UPDATE results SET candidate_id = '65090846f15b701a' WHERE candidate_id = 'f78b158f802c0eb2';  -- JENNIFER SANALITRO
UPDATE results SET candidate_id = '65090846f15b701a' WHERE candidate_id = 'c6e41f05eed9cb47';  -- JENNIFER SANALITRO
UPDATE results SET candidate_id = '02ed26fe660f2cbf' WHERE candidate_id = '9ceee80bcb9e8498';  -- JENNIFER ZORDANI
UPDATE results SET candidate_id = 'd7f2f23ce428f730' WHERE candidate_id = '1ae1d015b38a2e1b';  -- JERRY EVANS
UPDATE results SET candidate_id = '518e84188431b11a' WHERE candidate_id = 'bbea4692ac7bf92a';  -- JESSE RUIZ
UPDATE results SET candidate_id = 'c42cbec1356ebfdf' WHERE candidate_id = '2051726decd52de5';  -- JESSE SULLIVAN
UPDATE results SET candidate_id = 'd50ae3b99dd4d534' WHERE candidate_id = '1ca6ea7e0bbab706';  -- JESSE WHITE
UPDATE results SET candidate_id = '7e85321a5eb79d73' WHERE candidate_id = '4e5bef5e6626beec';  -- JESUS "CHUY" GARCIA
UPDATE results SET candidate_id = 'a60a029dcac152df' WHERE candidate_id = '1e9f08106ba208d6';  -- JILL OTTE
UPDATE results SET candidate_id = 'f0713a0108780e92' WHERE candidate_id = '446feb98014a3879';  -- JIM DURKIN

-- Batch 3
UPDATE results SET candidate_id = '139f7e7c17873e0d' WHERE candidate_id = '2ad7b537c3357bb8';  -- JIM OBERWEIS
UPDATE results SET candidate_id = '4be9a7b2970916dc' WHERE candidate_id = '22b6909ee0109111';  -- JIM WALSH
UPDATE results SET candidate_id = 'a279616c31d1da12' WHERE candidate_id = '1f608c55cbdf0a8a';  -- JIM WALZ
UPDATE results SET candidate_id = '0c970ba181649ef3' WHERE candidate_id = '72abe2ad7ba1a770';  -- JIMMY LEE TILLMAN II
UPDATE results SET candidate_id = '8ea611f830633bc2' WHERE candidate_id = 'e9abd0133d0c1597';  -- JO JORGENSEN
UPDATE results SET candidate_id = 'f9fe22e227f7c9b6' WHERE candidate_id = 'c096eaa83bb104ad';  -- JOE BIRKETT - NO
UPDATE results SET candidate_id = '1cfbab542274fd5b' WHERE candidate_id = 'f7e8ed05140279b3';  -- JOE BIRKETT - YES
UPDATE results SET candidate_id = '5b1c8cee3de4c0d1' WHERE candidate_id = 'adfd70fad361106a';  -- JOHN C. MILHISER
UPDATE results SET candidate_id = '2c90f60cb6d1c030' WHERE candidate_id = 'a0afe5728a66e765';  -- JOHN CONNOR
UPDATE results SET candidate_id = '381a5dd311a4bca2' WHERE candidate_id = '1ea5c764f3b29ab4';  -- JOHN CURRAN
UPDATE results SET candidate_id = '381a5dd311a4bca2' WHERE candidate_id = '1b0735433ee40b7e';  -- JOHN CURRAN
UPDATE results SET candidate_id = 'c230254e08314f22' WHERE candidate_id = 'c2cde85359c9575c';  -- JOHN J. CULLERTON
UPDATE results SET candidate_id = 'a35933ca1a6fa11e' WHERE candidate_id = 'd6d0f1905e0f9c47';  -- JOHN J. HOSTA
UPDATE results SET candidate_id = '81e12a6981f7bfb3' WHERE candidate_id = 'ee6401918460a03c';  -- JON STEWART
UPDATE results SET candidate_id = 'd901d2f7e4ddaf2b' WHERE candidate_id = '68daf046a030c8f2';  -- JONATHAN CARROLL
UPDATE results SET candidate_id = '888551e5b4ae331c' WHERE candidate_id = 'd9a27fac7cb4aa7a';  -- JOSEPH R. BIDEN
UPDATE results SET candidate_id = 'd23c84a5d1791c62' WHERE candidate_id = '439c974d981a04bc';  -- JOYCE MASON
UPDATE results SET candidate_id = '27fb799ae9a41496' WHERE candidate_id = '222aa02dc9274ea7';  -- JUAN ENRIQUE AGUIRRE
UPDATE results SET candidate_id = '07a4d86a0d5208f8' WHERE candidate_id = 'ddc491fac0ff52ac';  -- JUNAID AHMED
UPDATE results SET candidate_id = 'c2683bdcf0e61860' WHERE candidate_id = '0c8673ea4a2a5aff';  -- JUSTIN BURAU
UPDATE results SET candidate_id = '9d207f9e8d9a30ed' WHERE candidate_id = 'd50aa568b35c5d5a';  -- Jack Bower
UPDATE results SET candidate_id = 'ae278fe0e71ea590' WHERE candidate_id = 'c42b131307c9d0f8';  -- Jack Hille
UPDATE results SET candidate_id = '454cbe29961e6fc4' WHERE candidate_id = '7b470bcd420175dc';  -- Jackie McGrath
UPDATE results SET candidate_id = '149b768e6a5b6df8' WHERE candidate_id = '1b1c9867a929dcb0';  -- Jaclyn Jaime
UPDATE results SET candidate_id = 'a6a17be36fe58b97' WHERE candidate_id = 'edacdbd7da70d3e9';  -- Jacqueline Bujdei
UPDATE results SET candidate_id = 'ba081ef463b1276c' WHERE candidate_id = 'f6b62c747e33b165';  -- Jacqueline Jordan
UPDATE results SET candidate_id = 'a58bc163c6224dbc' WHERE candidate_id = 'e0a618346b4358f0';  -- Jacqueline Pereda
UPDATE results SET candidate_id = '2f2dfc3f0c669e56' WHERE candidate_id = 'c3599a6ce8000cfe';  -- Jaime S. Contreras
UPDATE results SET candidate_id = 'ecdabc80b91eb59d' WHERE candidate_id = 'f311fc92a30888f0';  -- James A. Hortsman
UPDATE results SET candidate_id = 'bf70a455719f3b88' WHERE candidate_id = '20d262d82f968615';  -- James C. Mitchell, Jr.
UPDATE results SET candidate_id = 'b7ba9fa5d66937a7' WHERE candidate_id = 'ec879f373214bbd4';  -- James Daemicke
UPDATE results SET candidate_id = '1dafe84875433d9d' WHERE candidate_id = '7bd5a00d33edc514';  -- James Di Paola
UPDATE results SET candidate_id = '04ba3e81d8c4ef67' WHERE candidate_id = '9f91714665b45edf';  -- James J. Bertucci
UPDATE results SET candidate_id = '4fe676000730c4c9' WHERE candidate_id = '9e17adc8dcb08591';  -- James J. Tinaglia
UPDATE results SET candidate_id = '4e949442640d3758' WHERE candidate_id = '659769838d407194';  -- James Johnson
UPDATE results SET candidate_id = '12206e6ba3ea481a' WHERE candidate_id = '2dde94349c942b46';  -- James Maher
UPDATE results SET candidate_id = '63fd62b82eed6f46' WHERE candidate_id = 'f3d23c46fcd47e8f';  -- James Meyer
UPDATE results SET candidate_id = '7a8ef3a4375c031c' WHERE candidate_id = 'ce4289e4e7966768';  -- James Oakley
UPDATE results SET candidate_id = '7ab96cfed2c6bf52' WHERE candidate_id = 'db150467625ed563';  -- James P. Nagle
UPDATE results SET candidate_id = '2d7a2287cdf1f402' WHERE candidate_id = 'e70cc34ae436e126';  -- James R. Emmett
UPDATE results SET candidate_id = '1178bd49c4601d46' WHERE candidate_id = '8b2aa7b74f1d2402';  -- James Ruffatto
UPDATE results SET candidate_id = '3d6444c2858744df' WHERE candidate_id = '56f46de6aa0dcde4';  -- James Taglia
UPDATE results SET candidate_id = 'b2c2a17d27dcd12f' WHERE candidate_id = 'f1a3f353d800e486';  -- James Wade
UPDATE results SET candidate_id = 'c4add355855c2d2b' WHERE candidate_id = 'f1d7bcf1ae3e3a3e';  -- Jamie Zaura
UPDATE results SET candidate_id = '451847f60a24b8de' WHERE candidate_id = '2bc8196882a9197c';  -- Jan Caron
UPDATE results SET candidate_id = 'aef02d48522ba638' WHERE candidate_id = '40706b11e59dc5af';  -- Jane A Russell
UPDATE results SET candidate_id = '4e67f9dd23bcf404' WHERE candidate_id = '11de3b3aab8a407c';  -- Janel A. King
UPDATE results SET candidate_id = '5443f0752aa3e79a' WHERE candidate_id = 'f0449d389b2acabd';  -- Janelle D. McFadden
UPDATE results SET candidate_id = '1885f768727d7e51' WHERE candidate_id = '40db257b0d35f8f0';  -- Janet Jordan
UPDATE results SET candidate_id = 'b0f9dd2fb61bbc6f' WHERE candidate_id = '32122b9b382a70b5';  -- Janet M. Sirabian
UPDATE results SET candidate_id = '1f3a74aac7a500ed' WHERE candidate_id = '4422d4d3a6b5d3e3';  -- Janine Witko
UPDATE results SET candidate_id = '95b8eb9dae712a4c' WHERE candidate_id = '4b50016ba4c122bf';  -- Jason Lohmeyer
UPDATE results SET candidate_id = '97f9354d29cef67d' WHERE candidate_id = 'efb2963858700ad9';  -- Jason Mathews
UPDATE results SET candidate_id = '0b239d650f2177b8' WHERE candidate_id = '3c1066dd68c06bb6';  -- Jason Pyle
UPDATE results SET candidate_id = '2e7c8a5dcd4bb40d' WHERE candidate_id = 'fb471c53a4fb83b0';  -- Jeff Cohen
UPDATE results SET candidate_id = '698150882b5c2a78' WHERE candidate_id = 'f11e612ab48ef39d';  -- Jeff Waters
UPDATE results SET candidate_id = '3ca732bb9436dbfd' WHERE candidate_id = '5f3ee8193157f891';  -- Jefferey Hodges
UPDATE results SET candidate_id = '851673452c8a181e' WHERE candidate_id = '5e540e38461088d4';  -- Jeffery Burns
UPDATE results SET candidate_id = '3f436afc0fa9ba61' WHERE candidate_id = 'dbf9856cfcce0b81';  -- Jeffrey C. Franke
UPDATE results SET candidate_id = '4285c662f3225ca1' WHERE candidate_id = '700da8bb10cd3ab5';  -- Jeffrey Johnson
UPDATE results SET candidate_id = '18b265349e4d5555' WHERE candidate_id = 'c86526292f6253c2';  -- Jeffrey L Sargent
UPDATE results SET candidate_id = '9be0f4a2f72a6cd0' WHERE candidate_id = '73ddf2018c4a8ea3';  -- Jeffrey M. Key
UPDATE results SET candidate_id = '29b51afae15e55d2' WHERE candidate_id = '5208b4ee4de196f2';  -- Jeffrey T. Sherwin
UPDATE results SET candidate_id = 'bd79f59ab7cd225f' WHERE candidate_id = 'e6d4d6c9cc15c410';  -- Jeffrey Zuercher
UPDATE results SET candidate_id = '95e70c67f5ede2e3' WHERE candidate_id = 'e554d9e829a3f9af';  -- Jennifer A. Braun-Denton
UPDATE results SET candidate_id = '0dc703dc0e11c325' WHERE candidate_id = '642c92b016c24925';  -- Jennifer Banek
UPDATE results SET candidate_id = '0dc703dc0e11c325' WHERE candidate_id = '0514c44934f517b3';  -- Jennifer Banek
UPDATE results SET candidate_id = '8fe6a7169c2e67e1' WHERE candidate_id = '2cbf914734de1694';  -- Jennifer Clark
UPDATE results SET candidate_id = '73b51a5d7e4af02a' WHERE candidate_id = '6458bb506e6eaf67';  -- Jennifer E Ziegler
UPDATE results SET candidate_id = '07531256f0f7f76b' WHERE candidate_id = 'b5308b2a3f28d9f2';  -- Jennifer J. Lucas
UPDATE results SET candidate_id = '7a2752b586b561f9' WHERE candidate_id = '123c2fe1363d01b7';  -- Jennifer La Mell Goldstone
UPDATE results SET candidate_id = 'd3a78c451ff1785c' WHERE candidate_id = 'e73008b4b7457d43';  -- Jennifer Marie Jensen
UPDATE results SET candidate_id = '900ea8915d4af439' WHERE candidate_id = 'db5fec01ca59baa8';  -- Jennifer Mitchell
UPDATE results SET candidate_id = '44dfb89bd037b6e3' WHERE candidate_id = '9e64953162b51203';  -- Jennifer Strauss Hendricks
UPDATE results SET candidate_id = '153058df67b5154a' WHERE candidate_id = '58d76d0ee4d5f79e';  -- Jennifer Wondrasek
UPDATE results SET candidate_id = '153058df67b5154a' WHERE candidate_id = '76faf9202bfbca87';  -- Jennifer Wondrasek
UPDATE results SET candidate_id = '3ca9e8c242914855' WHERE candidate_id = 'ac0215092339c2a3';  -- Jenny Levin
UPDATE results SET candidate_id = '2db77fd07e3a86e5' WHERE candidate_id = 'f79d355196eac269';  -- Jermaine Stewart
UPDATE results SET candidate_id = '060ef43dc5fdf2b1' WHERE candidate_id = '15b5479acab2d0da';  -- Jesal Patel
UPDATE results SET candidate_id = '194eb3971f0ffd92' WHERE candidate_id = 'cc2e84e2d4f14d98';  -- Jesse Greenberg
UPDATE results SET candidate_id = '913e65b600b7d9f4' WHERE candidate_id = '95087c42916f9d91';  -- Jesse Miranda
UPDATE results SET candidate_id = '42143425ba9c354f' WHERE candidate_id = '33918c5a693b1e81';  -- Jesse Rojo
UPDATE results SET candidate_id = '6f92fa5ba04eaeb8' WHERE candidate_id = '9eb6f795921451ad';  -- Jessica Gray
UPDATE results SET candidate_id = '10c162719f6f32c2' WHERE candidate_id = '3ee6ae04f2f257f3';  -- Jessica Hoffmann
UPDATE results SET candidate_id = '292b2e45cd4c5afa' WHERE candidate_id = 'a07faa5d84a09c63';  -- Jessica Underwood
UPDATE results SET candidate_id = '89bdc1ff36e002d8' WHERE candidate_id = '99de0a226c1b1c6d';  -- Jewell Thompson
UPDATE results SET candidate_id = 'c3c5cec98b1809ef' WHERE candidate_id = 'f17e3104d87aa4dd';  -- Jill Zubak
UPDATE results SET candidate_id = 'e201d33e01f49a94' WHERE candidate_id = 'cc3ff252968bcd38';  -- Jim Dillon
UPDATE results SET candidate_id = 'd730829b9e69d805' WHERE candidate_id = 'fd18911c5f39083b';  -- Jim Geldermann
UPDATE results SET candidate_id = '54047dd0c955809b' WHERE candidate_id = 'f4a6a8276e845232';  -- Jim Schwantz
UPDATE results SET candidate_id = 'a315aac57c62993e' WHERE candidate_id = '87b806bc35016538';  -- Jimi Psarakis
UPDATE results SET candidate_id = '006d0278c215b169' WHERE candidate_id = '408366fbe4f83f40';  -- Joan Bende
UPDATE results SET candidate_id = '4c4705662634537e' WHERE candidate_id = 'fbd5425acc4d726c';  -- Joanna M. Liotine Leafblad
UPDATE results SET candidate_id = '650c4adea50bee9e' WHERE candidate_id = 'ac95f89aa20e04b4';  -- Joanne R. Johnson
UPDATE results SET candidate_id = '650c4adea50bee9e' WHERE candidate_id = '302a5e93e681769b';  -- Joanne R. Johnson
UPDATE results SET candidate_id = '572eac1fd9666d99' WHERE candidate_id = '84c4b7e966d5c9da';  -- Joe LoVerde
UPDATE results SET candidate_id = '048e990eaa3916a0' WHERE candidate_id = '0d4f5f38a18d799a';  -- Joe Young
UPDATE results SET candidate_id = '0b22abfd3930707b' WHERE candidate_id = '90cc7c65bf39b7d1';  -- Joel Seeskin
UPDATE results SET candidate_id = 'e9a231a69c0c70e7' WHERE candidate_id = '4bb0b581fa29e888';  -- John "Jack" Lind
UPDATE results SET candidate_id = '8c89ac9e7bca5045' WHERE candidate_id = 'a00cc8409399c9e8';  -- John C. Johnson
UPDATE results SET candidate_id = '8913313331bac6b9' WHERE candidate_id = 'c119afc4d41354f4';  -- John Carpenter Clarke
UPDATE results SET candidate_id = 'bffbb30b76740215' WHERE candidate_id = '68fb69bf5d3562df';  -- John Cullerton
UPDATE results SET candidate_id = 'efac60716b3dd611' WHERE candidate_id = '4a30c10fdceb175a';  -- John D. Idleburg
UPDATE results SET candidate_id = '222e756d66707bff' WHERE candidate_id = 'd28cd393fab54c56';  -- John Egofske
UPDATE results SET candidate_id = '914c1654250e8b54' WHERE candidate_id = 'a842344266ac9ab3';  -- John Elleson
UPDATE results SET candidate_id = '757107d3bac4b21b' WHERE candidate_id = '2cf7300a26257d94';  -- John Gawel
UPDATE results SET candidate_id = '1dabc95d33c64dc4' WHERE candidate_id = 'd51d0c32500f6110';  -- John Harris
UPDATE results SET candidate_id = '792530f81c87afa9' WHERE candidate_id = 'a407fabc752935a5';  -- John M. Ross
UPDATE results SET candidate_id = 'ced2abb0b5fcc784' WHERE candidate_id = 'dce31a17ae59d2a1';  -- John P Hajduch
UPDATE results SET candidate_id = '59a5325ed0e8a570' WHERE candidate_id = 'd9f674601d60198f';  -- John P. Flaherty
UPDATE results SET candidate_id = '8e1b35867e0fcba7' WHERE candidate_id = '40993ae3b1aa9119';  -- John P. Forney
UPDATE results SET candidate_id = '781463f6994beebc' WHERE candidate_id = 'b72ce06c0e5e7e90';  -- John Pacella
UPDATE results SET candidate_id = '96b7461448316c0c' WHERE candidate_id = '4ed6d5890399cb91';  -- John T Supplitt
UPDATE results SET candidate_id = '775d4a3eac143232' WHERE candidate_id = 'a9fad5f834c42e7e';  -- John Wasik
UPDATE results SET candidate_id = '50787b5a70acc3e2' WHERE candidate_id = '0fdcabc8216e2b99';  -- Jonathan Matta
UPDATE results SET candidate_id = '7d2e13c0a28da952' WHERE candidate_id = 'b156115ea18ee704';  -- Jonathan Nieuwsma
UPDATE results SET candidate_id = 'e16dc46209930d9e' WHERE candidate_id = 'cb0c0c2daafd5482';  -- Jose A. Guzman
UPDATE results SET candidate_id = '2f864cb522c7377a' WHERE candidate_id = '26e7094892efe6f4';  -- Jose S. Martinez
UPDATE results SET candidate_id = 'c106686c54977e90' WHERE candidate_id = '912d1625703017b1';  -- Joseph A. Bosnick
UPDATE results SET candidate_id = 'e935c2d5f4130081' WHERE candidate_id = '62becb6688a20ca6';  -- Joseph Cohen
UPDATE results SET candidate_id = '754af240d98e38a8' WHERE candidate_id = '901dfbdffb50c683';  -- Joseph Mengoni
UPDATE results SET candidate_id = '298b7da40dc3c366' WHERE candidate_id = 'f6e4e650bd051e4e';  -- Joseph T. Balogh
UPDATE results SET candidate_id = '2ba2598736f1eb84' WHERE candidate_id = '9c9336fa84471de5';  -- Joseph W. LaPorte
UPDATE results SET candidate_id = '37e2131d62aba99a' WHERE candidate_id = 'fe4c3f1ec3aca805';  -- Joshua Charlson
UPDATE results SET candidate_id = '964e6ed435789019' WHERE candidate_id = 'ebe4ab378b1d8a50';  -- Joshua Travis
UPDATE results SET candidate_id = 'd4b60f65c85c5d92' WHERE candidate_id = 'fc5a0fec0cfd9880';  -- Josie Croll
UPDATE results SET candidate_id = '0469d11bb0770c5c' WHERE candidate_id = 'f7408bfac5c6e77a';  -- Josina Morita
UPDATE results SET candidate_id = '1f14de961c003804' WHERE candidate_id = '6cf4e4d1844d482a';  -- Joy Ebhomielen
UPDATE results SET candidate_id = 'bc10b40522f1d54f' WHERE candidate_id = 'ddda8bce11c69503';  -- Joy Johnson
UPDATE results SET candidate_id = 'bc10b40522f1d54f' WHERE candidate_id = '100a77829759d6d7';  -- Joy Johnson
UPDATE results SET candidate_id = '7320a96e91858181' WHERE candidate_id = '87d31d869bd3a04b';  -- Joy Symonds
UPDATE results SET candidate_id = 'ee150ff6c23b697c' WHERE candidate_id = '56fe57963df75cc0';  -- Joyce Dickerson
UPDATE results SET candidate_id = '2b4bcba4a30c671c' WHERE candidate_id = 'c262422363431997';  -- Joyce Mason
UPDATE results SET candidate_id = 'dd4d2113f20f2e20' WHERE candidate_id = '3c69941d7ef9ec6d';  -- Juan Geracaris
UPDATE results SET candidate_id = 'c43c243d892cc941' WHERE candidate_id = '13273d19ef6bc5f0';  -- Juan Urbina
UPDATE results SET candidate_id = '5d5cf6e93831d7dd' WHERE candidate_id = 'a11203ab673809a2';  -- Juanita M. Hardin
UPDATE results SET candidate_id = '070b7c6ca209c22a' WHERE candidate_id = '0bd5135d2e5186dc';  -- Julia Atkin
UPDATE results SET candidate_id = '443c78d7cc9698ff' WHERE candidate_id = 'ab9677fec667fe93';  -- Julie A. Morrison
UPDATE results SET candidate_id = '8c66d08706265957' WHERE candidate_id = 'ff27d65cd1048348';  -- Julie Cho
UPDATE results SET candidate_id = '51bc81bade165320' WHERE candidate_id = 'd8db2c714286765b';  -- Julie Genualdi
UPDATE results SET candidate_id = 'c81e97028e159f65' WHERE candidate_id = '79916c85803fef2c';  -- Justin Ford
UPDATE results SET candidate_id = '3464cf0ae55d8529' WHERE candidate_id = 'ffac9b9f8802dfca';  -- Justin Sheperd
UPDATE results SET candidate_id = '8e222c1427b8cd25' WHERE candidate_id = '13dc8b4a694ca4c6';  -- KAREN KOLODZIEJ
UPDATE results SET candidate_id = '2ea9ec7f0cab3225' WHERE candidate_id = '922ae7515dbcb1c5';  -- KARINA VILLA
UPDATE results SET candidate_id = '2ea9ec7f0cab3225' WHERE candidate_id = '6a19aed58ff7ce4c';  -- KARINA VILLA
UPDATE results SET candidate_id = '2ea9ec7f0cab3225' WHERE candidate_id = '9e9f14a4bc0909fe';  -- KARINA VILLA
UPDATE results SET candidate_id = '920472211f74a2fa' WHERE candidate_id = '54b22479ac927f5c';  -- KATHLEEN WILLIS
UPDATE results SET candidate_id = '920472211f74a2fa' WHERE candidate_id = 'e2739beb529d7e06';  -- KATHLEEN WILLIS
UPDATE results SET candidate_id = 'de4b91b1b1674e94' WHERE candidate_id = 'e059dc3b781d6137';  -- KATHY SALVI
UPDATE results SET candidate_id = 'f563ee0b992fe1e0' WHERE candidate_id = '9a4a38d95c2b39d7';  -- KEITH PEKAU
UPDATE results SET candidate_id = 'f282df06e1084eb3' WHERE candidate_id = '9afd312ad9c85bef';  -- KELLY M. BURKE
UPDATE results SET candidate_id = '52021b34f845b728' WHERE candidate_id = 'f428a246fe0e0da8';  -- KIMBERLY A. LIGHTFORD
UPDATE results SET candidate_id = 'bd2ff0d76aa3dd0f' WHERE candidate_id = '4fd9c5cd08f58036';  -- KRISTINA ZAHORIK
UPDATE results SET candidate_id = 'bd2ff0d76aa3dd0f' WHERE candidate_id = '5a966be22df3a264';  -- KRISTINA ZAHORIK
UPDATE results SET candidate_id = '49e9aec06a57517a' WHERE candidate_id = '4599d11c06143116';  -- KWAME RAOUL
UPDATE results SET candidate_id = '49e9aec06a57517a' WHERE candidate_id = '7fe8a58e3f4231c8';  -- KWAME RAOUL
UPDATE results SET candidate_id = '49e9aec06a57517a' WHERE candidate_id = 'd1f5b28849e5acb3';  -- KWAME RAOUL
UPDATE results SET candidate_id = '7c9ba259cb621884' WHERE candidate_id = 'fb5115e9c8c52a9d';  -- Kandice Cooley Jones
UPDATE results SET candidate_id = '530de71de666c1b1' WHERE candidate_id = '552a81f5986b0fb1';  -- Kanu Panchal
UPDATE results SET candidate_id = '6778a52cf0b0ce55' WHERE candidate_id = '9183dd052d9b3fa8';  -- Karen D. Special
UPDATE results SET candidate_id = '11f3478806cfd32f' WHERE candidate_id = 'b93cd238c6c7c1fb';  -- Karen Darch
UPDATE results SET candidate_id = '6915d91f2981e6a1' WHERE candidate_id = 'ac3b5c43ced50953';  -- Karen J. Arnet
UPDATE results SET candidate_id = '2718e1d41a429c27' WHERE candidate_id = '5898ea370e257b68';  -- Karen King
UPDATE results SET candidate_id = '74f6255f9059c7f1' WHERE candidate_id = '7b100f68e6cb7488';  -- Karen Taubman
UPDATE results SET candidate_id = '558227562ba26510' WHERE candidate_id = '6212db5bd69ca635';  -- Karen Wingfield-Bond
UPDATE results SET candidate_id = '6186de25e3c88f3e' WHERE candidate_id = '39b3585c5686256d';  -- Karl Olson
UPDATE results SET candidate_id = '4e272a7eb6fe8937' WHERE candidate_id = '50bf4f388eea5f36';  -- Kasia Mastrangeli
UPDATE results SET candidate_id = 'b23f7f2dea017663' WHERE candidate_id = 'fdbd444de73d3349';  -- Kat Abughazaleh
UPDATE results SET candidate_id = 'f566bbf09e93e0ee' WHERE candidate_id = 'f15b6c03da1e9e17';  -- Kate Duncan
UPDATE results SET candidate_id = '2dd7fb3f0eee840a' WHERE candidate_id = '7518ef7ae4e1fb3c';  -- Kate McGrath
UPDATE results SET candidate_id = '64301795acdb2412' WHERE candidate_id = '7ec0cdbf8d6da6ab';  -- Kate Spears
UPDATE results SET candidate_id = 'b8451442f9c8de83' WHERE candidate_id = '44f52ef275a1053a';  -- Katey Baldassano
UPDATE results SET candidate_id = '0bccaf1ffc39e927' WHERE candidate_id = 'db245344c95d5ae0';  -- Katherine Bevan
UPDATE results SET candidate_id = '9403847c1208ce49' WHERE candidate_id = 'e4cecaef4959a714';  -- Katherine Davis Vega
UPDATE results SET candidate_id = '1c4874e41f356e4f' WHERE candidate_id = '7263d213c976a729';  -- Kathleen Johnson
UPDATE results SET candidate_id = '1c4874e41f356e4f' WHERE candidate_id = '4b7e4a4a76e882c9';  -- Kathleen Johnson
UPDATE results SET candidate_id = '1df5b9b8db9f5206' WHERE candidate_id = '70e738c48cfb1748';  -- Kathryn Straniero
UPDATE results SET candidate_id = '359b667a57c0855c' WHERE candidate_id = 'afe9e0275de66fc9';  -- Kathryne Stern
UPDATE results SET candidate_id = '122c45f88ddc7a3c' WHERE candidate_id = '445edce643cd3c23';  -- Katie Karam
UPDATE results SET candidate_id = '2cc2dcc81fb52d51' WHERE candidate_id = 'e94187ce027c8261';  -- Katrina Thompson
UPDATE results SET candidate_id = '0d540a4113977f31' WHERE candidate_id = 'dd29d173dc2201c3';  -- Keith D. Olson
UPDATE results SET candidate_id = '0d7459c33402a957' WHERE candidate_id = '2ab5adf79cc8e7cd';  -- Keith Pekau
UPDATE results SET candidate_id = '7d6267135cdf8f77' WHERE candidate_id = 'a0b2c5cd2002d87b';  -- Kelly Dittmann
UPDATE results SET candidate_id = '2febf5b054198d2b' WHERE candidate_id = '824484cb1dcf83ad';  -- Kelly Maron Horvath
UPDATE results SET candidate_id = '475799dfd7c8e1d8' WHERE candidate_id = '77b3156d1c9fdea5';  -- Kelly Sexton-Kelly
UPDATE results SET candidate_id = '255f51b50ee05f76' WHERE candidate_id = 'bd383fadccf9658c';  -- Kelly Young
UPDATE results SET candidate_id = '8d17b234e799a3ab' WHERE candidate_id = '9a5309a4634c670b';  -- Kelvin M. Oliver
UPDATE results SET candidate_id = 'a39d1c4ff5ebd056' WHERE candidate_id = '4c62bd96ca48eb51';  -- Ken Abosch
UPDATE results SET candidate_id = '5fb8de28de50c2ad' WHERE candidate_id = 'c0436c07424176e6';  -- Kenneth "Ken" Henderson
UPDATE results SET candidate_id = '030c5600aaca40ec' WHERE candidate_id = '1a3b873bae6cb6c1';  -- Kenneth E. Lyons, Jr.
UPDATE results SET candidate_id = '77f3b1039b0c9b2f' WHERE candidate_id = 'ffaf860eae892eb4';  -- Kenneth Jochum
UPDATE results SET candidate_id = 'c772f6098c790c9c' WHERE candidate_id = '2495f98f45c3cedc';  -- Kenneth Klein
UPDATE results SET candidate_id = '98da1e4fbb0e19d2' WHERE candidate_id = 'b68df2e808f87e10';  -- Kenneth R. Van Dyke
UPDATE results SET candidate_id = '128b80896792e5fc' WHERE candidate_id = 'ceb9296b2bdf6f57';  -- Kenneth Wallace "Kenootz" Keeler
UPDATE results SET candidate_id = '40cb91969e2852ce' WHERE candidate_id = '55e87a398d4f982a';  -- Kenneth Yerkes
UPDATE results SET candidate_id = 'bcb57ed579ce8c95' WHERE candidate_id = '5bf5a49f8e7a9553';  -- Kevin Canfield
UPDATE results SET candidate_id = '761b46bbf2fe11dd' WHERE candidate_id = 'd808fe8793ccdd60';  -- Kevin Collins
UPDATE results SET candidate_id = '57b157de16d8cb1b' WHERE candidate_id = 'b0c07e752481ca43';  -- Kevin Pokorny
UPDATE results SET candidate_id = '34f856974cd16c50' WHERE candidate_id = 'd1b21178d6de94f8';  -- Kevin R. McDermott
UPDATE results SET candidate_id = '588ee869ec824bb0' WHERE candidate_id = 'b544cd9abb946952';  -- Kevin Richards

-- Batch 4
UPDATE results SET candidate_id = '89b68ad52c4de4d3' WHERE candidate_id = '231ea4ef77904b64';  -- Kevin Ryan
UPDATE results SET candidate_id = '60bd646c1f5431ca' WHERE candidate_id = 'b5c3a70562b7c469';  -- Kiana L. Belcher
UPDATE results SET candidate_id = 'a3a695620d0bebd9' WHERE candidate_id = 'f383a1f43fd454e9';  -- Kim Page
UPDATE results SET candidate_id = '28db2d34a8713729' WHERE candidate_id = 'c8e232f969ab6f85';  -- Kimball Ladien
UPDATE results SET candidate_id = 'e69089967fae41a3' WHERE candidate_id = 'f5382fb5b668383c';  -- Kimberly C. Kidd
UPDATE results SET candidate_id = 'b01930c0c375c0d0' WHERE candidate_id = '32acece05095065f';  -- Kirk Albinson
UPDATE results SET candidate_id = '70cea2771a7ea9f3' WHERE candidate_id = '738d37c368458429';  -- Kisha E. McCaskill
UPDATE results SET candidate_id = '2dea784050f2184c' WHERE candidate_id = '6d099f090931aad9';  -- Kit P. Ketchmark
UPDATE results SET candidate_id = 'af77c5abe59f72ae' WHERE candidate_id = 'cc29793aa3081b32';  -- Kristian "Krissie" Harris
UPDATE results SET candidate_id = '834f8548d4989d55' WHERE candidate_id = 'f09ba7a7595ea5dd';  -- Kristin Cunningham
UPDATE results SET candidate_id = '9cc0559dd34df6e1' WHERE candidate_id = 'b55afe7c1a2c4d52';  -- Kristy Gilbert
UPDATE results SET candidate_id = '24aeb4d352df745e' WHERE candidate_id = '8ac47362032be782';  -- Kristy Merrill
UPDATE results SET candidate_id = '3d8195ae503981cd' WHERE candidate_id = 'ffc7a78f6d6ee408';  -- Kyle R. Hastings
UPDATE results SET candidate_id = '8a840b12bfb12d13' WHERE candidate_id = '186e71a92d4ad42b';  -- LAURA ELLMAN
UPDATE results SET candidate_id = '8a840b12bfb12d13' WHERE candidate_id = '2dea491a986b652f';  -- LAURA ELLMAN
UPDATE results SET candidate_id = '666f889f64d18b03' WHERE candidate_id = '012180d4be3989bd';  -- LAURA HOIS
UPDATE results SET candidate_id = '2f5c2a6d1270d617' WHERE candidate_id = 'a06c368cebf50a9f';  -- LAURA M. MURPHY
UPDATE results SET candidate_id = '970def43da64b0e2' WHERE candidate_id = '9db1242d69642bc3';  -- LAUREN "LAURIE" NOWAK
UPDATE results SET candidate_id = '970def43da64b0e2' WHERE candidate_id = '9e90bfaf927d14a9';  -- LAUREN "LAURIE" NOWAK
UPDATE results SET candidate_id = '8ad68a1c29fa7555' WHERE candidate_id = '0a7f5f87682db04c';  -- LAUREN UNDERWOOD
UPDATE results SET candidate_id = '8ad68a1c29fa7555' WHERE candidate_id = 'b38e9fa24447d2bf';  -- LAUREN UNDERWOOD
UPDATE results SET candidate_id = '8ad68a1c29fa7555' WHERE candidate_id = '272b47e5a512d73b';  -- LAUREN UNDERWOOD
UPDATE results SET candidate_id = '848478d75dba61b3' WHERE candidate_id = 'b818cffeb20901d6';  -- LESLIE ARMSTRONG-McLEOD
UPDATE results SET candidate_id = '58fd6b8e974ef010' WHERE candidate_id = 'ab49dc9ea8b923d8';  -- LINDA HOLMES
UPDATE results SET candidate_id = '58fd6b8e974ef010' WHERE candidate_id = '0568b582b35246b2';  -- LINDA HOLMES
UPDATE results SET candidate_id = '58fd6b8e974ef010' WHERE candidate_id = 'a88858241d414549';  -- LINDA HOLMES
UPDATE results SET candidate_id = 'f26d071d48551402' WHERE candidate_id = '767d0caaa70ccc1f';  -- LINDA R ROBERTSON
UPDATE results SET candidate_id = '19a039899f753c30' WHERE candidate_id = '0337093316df9532';  -- LIZ BISHOP
UPDATE results SET candidate_id = '9b18f0109a73ba75' WHERE candidate_id = '2901673496e9c8c0';  -- LaSandra Hutchinson
UPDATE results SET candidate_id = '2969afaa47475986' WHERE candidate_id = '0a55e7cc7dd8eb42';  -- Larry Berg
UPDATE results SET candidate_id = '4aafdb0e8e307a39' WHERE candidate_id = '58b069f3bac8a7da';  -- Larry McShane
UPDATE results SET candidate_id = '893b18d010fb36cd' WHERE candidate_id = '113902d198997e90';  -- Larry Reiner
UPDATE results SET candidate_id = 'b945c0b86b64e1fe' WHERE candidate_id = 'eed4b1c851eb5480';  -- Larry W. DeYoung
UPDATE results SET candidate_id = '0248d223b4b7a471' WHERE candidate_id = '925e5cb3c24833a5';  -- Laura Ann Cassidy-Hatchet
UPDATE results SET candidate_id = '314146bac6ab22c0' WHERE candidate_id = 'b3e9ae861bca95f9';  -- Laura Cardenas
UPDATE results SET candidate_id = '93aff84b9a51083c' WHERE candidate_id = '1796dcddfbfdaf5c';  -- Laura Faver Dias
UPDATE results SET candidate_id = '21db339a6fa454f7' WHERE candidate_id = '2ac2cb8bbf211838';  -- Laura Fine
UPDATE results SET candidate_id = 'b5f082e77c04e887' WHERE candidate_id = 'fa5a476bddb78b19';  -- Laura Hruska
UPDATE results SET candidate_id = 'abc788a9e0b416d9' WHERE candidate_id = 'ddbae09596e06263';  -- Laura J. Kreil
UPDATE results SET candidate_id = '8154858676a4b418' WHERE candidate_id = 'a096d463eb9e3af2';  -- Laura S. Ekstrom
UPDATE results SET candidate_id = '8154858676a4b418' WHERE candidate_id = 'e9b13cd14ebb1019';  -- Laura S. Ekstrom
UPDATE results SET candidate_id = 'bdccb80cf2f0e929' WHERE candidate_id = 'b3f3377fc15ac958';  -- Lauren Berkowitz Klauer
UPDATE results SET candidate_id = 'c1d7736f871917bb' WHERE candidate_id = 'bc870e4785b54ac6';  -- Lauren Klauer
UPDATE results SET candidate_id = '74758f2f06537871' WHERE candidate_id = 'cb1ba6111a342d9e';  -- Lauren Roman
UPDATE results SET candidate_id = '37938db4731faaaf' WHERE candidate_id = '3687e432e241de7c';  -- Laurence Patterson II
UPDATE results SET candidate_id = '46324432a1c232fe' WHERE candidate_id = 'afa284ccda905d14';  -- Lawrence L. Jackson
UPDATE results SET candidate_id = 'b4405fbf2e91455b' WHERE candidate_id = 'ed6d9901ca39f389';  -- Leah Collister-Lazzari
UPDATE results SET candidate_id = '58a4931a489668fc' WHERE candidate_id = '59e088fcd2ce52a9';  -- Leah Lussem
UPDATE results SET candidate_id = '164714ad7bfdc37d' WHERE candidate_id = 'a3566fc28b8efb90';  -- Leonard Munson
UPDATE results SET candidate_id = '29a01d64494abebf' WHERE candidate_id = '2249ae119e63b965';  -- Lester A. Ottenheimer
UPDATE results SET candidate_id = '13f2abd244c7d2d9' WHERE candidate_id = '3c5b1aadaba9f8e5';  -- Linda Dressler
UPDATE results SET candidate_id = '76975c45f6d5927f' WHERE candidate_id = '821c617356b3133f';  -- Linda Hovde
UPDATE results SET candidate_id = 'cf1e663ddbf79fe7' WHERE candidate_id = 'ea47c4a26605c17e';  -- Linda M. Hawkins
UPDATE results SET candidate_id = '1d4e6f38c1dc7700' WHERE candidate_id = '51303c2ed7f33462';  -- Linda O''Dowd
UPDATE results SET candidate_id = '1d144bb15793f25a' WHERE candidate_id = '57ca7e2b6780f41e';  -- Linda Tatum
UPDATE results SET candidate_id = '3a1e0006307b0188' WHERE candidate_id = '277416f1bd076678';  -- Lindsay Prigge
UPDATE results SET candidate_id = '7fde8d3c1c56eb09' WHERE candidate_id = 'ecd0821cfdbc6d72';  -- Lisa Carson
UPDATE results SET candidate_id = 'ecd3a4965b3827b7' WHERE candidate_id = 'f12e397b10b87dc2';  -- Lisa O''Donovan
UPDATE results SET candidate_id = '44619df493f41cdb' WHERE candidate_id = 'd0295e9dfa9e3a6e';  -- Lisa Stanton
UPDATE results SET candidate_id = '896526c0991457e6' WHERE candidate_id = 'c3c49e9dbdca6ab2';  -- Llona Lewis
UPDATE results SET candidate_id = '1aaf97fe924a533b' WHERE candidate_id = 'd83f6da31dea7e3b';  -- Lorena Gasca
UPDATE results SET candidate_id = '971824f57decc330' WHERE candidate_id = '22d7978e0226402d';  -- Loretta Wells
UPDATE results SET candidate_id = '62fa4c3b11051c60' WHERE candidate_id = '73855dd5de234e42';  -- Lori Leahy
UPDATE results SET candidate_id = 'c4e85485c9b00ec3' WHERE candidate_id = 'e92eb0027d7e26bd';  -- Lori Pierce
UPDATE results SET candidate_id = 'ef44c74f09fff70d' WHERE candidate_id = '59672c2436ed0ac9';  -- Lori Smith
UPDATE results SET candidate_id = '97cae2650c8c8e7d' WHERE candidate_id = 'b6c84144f43b1233';  -- Lori Thomas
UPDATE results SET candidate_id = '4b7c54d178ea5ddd' WHERE candidate_id = '8e256c71e2cd558a';  -- Louise Barnett
UPDATE results SET candidate_id = '4b7c54d178ea5ddd' WHERE candidate_id = '8a32bbc4eba81085';  -- Louise Barnett
UPDATE results SET candidate_id = '6ae15de91ef8b3b1' WHERE candidate_id = 'dc12278d416c6228';  -- Lucy Mierop
UPDATE results SET candidate_id = '8290ea584ba7cc5a' WHERE candidate_id = 'cecea551fe2486dd';  -- Luisa Ellenbogen
UPDATE results SET candidate_id = 'c690f87e487d2c58' WHERE candidate_id = 'df7514ee5ebbcd54';  -- Luiz Montoya
UPDATE results SET candidate_id = '03083688b4f8b917' WHERE candidate_id = '5e425c6b46a8798b';  -- Lus E Chavez
UPDATE results SET candidate_id = '20f631a2c88a9b31' WHERE candidate_id = 'e88af8fe9a210cbc';  -- Luz E. Rangel Raymond
UPDATE results SET candidate_id = '9c72a91b6628ce4e' WHERE candidate_id = '99dda83f29ce048e';  -- Lyvette Jones
UPDATE results SET candidate_id = '8362556eb6830362' WHERE candidate_id = 'daa52610ea48f57d';  -- MAGGIE WUNDERLY
UPDATE results SET candidate_id = 'ff1bc771a1775c13' WHERE candidate_id = '7df0eaa89198ec93';  -- MAHNOOR AHMAD
UPDATE results SET candidate_id = '970daac6e20a6f5f' WHERE candidate_id = 'dbe693dc68174538';  -- MARGARET "PEGGY" O''CONNELL
UPDATE results SET candidate_id = '6797fa5296ebddf8' WHERE candidate_id = '1164c5376db8cdb2';  -- MARGARET CROKE
UPDATE results SET candidate_id = 'bf59d169d9e1a9b7' WHERE candidate_id = '17fd403ef4efc5cd';  -- MARIE NEWMAN
UPDATE results SET candidate_id = 'bf59d169d9e1a9b7' WHERE candidate_id = '1b7c5a1095cfd12a';  -- MARIE NEWMAN
UPDATE results SET candidate_id = 'f99d2a23679ffcb7' WHERE candidate_id = 'badcd070910c6122';  -- MARK C. CURRAN JR.
UPDATE results SET candidate_id = '5f57554ebd30944b' WHERE candidate_id = 'a3e9af99453259e2';  -- MARK GUETHLE
UPDATE results SET candidate_id = 'd2582763dde123a7' WHERE candidate_id = '611f75029853efdd';  -- MARK JOSEPH CARROLL
UPDATE results SET candidate_id = 'd3f9514bfe5c0825' WHERE candidate_id = '1fe3a9a3bb72f704';  -- MARK RICE
UPDATE results SET candidate_id = '4b408c75b7fa907b' WHERE candidate_id = '5f86735da7bb6857';  -- MARNIE MICHELLE SLAVIN
UPDATE results SET candidate_id = '61c4478b8426d497' WHERE candidate_id = '118cd4dc9a53acea';  -- MARTHA "MARTI" DEUTER
UPDATE results SET candidate_id = 'd74b7d114c44459f' WHERE candidate_id = '6ecee49f10648057';  -- MARTIN McLAUGHLIN
UPDATE results SET candidate_id = '250d6fe4b6f37318' WHERE candidate_id = '1afbd25114d694ba';  -- MARY EDLY-ALLEN
UPDATE results SET candidate_id = '7e2dece959ea6730' WHERE candidate_id = '1e74eba6606333a0';  -- MATTHEW "MATT" DUBIEL
UPDATE results SET candidate_id = 'b65052a9609f99ae' WHERE candidate_id = 'e1858d811999223d';  -- MATTHEW BROLLEY
UPDATE results SET candidate_id = 'fc11f504f88f0ed6' WHERE candidate_id = '406b133dc9a7eb60';  -- MAURA HIRSCHAUER
UPDATE results SET candidate_id = 'fc11f504f88f0ed6' WHERE candidate_id = '68cf4d386e79f16b';  -- MAURA HIRSCHAUER
UPDATE results SET candidate_id = '5b79c599deb2b49f' WHERE candidate_id = '06f7e1225e5d86ab';  -- MAX SOLOMON
UPDATE results SET candidate_id = 'cb4fd1abbc3768bf' WHERE candidate_id = 'c117bb2bb46551ff';  -- MELINDA BUSH
UPDATE results SET candidate_id = '7e0a6bb78d944e6e' WHERE candidate_id = 'a77ff15712911e25';  -- MICHAEL C. CUDZIK
UPDATE results SET candidate_id = 'aef4bbdcdf328439' WHERE candidate_id = 'ce3b352587b4efe1';  -- MICHAEL CROWNER
UPDATE results SET candidate_id = 'fe8bf9985d0b5079' WHERE candidate_id = 'a6e439208139a917';  -- MICHAEL W. FRERICHS
UPDATE results SET candidate_id = 'fe8bf9985d0b5079' WHERE candidate_id = '1243394deabe2c89';  -- MICHAEL W. FRERICHS
UPDATE results SET candidate_id = 'fe8bf9985d0b5079' WHERE candidate_id = '3d107357f244d671';  -- MICHAEL W. FRERICHS
UPDATE results SET candidate_id = 'f24f96182733dee3' WHERE candidate_id = '3b2bb60f164de0bf';  -- MICHELLE MUSSMAN
UPDATE results SET candidate_id = 'f24f96182733dee3' WHERE candidate_id = '3293378d4cd05f48';  -- MICHELLE MUSSMAN
UPDATE results SET candidate_id = 'f24f96182733dee3' WHERE candidate_id = '3dc4235dabf43f2d';  -- MICHELLE MUSSMAN
UPDATE results SET candidate_id = 'e4bcce42abfe2aa5' WHERE candidate_id = '66390e016a17b200';  -- MIKE QUIGLEY
UPDATE results SET candidate_id = 'a58530b1df185e9e' WHERE candidate_id = '3575b605885ac369';  -- Malgorzata McGonigal
UPDATE results SET candidate_id = '8def5006350e696d' WHERE candidate_id = 'fa9b3127702bc3a8';  -- Marah Altenberg
UPDATE results SET candidate_id = '2638059aee6e1e9f' WHERE candidate_id = '42417f83c4bbb1f7';  -- Marcellus Wells
UPDATE results SET candidate_id = '5b89fc0e1aea3923' WHERE candidate_id = '92938333a590c25f';  -- Marcia Hollis-Bratcher
UPDATE results SET candidate_id = '588123cbabb5f7f5' WHERE candidate_id = '728fe1f56c8a57cb';  -- Margot Dallstream
UPDATE results SET candidate_id = '7617762168a9bb7b' WHERE candidate_id = '7c91577558673db0';  -- Maria A. Gallegos
UPDATE results SET candidate_id = 'ed8e3ade074e29fa' WHERE candidate_id = '1ad154d100395897';  -- Maria C. Moreno
UPDATE results SET candidate_id = '67da21f2142d7c38' WHERE candidate_id = '0373f0062c3fff78';  -- Maria Peterson
UPDATE results SET candidate_id = '67da21f2142d7c38' WHERE candidate_id = '61902ef52f5656ad';  -- Maria Peterson
UPDATE results SET candidate_id = '5a7d214d99b710db' WHERE candidate_id = 'bc400bc222c8771e';  -- Marianne Bailey
UPDATE results SET candidate_id = '3adf98bc3fa9d678' WHERE candidate_id = 'c15c0d4c077692d4';  -- Mario Ramirez
UPDATE results SET candidate_id = '394d38bbd3f196b3' WHERE candidate_id = 'bc05f0d5f0fb8a47';  -- Marissa Gutierrez
UPDATE results SET candidate_id = '57b7f2470d99b1aa' WHERE candidate_id = 'b87df4bba2889541';  -- Marjorie A. Manchen
UPDATE results SET candidate_id = '11626bb8d8d74b05' WHERE candidate_id = '1a3e0afb23f82e72';  -- Mark Anderson
UPDATE results SET candidate_id = '1d7d99225016c341' WHERE candidate_id = '474eb235880018c2';  -- Mark Arnold Fredrickson
UPDATE results SET candidate_id = '4bd01ad407f98dfd' WHERE candidate_id = 'd06c33acb50b43e7';  -- Mark Elkins
UPDATE results SET candidate_id = '56b149d2260f7035' WHERE candidate_id = 'd0cdc0323e787fb9';  -- Mark G. Benson
UPDATE results SET candidate_id = '2465ed7bb47b6137' WHERE candidate_id = '16140d4303229613';  -- Mark L. Walker
UPDATE results SET candidate_id = '81991db66c92245d' WHERE candidate_id = 'ef668a13a1e4dcf2';  -- Mark Miller
UPDATE results SET candidate_id = 'd15de5362d28d089' WHERE candidate_id = 'ecc294ed59e1918b';  -- Mark Mitchell
UPDATE results SET candidate_id = 'ed205ba9f99f727e' WHERE candidate_id = '0252139ec205582f';  -- Mark Stenberg
UPDATE results SET candidate_id = '15d82942019b17d0' WHERE candidate_id = '74bc4805b20d94fe';  -- Mark Votruba
UPDATE results SET candidate_id = '8951b2b0fde41680' WHERE candidate_id = 'b51fb8734011a68b';  -- Mark W. Smith
UPDATE results SET candidate_id = '753db3cacf3609bb' WHERE candidate_id = '8f60a9d49ba3a1eb';  -- Markita L. Alexander
UPDATE results SET candidate_id = '1f453b1127505ad7' WHERE candidate_id = 'f628a0027dbbe1c9';  -- Marlene Flahaven
UPDATE results SET candidate_id = '4b2a9398de89b172' WHERE candidate_id = 'c66c56b457ba44b2';  -- Marshelle "Lil Mama" Freeman
UPDATE results SET candidate_id = '0f651d84afb734a5' WHERE candidate_id = '91c81f74b5ee29cd';  -- Martin C. Maloney
UPDATE results SET candidate_id = '2e70f31ecfde0a5e' WHERE candidate_id = '27a9ba4cc121e458';  -- Martin J. Moylan
UPDATE results SET candidate_id = '6db73fa0c0e4a8c1' WHERE candidate_id = 'a05ecf86d566d5b9';  -- Martin McLaughlin
UPDATE results SET candidate_id = '6db73fa0c0e4a8c1' WHERE candidate_id = '5e48e5aab4b1c8e4';  -- Martin McLaughlin
UPDATE results SET candidate_id = '28c7887d07e3058c' WHERE candidate_id = '75b359bf69e5ed08';  -- Martin Pratscher
UPDATE results SET candidate_id = '38bf1800858d0a5d' WHERE candidate_id = '60d90d939e87729d';  -- Martina Mahaffey
UPDATE results SET candidate_id = 'b99c2a25948e9ede' WHERE candidate_id = 'c38366c78df410f5';  -- Martine L. Scheuerman
UPDATE results SET candidate_id = 'dac5efc608d678f8' WHERE candidate_id = 'ece555c98dbf778f';  -- Marvel Parker
UPDATE results SET candidate_id = '9d477fbbdde8e9a5' WHERE candidate_id = 'bc675ac1079e58b8';  -- Mary "May" Larry
UPDATE results SET candidate_id = '18e24a2a4b40bd26' WHERE candidate_id = '6eeb525cde70e16c';  -- Mary Anne Coleman
UPDATE results SET candidate_id = '132ace27e4ce96c5' WHERE candidate_id = '2ef62d4660676093';  -- Mary C. Krueger
UPDATE results SET candidate_id = '1721c1fc585c4065' WHERE candidate_id = '61c2421c1a695d06';  -- Mary Catuara
UPDATE results SET candidate_id = '57727384765ef736' WHERE candidate_id = '06155bcd1ff5eaf8';  -- Mary Edly-Allen
UPDATE results SET candidate_id = '57727384765ef736' WHERE candidate_id = '3d684694936e6da1';  -- Mary Edly-Allen
UPDATE results SET candidate_id = '0b3c84881f9e7756' WHERE candidate_id = 'f67d9b6f26b36d34';  -- Mary List
UPDATE results SET candidate_id = '8ffe2c57bd93b6d2' WHERE candidate_id = '717c75daff1078cb';  -- Mary Meirose Oppenheim
UPDATE results SET candidate_id = '41912519ba99675e' WHERE candidate_id = '613f0aadaf8d4194';  -- Mary Moodhe
UPDATE results SET candidate_id = '41912519ba99675e' WHERE candidate_id = 'df9b7a285242b313';  -- Mary Moodhe
UPDATE results SET candidate_id = '63df82e3c78aa7eb' WHERE candidate_id = '4b5a5965d10809b2';  -- Mary Patricia (Pat) Stack
UPDATE results SET candidate_id = 'a96c0f946923aa35' WHERE candidate_id = '52623d1b14ae9c46';  -- Mary Ramirez-Taconi
UPDATE results SET candidate_id = '139591e90f672e6e' WHERE candidate_id = '725f6196837e018f';  -- Mary Rob Clarke
UPDATE results SET candidate_id = '11b5e99de7edbdb2' WHERE candidate_id = '5b95812e06eaf3c5';  -- Mary Zofkie
UPDATE results SET candidate_id = '182e6b1003419e1e' WHERE candidate_id = 'f7d6b5fde4804252';  -- Marybelle Mandel
UPDATE results SET candidate_id = '35054266bba29aa6' WHERE candidate_id = '90048b132ac649bf';  -- Maryfrances Healy Leno
UPDATE results SET candidate_id = 'c6b87b92da001a7d' WHERE candidate_id = '5df8829f886ef9d5';  -- Mason B. Newell
UPDATE results SET candidate_id = '3c9528d3f09b1187' WHERE candidate_id = 'c316fd030aa8a05f';  -- Matt Glancy
UPDATE results SET candidate_id = '62cd364b5a68315c' WHERE candidate_id = 'bf366b85d024233e';  -- Matt Sheriff
UPDATE results SET candidate_id = 'ea2d862864aaa361' WHERE candidate_id = '70a364d1a4d6ec73';  -- Matthew Conroy
UPDATE results SET candidate_id = '2e3044f73a85048d' WHERE candidate_id = 'e18ef714434da411';  -- Matthew Holbrook
UPDATE results SET candidate_id = '0a99ea607b6a9816' WHERE candidate_id = '85d98a4e51fa7b76';  -- Matthew Marley Mitchell
UPDATE results SET candidate_id = '80474f27b2c032f9' WHERE candidate_id = 'b6f44669a45db08d';  -- Maureen C. Grady-Perovich
UPDATE results SET candidate_id = '401023f6c2887fe7' WHERE candidate_id = 'd67d5647f8516c97';  -- Maureen Flanagan Broderick
UPDATE results SET candidate_id = '0f8f2e3a5e33a153' WHERE candidate_id = 'ec0b522ad9ab6a06';  -- Maya L. Ganguly
UPDATE results SET candidate_id = '6c5a500e93403059' WHERE candidate_id = 'e7ae1c2676b00639';  -- Mazhar Khan
UPDATE results SET candidate_id = 'a8108448c5a63893' WHERE candidate_id = 'e0db893314cdf943';  -- Melanie L Myers
UPDATE results SET candidate_id = '8496db9c8ee8ecec' WHERE candidate_id = 'f1a40dccd10785f6';  -- Melissa Castillo
UPDATE results SET candidate_id = '718865d58142ac80' WHERE candidate_id = 'dae3b0d680d6c240';  -- Melissa Enright Taylor
UPDATE results SET candidate_id = '239b6376d2b45c0a' WHERE candidate_id = '2905ea901dc12a21';  -- Melissa Hulting
UPDATE results SET candidate_id = 'b59fb36e92dd0e62' WHERE candidate_id = 'c8bf8e7d3ed7c953';  -- Melissa Obrock
UPDATE results SET candidate_id = '087680ee660d0e48' WHERE candidate_id = '2f9530f1a7c8c0b4';  -- Melissa Owens
UPDATE results SET candidate_id = '22c5dae9c738d323' WHERE candidate_id = 'a79f7ae96109aad2';  -- Micaela G. Smith
UPDATE results SET candidate_id = '2c03a782b2504ead' WHERE candidate_id = 'ee4451e0bde6b268';  -- Michael A. Corrigan
UPDATE results SET candidate_id = '32b057c37e53896a' WHERE candidate_id = '53475bf822ddf19e';  -- Michael A. Pope
UPDATE results SET candidate_id = '521341ad4f32c501' WHERE candidate_id = '60a526df3eb0475a';  -- Michael B. Jenny
UPDATE results SET candidate_id = '1e650dbb2814ec01' WHERE candidate_id = '64d4b38e40e90500';  -- Michael Brown
UPDATE results SET candidate_id = 'd85a4c589fdaa6ab' WHERE candidate_id = 'dda152e0a6f6a15f';  -- Michael J. Aumiller
UPDATE results SET candidate_id = '8d8a5ba2f9e17e21' WHERE candidate_id = 'c509fca1aea2aa80';  -- Michael J. Ciavattone
UPDATE results SET candidate_id = '1627f09d06453425' WHERE candidate_id = '5b5f67bc6b0bb45b';  -- Michael J. Garvey
UPDATE results SET candidate_id = 'bdbb0b56c9eadc41' WHERE candidate_id = '6c51cfdf76f9bfbc';  -- Michael L. Karner
UPDATE results SET candidate_id = 'bdbb0b56c9eadc41' WHERE candidate_id = '2bc71bb86079cb01';  -- Michael L. Karner
UPDATE results SET candidate_id = 'ebc499e862e90ae2' WHERE candidate_id = 'b12e8df26629f9c6';  -- Michael M. Chvatal
UPDATE results SET candidate_id = '390d7e207170e8c4' WHERE candidate_id = 'd2b52ae4af265aaa';  -- Michael M. Lupo
UPDATE results SET candidate_id = '5b989b36704856fb' WHERE candidate_id = 'cf33c643a328d15b';  -- Michael Mann
UPDATE results SET candidate_id = '5b989b36704856fb' WHERE candidate_id = 'ce644e048319ae47';  -- Michael Mann
UPDATE results SET candidate_id = '45f9a140472234e2' WHERE candidate_id = '8eaef4ddb19bc167';  -- Michael Murphy
UPDATE results SET candidate_id = '0b7d2b3432d3f4af' WHERE candidate_id = '498b20d6795bf5b8';  -- Michael Pierce
UPDATE results SET candidate_id = '27cc78fd1dcb8008' WHERE candidate_id = 'b6bcab8c48e6b88d';  -- Michael Reiser
UPDATE results SET candidate_id = '27cc78fd1dcb8008' WHERE candidate_id = '826b6004de1f042e';  -- Michael Reiser
UPDATE results SET candidate_id = '3e266fcba9952454' WHERE candidate_id = 'b559ac55f3e96357';  -- Michael Shackleton
UPDATE results SET candidate_id = '6c6d96177b8579d1' WHERE candidate_id = '7ae5d9b17a36d56c';  -- Michael Smith
UPDATE results SET candidate_id = '822a62991ed014df' WHERE candidate_id = 'aa158da21dff2d48';  -- Michael Thomas
UPDATE results SET candidate_id = '2fa8cd5bdae9d25a' WHERE candidate_id = '6be24abd68aeb270';  -- Michael W. Glotz
UPDATE results SET candidate_id = '259ae27303b7dbbb' WHERE candidate_id = '588d4762ed341bee';  -- Michaeline Skibinski
UPDATE results SET candidate_id = 'b3e37cfb02d9a689' WHERE candidate_id = 'cd6433382d8dd4c8';  -- Michele Helsel
UPDATE results SET candidate_id = '45e6f22bcafb502b' WHERE candidate_id = 'aa34e28b21aa5fe0';  -- Michele Turner
UPDATE results SET candidate_id = '4bda1fd75e175a23' WHERE candidate_id = '621bfade0bd9808c';  -- Michelle Fisher
UPDATE results SET candidate_id = '3ab4bfe6bb887260' WHERE candidate_id = 'aa2e5652c96cc791';  -- Michelle Nelson
UPDATE results SET candidate_id = '97acb157838dbae8' WHERE candidate_id = 'f390699726a6f331';  -- Midalia Nevarez
UPDATE results SET candidate_id = '4e173118d147c365' WHERE candidate_id = '528a99af6bdf461c';  -- Mike Burns
UPDATE results SET candidate_id = '5fcaac96f6818474' WHERE candidate_id = 'ea433e79bb840c5b';  -- Mike Goodman
UPDATE results SET candidate_id = '344ce48a709eb964' WHERE candidate_id = 'eecec4430b90162d';  -- Mike Moran

-- Batch 5
UPDATE results SET candidate_id = '41acfa3c12c99b6c' WHERE candidate_id = 'f8fa2b7ea8bbcb8a';  -- Mike Porfirio
UPDATE results SET candidate_id = 'd14c8278d3100304' WHERE candidate_id = '13faaebf23703204';  -- Mike Quigley
UPDATE results SET candidate_id = 'd14c8278d3100304' WHERE candidate_id = '35b197a57943a3d1';  -- Mike Quigley
UPDATE results SET candidate_id = '743370c616e2021b' WHERE candidate_id = 'f497dcff84602363';  -- Mike Simmons
UPDATE results SET candidate_id = 'eaffb825fe454ec9' WHERE candidate_id = '66b9c9d917fe75d4';  -- Mike Terson
UPDATE results SET candidate_id = 'd7041c0b78037bac' WHERE candidate_id = '6250c18198120fba';  -- Miriam Cruz
UPDATE results SET candidate_id = 'dac97f4f7dcc58d5' WHERE candidate_id = 'd93ed23a3f42b23a';  -- Mitchell Milenkovic
UPDATE results SET candidate_id = '735aafb31b0d2d01' WHERE candidate_id = 'b110781445c7fdbb';  -- Mohammed Azam Hussain
UPDATE results SET candidate_id = '4bb2ef3d9cb2a612' WHERE candidate_id = 'd40d4cf2f60b2f29';  -- Monica Fletcher
UPDATE results SET candidate_id = '690cb823e54f00b6' WHERE candidate_id = 'abc2d9e97dadb408';  -- Monica M. Gordon
UPDATE results SET candidate_id = 'a4ff72819caf7a06' WHERE candidate_id = 'd422d17de014a8ae';  -- Monica Yvette Holden
UPDATE results SET candidate_id = '1c6d30b8d1a1d7d3' WHERE candidate_id = 'ec59e187603ee6eb';  -- Monika Stajniak
UPDATE results SET candidate_id = '6a2abf7eeea4f898' WHERE candidate_id = '138608ded54daa28';  -- Morgan Coghill
UPDATE results SET candidate_id = '52be5fb6e2bc008c' WHERE candidate_id = '9243419686b4ac73';  -- Morgan Dubiel
UPDATE results SET candidate_id = '4190f1ca616d4ae7' WHERE candidate_id = '43ded3789e35532d';  -- Muhaymin Muhammad
UPDATE results SET candidate_id = 'd6af8268b737151f' WHERE candidate_id = 'f318fbc536dd71b8';  -- Mychal J. Toscas
UPDATE results SET candidate_id = '7eb0066379cc0a84' WHERE candidate_id = 'd521b259db048861';  -- Myra Gardner
UPDATE results SET candidate_id = '7afd6163dc2fb6d2' WHERE candidate_id = '9d2e3b48dae37da0';  -- NANCY ROTERING
UPDATE results SET candidate_id = '955ccf53f6fe311b' WHERE candidate_id = '09230cc27a0538f4';  -- NANCY SHEPHERDSON
UPDATE results SET candidate_id = '13c80df0cc294034' WHERE candidate_id = 'b923cc6ec2df7e1d';  -- NICOLE LA HA
UPDATE results SET candidate_id = 'e8178348e0dd6bb0' WHERE candidate_id = 'bef449fead70d6ab';  -- NIKI CONFORTI
UPDATE results SET candidate_id = 'e8178348e0dd6bb0' WHERE candidate_id = '413dcd863b9c4414';  -- NIKI CONFORTI
UPDATE results SET candidate_id = '506b28cee564728a' WHERE candidate_id = '7fa3b767c460b54a';  -- NO
UPDATE results SET candidate_id = '506b28cee564728a' WHERE candidate_id = 'ff8ab8cb370dac25';  -- NO
UPDATE results SET candidate_id = 'accff35961a09261' WHERE candidate_id = 'e60530c2a26b5bd6';  -- NORMA HERNANDEZ
UPDATE results SET candidate_id = '40ca4d0d4621db17' WHERE candidate_id = 'ff10da12f3cf4143';  -- Nabeela Syed
UPDATE results SET candidate_id = '40ca4d0d4621db17' WHERE candidate_id = '69a32cecf5fccdce';  -- Nabeela Syed
UPDATE results SET candidate_id = '684128f2021ceb54' WHERE candidate_id = '704b59f3f60967f9';  -- Naema Abraham
UPDATE results SET candidate_id = '2c354d7ba372867b' WHERE candidate_id = '63ee098041e65692';  -- Nan Weiss-Ham
UPDATE results SET candidate_id = '22691ab777686148' WHERE candidate_id = '6c54ff80627cd369';  -- Nancy M. O''Connor
UPDATE results SET candidate_id = '96d788e6b04e1040' WHERE candidate_id = '42d4f172080e461e';  -- Nancy N. Robb
UPDATE results SET candidate_id = 'd51e3b75eb992877' WHERE candidate_id = 'c5e33dbaf41c2a44';  -- Nancy Novit
UPDATE results SET candidate_id = '718cd83cdd34cf34' WHERE candidate_id = 'c1eb9ba37741e5a9';  -- Nancy Rita
UPDATE results SET candidate_id = '8250cc65b3b03e78' WHERE candidate_id = 'd4dc757dd6592a4a';  -- Nancy Ross Dribin
UPDATE results SET candidate_id = '5bb04c4a6a2daeb7' WHERE candidate_id = 'cbfc2d33f8438bff';  -- Natalie Opila
UPDATE results SET candidate_id = '7cd0318bdae8b4c8' WHERE candidate_id = 'f1a1d65cb9ec7ec3';  -- Nazario Garcia
UPDATE results SET candidate_id = '383f8f24faebe007' WHERE candidate_id = '12914d834eeca0cd';  -- Nelda Munoz
UPDATE results SET candidate_id = '277266d0fa31523b' WHERE candidate_id = 'dc5d68721279789b';  -- Nicholas Caprio
UPDATE results SET candidate_id = '27a83504eae1d126' WHERE candidate_id = '9d53ae705296a04c';  -- Nicholas Hutchison
UPDATE results SET candidate_id = 'b86a5dbf72ca1701' WHERE candidate_id = 'bd5b182d6b6be8b9';  -- Nicholas J. Pecora
UPDATE results SET candidate_id = '445f1276956e6334' WHERE candidate_id = '693e598672ad2bee';  -- Nicholas P. Bobis
UPDATE results SET candidate_id = '3b6080cd734014d6' WHERE candidate_id = 'a958c268d36a1ba9';  -- Nicholas Scipione
UPDATE results SET candidate_id = 'df1a192dd43493a3' WHERE candidate_id = '931c1d2d37533a90';  -- Nichole Lies
UPDATE results SET candidate_id = 'dea954fd38cc7995' WHERE candidate_id = 'fb2975d5665a1b99';  -- Nick Pyati
UPDATE results SET candidate_id = '56806ca52329612f' WHERE candidate_id = 'f7db1c3885c22f45';  -- Nicolle Grasse
UPDATE results SET candidate_id = '0010ed095a4d1d15' WHERE candidate_id = '291bafe0401a1eef';  -- No Candidate
UPDATE results SET candidate_id = '0010ed095a4d1d15' WHERE candidate_id = 'e93b0d998056d7e9';  -- No Candidate
UPDATE results SET candidate_id = '0010ed095a4d1d15' WHERE candidate_id = '63eb9609113d614e';  -- No Candidate
UPDATE results SET candidate_id = '09d913c0011f03c7' WHERE candidate_id = '3629a2224f46a40a';  -- No Candidate 2
UPDATE results SET candidate_id = '151ddd996d8ced82' WHERE candidate_id = '6412663af0a3fbc9';  -- No Candidate 3
UPDATE results SET candidate_id = '4df239db15ca09cc' WHERE candidate_id = 'ff3a3d66c8ee56ee';  -- No Candidate 4
UPDATE results SET candidate_id = '3f19b2bd5b359ea4' WHERE candidate_id = '9de507b7c992d6d6';  -- Noelle Sullivan
UPDATE results SET candidate_id = 'a3d791b5de4de7fc' WHERE candidate_id = 'eba169fa3714e653';  -- Nyota T. Figgs
UPDATE results SET candidate_id = '1e3cf5547ad4b10d' WHERE candidate_id = '756a391f7591e94e';  -- Nyree D. Ford
UPDATE results SET candidate_id = 'd761d85fb627b08a' WHERE candidate_id = '54e04f575d4029c4';  -- Over Votes
UPDATE results SET candidate_id = 'd761d85fb627b08a' WHERE candidate_id = 'df2009b18f7c3fb1';  -- Over Votes
UPDATE results SET candidate_id = 'd761d85fb627b08a' WHERE candidate_id = '0b71e61e1e17c345';  -- Over Votes
UPDATE results SET candidate_id = 'd761d85fb627b08a' WHERE candidate_id = '989f2066e72f5b80';  -- Over Votes
UPDATE results SET candidate_id = 'd761d85fb627b08a' WHERE candidate_id = '9291cf28f26d2002';  -- Over Votes
UPDATE results SET candidate_id = 'd761d85fb627b08a' WHERE candidate_id = 'f9f43aae75ffd8de';  -- Over Votes
UPDATE results SET candidate_id = 'fbf19f8d454ebc97' WHERE candidate_id = '8caa4bc721d9c703';  -- PAT QUINN
UPDATE results SET candidate_id = '1076f0adf8365a56' WHERE candidate_id = '725eafe8d6fef7f2';  -- PATRICK J. HYNES
UPDATE results SET candidate_id = '83826fb4bbf6ecd9' WHERE candidate_id = 'd42a76417ff6664f';  -- PATRICK WATSON
UPDATE results SET candidate_id = '83826fb4bbf6ecd9' WHERE candidate_id = 'e7e7c227d895c317';  -- PATRICK WATSON
UPDATE results SET candidate_id = 'c7d5d26186d5a2e1' WHERE candidate_id = '011e50231ff0194d';  -- PAUL SCHIMPF
UPDATE results SET candidate_id = '6bfee468133ecd2d' WHERE candidate_id = '4283c735e8de24d1';  -- PEGGY HUBBARD
UPDATE results SET candidate_id = 'd5010794bbada3b8' WHERE candidate_id = '33d75c64fbfa6310';  -- PETER JANKO
UPDATE results SET candidate_id = 'd5010794bbada3b8' WHERE candidate_id = '1ae382a9c567af90';  -- PETER JANKO
UPDATE results SET candidate_id = 'd5010794bbada3b8' WHERE candidate_id = '45f0e3af4462c10c';  -- PETER JANKO
UPDATE results SET candidate_id = '3b89976acba9b260' WHERE candidate_id = 'f6c074e7b0316fb1';  -- PETER KOPSAFTIS
UPDATE results SET candidate_id = '67feceee79aac015' WHERE candidate_id = '2d55394d0b4ae9ac';  -- PHILLIP OWEN WOOD
UPDATE results SET candidate_id = '81364377183b1a59' WHERE candidate_id = '079b3795a1dcf5bf';  -- PRESTON NELSON
UPDATE results SET candidate_id = '1f35eb36690e4b96' WHERE candidate_id = 'ea55a05e21e10e2c';  -- Pamela Alper
UPDATE results SET candidate_id = '6efdcc266a156275' WHERE candidate_id = 'dc9012c9cb16a311';  -- Pamela J. Kende
UPDATE results SET candidate_id = '04251f69e774c7de' WHERE candidate_id = '50086e9c98491191';  -- Pamela M. Jeanes
UPDATE results SET candidate_id = 'c28dfc0b051dfcf7' WHERE candidate_id = 'b63194130c101ad4';  -- Patricia A. Brown
UPDATE results SET candidate_id = '33e7c99ae8e40094' WHERE candidate_id = '77164ea0f42d7dde';  -- Patricia Camalliere
UPDATE results SET candidate_id = '845c319345e1464d' WHERE candidate_id = 'a80427cb3fcb5f58';  -- Patricia Chao-Malave
UPDATE results SET candidate_id = 'd59175f6a8ce3d66' WHERE candidate_id = '859fcb8ad7102712';  -- Patricia Harris
UPDATE results SET candidate_id = '1cca940141b561ba' WHERE candidate_id = '39fa3f5baa7beb7e';  -- Patricia Savage-Williams
UPDATE results SET candidate_id = 'dd2846ae5b928ce7' WHERE candidate_id = 'e106df4b868cd104';  -- Patrick A. Horcher
UPDATE results SET candidate_id = '442a061aabd71efd' WHERE candidate_id = '1a2ee13c1ce89803';  -- Patrick Conway
UPDATE results SET candidate_id = '9f8f7ae06a41d551' WHERE candidate_id = '55ef00d1f827a397';  -- Patrick Kinnane
UPDATE results SET candidate_id = '3a228509c325192c' WHERE candidate_id = '6b1f1c8b07fa313a';  -- Patrick Liapes
UPDATE results SET candidate_id = 'acaa6b02c0dd2e09' WHERE candidate_id = 'b720be7f626fc4ae';  -- Paul Alongi
UPDATE results SET candidate_id = '9ea1fde5066dd7e6' WHERE candidate_id = '8c0d8c3de52ad942';  -- Paul Frank
UPDATE results SET candidate_id = 'a0f7c0ee7ca138cc' WHERE candidate_id = '6b384800742acd84';  -- Paul Friedman
UPDATE results SET candidate_id = '09ffd73253f484e1' WHERE candidate_id = '17a180f07eb4c6be';  -- Paul Smith
UPDATE results SET candidate_id = '2da68db2d72f2b4e' WHERE candidate_id = 'bbee5d99f98c4c47';  -- Paul W. Saladino
UPDATE results SET candidate_id = '1f638aaad237b81c' WHERE candidate_id = '41f6fd0f3a48e1b5';  -- Paul Zangara
UPDATE results SET candidate_id = '1f638aaad237b81c' WHERE candidate_id = '127dcba959d978d3';  -- Paul Zangara
UPDATE results SET candidate_id = '66aafbe425a15b34' WHERE candidate_id = 'e22403b48be2f8a1';  -- Paula Jacobsen
UPDATE results SET candidate_id = '10a1506d33f16837' WHERE candidate_id = '82b5b5fc8855137d';  -- Paulette Greenberg
UPDATE results SET candidate_id = '695413775d43596d' WHERE candidate_id = 'c2e6047353474bec';  -- Peggy Peterson
UPDATE results SET candidate_id = '043abc18b0a4a7d7' WHERE candidate_id = 'a28dd1b4e4647262';  -- Penny Lundquist
UPDATE results SET candidate_id = '0159e0f1b4188762' WHERE candidate_id = '7e199f6befc995ea';  -- Peter D. Theodore
UPDATE results SET candidate_id = '2999a300fb6f23d8' WHERE candidate_id = 'c2c896b480d13347';  -- Peter R. Dombrowski
UPDATE results SET candidate_id = '5d185e54ba97888e' WHERE candidate_id = 'b746a128e2db14a0';  -- Phil Andrew
UPDATE results SET candidate_id = '2a9f07c70a6b56ac' WHERE candidate_id = '5008d9b138499e36';  -- Phillip S. Abed
UPDATE results SET candidate_id = '4640af6ed4ed2da7' WHERE candidate_id = '9da169fc7c83c5e2';  -- Phyllis Lubinski
UPDATE results SET candidate_id = '17e57a3094a83bf1' WHERE candidate_id = 'd3c640083834ed62';  -- Phyllis M. Saunders
UPDATE results SET candidate_id = 'ee1751db263869af' WHERE candidate_id = 'c6dc2c555ed11786';  -- Prince Reed
UPDATE results SET candidate_id = 'a4267af9ecf6ea96' WHERE candidate_id = '31ae3fbee05702c6';  -- RACHEL DAVIS
UPDATE results SET candidate_id = '8309fbcd0b8c61ab' WHERE candidate_id = '0241dce759937d42';  -- RACHEL VENTURA
UPDATE results SET candidate_id = 'f516d30cbc718aa2' WHERE candidate_id = '23e677aa94ecb0a0';  -- RAJA KRISHNAMOORTHI
UPDATE results SET candidate_id = 'f516d30cbc718aa2' WHERE candidate_id = '242fe264517a4653';  -- RAJA KRISHNAMOORTHI
UPDATE results SET candidate_id = 'f516d30cbc718aa2' WHERE candidate_id = 'cfbb8b2008f75005';  -- RAJA KRISHNAMOORTHI
UPDATE results SET candidate_id = '8c90027b88d517b0' WHERE candidate_id = '64c425d1df3af0fe';  -- RANDI OLSON
UPDATE results SET candidate_id = '93d76b90b4dd7998' WHERE candidate_id = '6e4c5bedc20c9fbe';  -- RAYMOND A. LOPEZ
UPDATE results SET candidate_id = 'c9e4dc76b045a872' WHERE candidate_id = 'ad529238027cbfb5';  -- RENATO MARIOTTI
UPDATE results SET candidate_id = 'c9e4dc76b045a872' WHERE candidate_id = '1624980346c5ba0c';  -- RENATO MARIOTTI
UPDATE results SET candidate_id = '981dc603d7d2f65e' WHERE candidate_id = '220d184ab69993e0';  -- RICHARD C. IRVIN
UPDATE results SET candidate_id = '4b11663e97921695' WHERE candidate_id = '18965aaa40b15700';  -- RICHARD J. DURBIN
UPDATE results SET candidate_id = '26a03ba81ad89808' WHERE candidate_id = '5a4de1628949103a';  -- RICHARD JANOR
UPDATE results SET candidate_id = '3918ebcc3b5124db' WHERE candidate_id = 'e7ac07b3e9cc9fb6';  -- RITA MAYFIELD
UPDATE results SET candidate_id = 'a889571b5ad4b966' WHERE candidate_id = '39191cf64c39bcaa';  -- ROBERT "BOBBY" PITON
UPDATE results SET candidate_id = '2fd6f4a57706dff4' WHERE candidate_id = '227a0720a2397ed3';  -- ROBERT "ROB" CRUZ
UPDATE results SET candidate_id = 'f8783e93439c147b' WHERE candidate_id = 'a7d4f763fe8b3db4';  -- ROBERT "RUSTY" STEVENS
UPDATE results SET candidate_id = '8cd111a347909843' WHERE candidate_id = 'ce8361057bd05772';  -- ROBERT MARSHALL
UPDATE results SET candidate_id = '8cd111a347909843' WHERE candidate_id = '4a3352d17579855f';  -- ROBERT MARSHALL
UPDATE results SET candidate_id = '5f76b33adadd87ba' WHERE candidate_id = '1d6c97e4dbeb8f06';  -- RaDonna Brown
UPDATE results SET candidate_id = '0e97f4d8541e3840' WHERE candidate_id = 'e41a4acf4002504f';  -- Rachel H. Forsyth-Tuerck
UPDATE results SET candidate_id = '0e97f4d8541e3840' WHERE candidate_id = 'dcf4fb57c560a968';  -- Rachel H. Forsyth-Tuerck
UPDATE results SET candidate_id = '4500b60abc06de69' WHERE candidate_id = 'b8a7c3deddda9110';  -- Rachel Marroquin
UPDATE results SET candidate_id = '81ce177a37ffcfdc' WHERE candidate_id = '91e21d354709dbd4';  -- Rajkumari Chhatwani
UPDATE results SET candidate_id = '0ebc04706a9b8479' WHERE candidate_id = '1cf4678c60158d78';  -- Ramanda Bond
UPDATE results SET candidate_id = '1144de58c87e7d23' WHERE candidate_id = 'f4796a09a2100360';  -- Ramonde D. Williams
UPDATE results SET candidate_id = '1e7b9fd98b35c7de' WHERE candidate_id = '32d9487c75f8202a';  -- Randall K. Blakey
UPDATE results SET candidate_id = '73c6f84d0bf9ed62' WHERE candidate_id = 'e47a476f4ed867c7';  -- Ray C. Banks
UPDATE results SET candidate_id = 'ae0f1ab5e9a490dc' WHERE candidate_id = 'df1b929036f6c5cb';  -- Raymond E. Massie
UPDATE results SET candidate_id = '83ccf6aed2d1fe88' WHERE candidate_id = 'bd5319737f4632b9';  -- Rebecca Pfisterer
UPDATE results SET candidate_id = '0872bcc49e8b4cb6' WHERE candidate_id = '1bca1ded135801b9';  -- Rebekah Metts-Childers
UPDATE results SET candidate_id = '180c8023622e461b' WHERE candidate_id = '4026eb0264a56199';  -- Regina Houston
UPDATE results SET candidate_id = '0ad045fe2484fe3a' WHERE candidate_id = 'cec1a74af86eca8a';  -- Renee N. Harding
UPDATE results SET candidate_id = 'f19a253e6d220996' WHERE candidate_id = 'dd6e1fd7fdaff065';  -- Renita D. Davis
UPDATE results SET candidate_id = '22b159f783fbdffe' WHERE candidate_id = 'd7d82982cd7a69cd';  -- Respicio F. Vazquez
UPDATE results SET candidate_id = '4e6594460cdec73b' WHERE candidate_id = 'a881f5ec1c901a45';  -- Rezwanul Haque
UPDATE results SET candidate_id = 'ccfdfba17ee604a3' WHERE candidate_id = 'ff5ea11dc0b14a3a';  -- Ricardo D. Spivey
UPDATE results SET candidate_id = '02b377d4677b4aea' WHERE candidate_id = 'c7ef3f93f5b56717';  -- Rich Grochowski
UPDATE results SET candidate_id = '449b65c56e35ebc5' WHERE candidate_id = '71ae56dc44fec3c5';  -- Richard A. Brogan
UPDATE results SET candidate_id = '8a050da3aba8b6bb' WHERE candidate_id = '9c562a1f66f1dc35';  -- Richard A. Sloan
UPDATE results SET candidate_id = '8c4ed6f5224ef492' WHERE candidate_id = 'b84b4a97930c2a79';  -- Richard C. McCarthy
UPDATE results SET candidate_id = '21d62c024d1c369f' WHERE candidate_id = '9d20ef9c4efa5fb6';  -- Richard Keenley
UPDATE results SET candidate_id = '83b5ca11111491c3' WHERE candidate_id = 'b70bac975b905e9f';  -- Richard Mayers
UPDATE results SET candidate_id = '1a6d5547d02fcfaa' WHERE candidate_id = '03e8ed0fbed39c4c';  -- Richard Patinkin
UPDATE results SET candidate_id = '852ce1d9a98d7573' WHERE candidate_id = '09af805b17660797';  -- Rita Mayfield
UPDATE results SET candidate_id = '6b8589f10a167cf1' WHERE candidate_id = 'c5e34976cb9fb0a7';  -- Rob Loehr
UPDATE results SET candidate_id = '942e21881d6521cc' WHERE candidate_id = 'a71a8fcd716f8053';  -- Robert B. Rognstad
UPDATE results SET candidate_id = 'a8ae8b3167a2685d' WHERE candidate_id = 'e17eda2c71192dbe';  -- Robert Bowe
UPDATE results SET candidate_id = '1bbeeb1097f72420' WHERE candidate_id = '8d15d32dd35010d9';  -- Robert Dearborn
UPDATE results SET candidate_id = 'e1e2912cf7a14361' WHERE candidate_id = 'eb4549e7c78b4555';  -- Robert E. Maloney
UPDATE results SET candidate_id = '58f259830d761afe' WHERE candidate_id = 'c775ddc268fa96af';  -- Robert Farr
UPDATE results SET candidate_id = '3d3ce468b303c513' WHERE candidate_id = '8474724218b44edd';  -- Robert J. Lovero
UPDATE results SET candidate_id = 'a0651a617e1892e8' WHERE candidate_id = 'bd9c6b6adadc6a1b';  -- Robert Jones
UPDATE results SET candidate_id = 'd2d4c36a38bad0ff' WHERE candidate_id = 'c9448a42af8d30c9';  -- Robert L. Benton
UPDATE results SET candidate_id = '5509e3f9c735dc39' WHERE candidate_id = '75eac37fc35b8153';  -- Robert M. Zubak
UPDATE results SET candidate_id = 'd9eb97547bd2fa72' WHERE candidate_id = 'ec603f3e5cd23077';  -- Robert Windon
UPDATE results SET candidate_id = 'cf33ccef770fa7d6' WHERE candidate_id = '1486c7bbcf33a69e';  -- Roberto Botello
UPDATE results SET candidate_id = '8b25f25c7085b934' WHERE candidate_id = '3d933ef42c205b48';  -- Rocio Cleveland
UPDATE results SET candidate_id = '8b25f25c7085b934' WHERE candidate_id = 'e3b6d60bfa5ba675';  -- Rocio Cleveland
UPDATE results SET candidate_id = '24e186c0b14ca568' WHERE candidate_id = '658c227d6f0df9ea';  -- Rodney Cummings
UPDATE results SET candidate_id = '2925a9a5a5084851' WHERE candidate_id = '55da6f51acbcb980';  -- Rodrick L. Jefferson
UPDATE results SET candidate_id = '6ba8e2ab006396c3' WHERE candidate_id = 'f3c16207d66a59a8';  -- Roger A. Agpawa
UPDATE results SET candidate_id = '072fcaeebc2d2c5c' WHERE candidate_id = '68c7557a1512881f';  -- Roger Glass
UPDATE results SET candidate_id = '25e64151b49e9d74' WHERE candidate_id = '5a4b227ec6075d83';  -- Roger Romanelli
UPDATE results SET candidate_id = '95c7198510975179' WHERE candidate_id = 'a474580d6a68a70b';  -- Ronald Brown
UPDATE results SET candidate_id = '087c819bd1ef33e9' WHERE candidate_id = '9e3cdf4e78f8a26b';  -- Ronald Heveran
UPDATE results SET candidate_id = '6ae7db736674aaff' WHERE candidate_id = '931127e9582e45ff';  -- Ronald Nightengale
UPDATE results SET candidate_id = '945fdc2346ab2130' WHERE candidate_id = 'a083ead4ba852762';  -- Rosa Jos
UPDATE results SET candidate_id = 'b8dbe08eab9a888e' WHERE candidate_id = '0478770e0147658e';  -- Ryan T. Buckley
UPDATE results SET candidate_id = '3ef3f7064c3c50ac' WHERE candidate_id = '4d1139901caccb0f';  -- Ryan VenHorst
UPDATE results SET candidate_id = '06c522432203a067' WHERE candidate_id = 'f33f65b982126e69';  -- SADIA COVERT
UPDATE results SET candidate_id = 'a2d53e5255c31c44' WHERE candidate_id = 'af462c42e10336d3';  -- SAM YINGLING
UPDATE results SET candidate_id = '9fee77939c9b65f6' WHERE candidate_id = '5ec172ad1ffcd9db';  -- SCOTT BLOOMQUIST
UPDATE results SET candidate_id = '01805e4384e6f907' WHERE candidate_id = '8f17b854b1025144';  -- SCOTT DRURY
UPDATE results SET candidate_id = '283de6cf4c34c361' WHERE candidate_id = 'bb3854d983bcfe4c';  -- SCOTT R. KASPAR
UPDATE results SET candidate_id = '1c4258f0e3abd584' WHERE candidate_id = 'a6d3c4cf59f56303';  -- SCOTT SCHLUTER
UPDATE results SET candidate_id = '07e1dff8c4d71628' WHERE candidate_id = '27578df03143988f';  -- SEAN CASTEN
UPDATE results SET candidate_id = '07e1dff8c4d71628' WHERE candidate_id = 'e184370ee18cf989';  -- SEAN CASTEN
UPDATE results SET candidate_id = '07e1dff8c4d71628' WHERE candidate_id = '7bc522488a638898';  -- SEAN CASTEN
UPDATE results SET candidate_id = '07e1dff8c4d71628' WHERE candidate_id = 'dbda8f18a2a6a348';  -- SEAN CASTEN
UPDATE results SET candidate_id = 'cb9f17ee6183ae54' WHERE candidate_id = '62edfee7933f1d89';  -- SETH LEWIS
UPDATE results SET candidate_id = 'cb9f17ee6183ae54' WHERE candidate_id = 'cb515bbc2873277f';  -- SETH LEWIS
UPDATE results SET candidate_id = '8c69750cd080f0ad' WHERE candidate_id = '3c5c5cdcaf091d7a';  -- SHANNON L. TERESI
UPDATE results SET candidate_id = '57aa3f01561112b1' WHERE candidate_id = 'd0289ed0a259b1a7';  -- SHARON FAIRLEY
UPDATE results SET candidate_id = 'a3fd56b70f18fbf1' WHERE candidate_id = '451681089ac65870';  -- SIDNEY MOORE
UPDATE results SET candidate_id = 'd58dc13cff656145' WHERE candidate_id = 'ceeb060ede974e80';  -- SILVANA TABARES
UPDATE results SET candidate_id = 'fa530c6fd8cdec52' WHERE candidate_id = '079aa99341d7f666';  -- STEPHANIE A. KIFOWIT
UPDATE results SET candidate_id = 'fa530c6fd8cdec52' WHERE candidate_id = '27276932d287f65c';  -- STEPHANIE A. KIFOWIT
UPDATE results SET candidate_id = 'fa530c6fd8cdec52' WHERE candidate_id = 'ec4ca4588f23ced8';  -- STEPHANIE A. KIFOWIT
UPDATE results SET candidate_id = '04e82bad490336ce' WHERE candidate_id = '74608beaead82870';  -- STEVE KIM
UPDATE results SET candidate_id = 'af6172f4be5c8ffb' WHERE candidate_id = '7a7c3d4213bf733c';  -- SUE REZIN
UPDATE results SET candidate_id = 'dcc19378a7a6e6c4' WHERE candidate_id = '08d1e34361f70395';  -- SUSAN L. HATHAWAY-ALTMAN
UPDATE results SET candidate_id = '7004daf08120a140' WHERE candidate_id = 'cf567c73e696926b';  -- SUSANA A. MENDOZA
UPDATE results SET candidate_id = '7004daf08120a140' WHERE candidate_id = '9fed434e0a72902f';  -- SUSANA A. MENDOZA
UPDATE results SET candidate_id = '391bd319890d3eb8' WHERE candidate_id = 'a26df22d00ec753c';  -- SUZANNE "SUZY" GLOWIAK HILTON
UPDATE results SET candidate_id = 'dc7950e6259aba84' WHERE candidate_id = 'f90176dcf016186f';  -- Sabrina Fisher
UPDATE results SET candidate_id = '3ed0fa5b15cd2d67' WHERE candidate_id = '4b76375147ce0cee';  -- Sally Tomlinson
UPDATE results SET candidate_id = '4b6bdcbcf55d0355' WHERE candidate_id = 'be803ae5d88ba2a8';  -- Sam A. Brown
UPDATE results SET candidate_id = '13d7ae229b49bc3c' WHERE candidate_id = '5a29b3bde15e10d6';  -- Sam Polan

-- Batch 6
UPDATE results SET candidate_id = '047fae14d6d718c0' WHERE candidate_id = 'bf3c1d013ab95f77';  -- Sandra Alexander
UPDATE results SET candidate_id = '3d9478a7774f999e' WHERE candidate_id = '21b53fe6da1e4e9b';  -- Sandra Ficke-Bradford
UPDATE results SET candidate_id = '2c2d393f40fd58e1' WHERE candidate_id = '32719ed183fe3e10';  -- Sandra Joyce
UPDATE results SET candidate_id = '0a57a5951ba3c123' WHERE candidate_id = '6c57f9e917cdb296';  -- Sandra Morgan
UPDATE results SET candidate_id = '29a13eda6d0de818' WHERE candidate_id = 'ccfe1aa7f700853c';  -- Sandra Tomschin
UPDATE results SET candidate_id = '1ad7cbb93bc02727' WHERE candidate_id = '8bd9eb062edeff6a';  -- Sandy Hart
UPDATE results SET candidate_id = '119c9113ba93de51' WHERE candidate_id = '3eadf848ee70c3c5';  -- Sandy Szczygiel
UPDATE results SET candidate_id = '2885aef93c749542' WHERE candidate_id = 'a8b83bba22adc585';  -- Sarah Kaliski-Roll
UPDATE results SET candidate_id = '383470ff64af1423' WHERE candidate_id = 'b7971d473a1e4b27';  -- Scott Bagnall
UPDATE results SET candidate_id = '05c665740b8824e1' WHERE candidate_id = '08221436b87562d1';  -- Scott Jacobson
UPDATE results SET candidate_id = 'dc5d846ed957ac7b' WHERE candidate_id = 'f2d7d5a811245690';  -- Scott Lewis
UPDATE results SET candidate_id = '9655cdc1040354fb' WHERE candidate_id = 'c5d73f6c0e9a4c2f';  -- Scottie L. Hatten
UPDATE results SET candidate_id = '39c85ed2ea1a19a5' WHERE candidate_id = 'fc32d595feed829d';  -- Sergio Rodriguez
UPDATE results SET candidate_id = '39c85ed2ea1a19a5' WHERE candidate_id = 'e2c21a84b7a10b6b';  -- Sergio Rodriguez
UPDATE results SET candidate_id = '5f2675d144340ad2' WHERE candidate_id = '602c83735171d3a3';  -- Seth Alan Cohen
UPDATE results SET candidate_id = '432251b9e52ffbaf' WHERE candidate_id = 'b07b9858f51927a5';  -- Seth J. Schriftman
UPDATE results SET candidate_id = '081a06d9b5692190' WHERE candidate_id = '6c22b727deacc12c';  -- Shakundala "Sk" Narayan
UPDATE results SET candidate_id = '7df7354d3c0dad98' WHERE candidate_id = 'ba6623b6d06ce2c8';  -- Shaun Colin Murphy
UPDATE results SET candidate_id = 'c61bb28c02f5bc29' WHERE candidate_id = 'a9e50446bd5a8299';  -- Sheila P. Collier
UPDATE results SET candidate_id = '554834cf443be746' WHERE candidate_id = 'c44f2687f54d02fe';  -- Sheila Wachholder
UPDATE results SET candidate_id = '289c28bf5881acce' WHERE candidate_id = 'f43bce3e2e7d4bc1';  -- Sheila Yvonne Chalmers-Currin
UPDATE results SET candidate_id = '78f0ea9b5697ec1f' WHERE candidate_id = '8e48a934a6123066';  -- Sheri Lynn Gustafson
UPDATE results SET candidate_id = 'dbaeec66e584be33' WHERE candidate_id = '37333c81137da642';  -- Sheri Sauer
UPDATE results SET candidate_id = '37062773af366684' WHERE candidate_id = 'a58a30d49698119f';  -- Shiva Mohsenzadeh
UPDATE results SET candidate_id = '0d63de0b4889e99a' WHERE candidate_id = '94a429581b68f4d2';  -- Slagjana Aleksikj
UPDATE results SET candidate_id = '011376de78f3e62b' WHERE candidate_id = '8fbbfc2707e4fd5c';  -- Sonia Jenkins
UPDATE results SET candidate_id = '0ea92f2e037ae16a' WHERE candidate_id = '63a4c6fdce0ff5d9';  -- Sonja Jones-Wilson
UPDATE results SET candidate_id = '1aa29ee97ad36905' WHERE candidate_id = '61b60bb6f9af49ef';  -- Sonya Irene Williams
UPDATE results SET candidate_id = '359de7e9feed328c' WHERE candidate_id = 'ab374891334fad61';  -- Sophia Collins
UPDATE results SET candidate_id = '349930fda4c9d3d4' WHERE candidate_id = '4ecc4609dec3655a';  -- Stacey Sunderland
UPDATE results SET candidate_id = '81aff30837153f76' WHERE candidate_id = 'dcdd4b3aaffc2e02';  -- Stefan Mozer
UPDATE results SET candidate_id = '3a7549dbd2eece0b' WHERE candidate_id = 'cbde4efa97645a0a';  -- Stephanie Basanez Gunn
UPDATE results SET candidate_id = 'f4dfaf2756be808a' WHERE candidate_id = 'bdfef774d6f7c103';  -- Stephanie Brand
UPDATE results SET candidate_id = '63363320c9f66c71' WHERE candidate_id = '756ce68fc3e0a74e';  -- Stephen Baker
UPDATE results SET candidate_id = 'e5c1c24805e6f1aa' WHERE candidate_id = 'ff2b24dcfe4dcbd6';  -- Stephen Cummins
UPDATE results SET candidate_id = '124f66caed6f4ffb' WHERE candidate_id = 'beb6a7b05efc4130';  -- Steve Drew
UPDATE results SET candidate_id = '8e3bdc612ccb7dee' WHERE candidate_id = 'c7c749986677c0ce';  -- Steve Pesce
UPDATE results SET candidate_id = 'd05411f3e7886e1d' WHERE candidate_id = 'e8e78b7f2a9b5aa1';  -- Steve Wang
UPDATE results SET candidate_id = 'd05411f3e7886e1d' WHERE candidate_id = '6c217ec9ed2a4107';  -- Steve Wang
UPDATE results SET candidate_id = '110a0eac6eb68ad1' WHERE candidate_id = 'f945e43c65e70eba';  -- Steven G. Thomas
UPDATE results SET candidate_id = '16a8e122329badc8' WHERE candidate_id = 'f578eec871fb1244';  -- Steven J. Zawaski
UPDATE results SET candidate_id = '6dd238fb094752f5' WHERE candidate_id = 'e4878d543222c73b';  -- Steven P. Carr
UPDATE results SET candidate_id = 'bb602e10d54ef903' WHERE candidate_id = '189a9d62bff62216';  -- Steven Richmond
UPDATE results SET candidate_id = '0f9a794142cedfe2' WHERE candidate_id = '51ad0ced822484f9';  -- Sue Stein
UPDATE results SET candidate_id = '002aba80a7538693' WHERE candidate_id = 'd6d4f7136f8af1f0';  -- Susan Schaus
UPDATE results SET candidate_id = 'd71f3261f1ef2bd9' WHERE candidate_id = 'a08bb9d8316f0a40';  -- Susan Stein
UPDATE results SET candidate_id = '019f5867fac3b0b3' WHERE candidate_id = 'c61340d1adb13287';  -- Suzan Atallah
UPDATE results SET candidate_id = '755d56dc38cc4584' WHERE candidate_id = 'ee81f1d584e1da31';  -- Synathia Harris
UPDATE results SET candidate_id = 'b1945331120a298a' WHERE candidate_id = '78dadda184d4afc9';  -- TAMMY DUCKWORTH
UPDATE results SET candidate_id = 'ba38b2359ba64917' WHERE candidate_id = '4ad01f604f4528ad';  -- TERRA COSTA HOWARD
UPDATE results SET candidate_id = 'ba38b2359ba64917' WHERE candidate_id = '918e2c8f2602f0c8';  -- TERRA COSTA HOWARD
UPDATE results SET candidate_id = 'ba38b2359ba64917' WHERE candidate_id = '586f2ea0a1685279';  -- TERRA COSTA HOWARD
UPDATE results SET candidate_id = '7f6c8567f5034f0b' WHERE candidate_id = 'c4ae4c6972eead5f';  -- TERRELL BARNES
UPDATE results SET candidate_id = '79d60c5e9320f8d6' WHERE candidate_id = 'f8e42901ad4821a4';  -- THOMAS G. DeVORE
UPDATE results SET candidate_id = '55cb827f42774879' WHERE candidate_id = 'dc9fa8a7c3b855b2';  -- TIMMY KNUDSEN
UPDATE results SET candidate_id = '56e7e9a239e6b982' WHERE candidate_id = 'ee0c1060ccda81d4';  -- TIO HARDIMAN
UPDATE results SET candidate_id = 'bcb2aa8ed2fc2762' WHERE candidate_id = '805e84e5feed48a6';  -- TOM DEMMER
UPDATE results SET candidate_id = '3b3d23ea5baa37d6' WHERE candidate_id = '334b238af10f1706';  -- TOM WEBER
UPDATE results SET candidate_id = 'b6d256950d9322ff' WHERE candidate_id = 'b796b83c1dbaeb90';  -- Tabatha C. Sutera
UPDATE results SET candidate_id = '32dec7432db14534' WHERE candidate_id = '7bc4966e0c6217a7';  -- Taneshia Armstrong
UPDATE results SET candidate_id = '08b388f31ee41dd4' WHERE candidate_id = '5226229b2339304e';  -- Tanya T. Butler
UPDATE results SET candidate_id = '31ec43e1b07ab8cb' WHERE candidate_id = '5c1580d83513470b';  -- Tarryne Marchione
UPDATE results SET candidate_id = '9cffd3faa2b01eef' WHERE candidate_id = 'ed4829a43d33fa0b';  -- Tasneem Abuzir
UPDATE results SET candidate_id = '793c5efcf9fac20f' WHERE candidate_id = 'b3fef1132d7517e0';  -- Taylor Burmeister
UPDATE results SET candidate_id = '1b382a8257d691d9' WHERE candidate_id = 'a6e6263960c62657';  -- Taylor Cottam
UPDATE results SET candidate_id = 'ba33d919cc89b837' WHERE candidate_id = 'd3847065c974328c';  -- Tedd Muersch Jr.
UPDATE results SET candidate_id = '53e5361725e95507' WHERE candidate_id = '671d95859dfa6ec8';  -- Teresa Cameron
UPDATE results SET candidate_id = '81a7af8cfe159eff' WHERE candidate_id = 'ed89174684b2b237';  -- Teresa Jemine
UPDATE results SET candidate_id = '1a1b4d5c2a5659ba' WHERE candidate_id = 'eb3b88dbe19099b5';  -- Terry L. Matthews
UPDATE results SET candidate_id = '5a0e82aeb5a1962e' WHERE candidate_id = 'd9df216b8eba8fe0';  -- Terry R. Wells
UPDATE results SET candidate_id = '0707f2ded0f9fdbf' WHERE candidate_id = '5a4270df61031196';  -- Thaddeus Jones
UPDATE results SET candidate_id = '029572b88c1a24de' WHERE candidate_id = 'f4cc3803807c97d4';  -- Theaplise "Theo" Brooks
UPDATE results SET candidate_id = '989d055785009950' WHERE candidate_id = 'd691f06be1d52c8f';  -- Theresa M. Settles
UPDATE results SET candidate_id = '1210e29283cae14b' WHERE candidate_id = 'c1bf053c824d542b';  -- Thomas A. Brown
UPDATE results SET candidate_id = 'd0e8017b12adbf07' WHERE candidate_id = 'ec6992376aee423c';  -- Thomas F. Kosowski
UPDATE results SET candidate_id = 'b9778c88bf949051' WHERE candidate_id = 'b83dc9a3fbd33a0d';  -- Thomas J. Mitoraj
UPDATE results SET candidate_id = '0eb3c11b4364c63a' WHERE candidate_id = '5f137605c909db82';  -- Thomas M. Perrin
UPDATE results SET candidate_id = '62e90e056b0e519e' WHERE candidate_id = '69a62ae2c678423e';  -- Thomas Maillard
UPDATE results SET candidate_id = '5f7d3d5f89c931fb' WHERE candidate_id = '9f7b055ccf00a8dd';  -- Thomas Martelli
UPDATE results SET candidate_id = '1e218b03d710ab3d' WHERE candidate_id = '6268b260ef9d0b5f';  -- Thomas W. Strauss
UPDATE results SET candidate_id = '5e92fe2bb7b345d4' WHERE candidate_id = 'd4524e0cb8db6949';  -- Timothy E. Gillian
UPDATE results SET candidate_id = '49bbb3f440ac160d' WHERE candidate_id = 'df11dcd8e58a37cb';  -- Timothy J. Doron
UPDATE results SET candidate_id = '39d8fa54c65a3c1a' WHERE candidate_id = '4ec0a8849e2ee6b2';  -- Timothy Jones
UPDATE results SET candidate_id = '0a670ac3b0a350b3' WHERE candidate_id = '951a59d69b21ca5e';  -- Todd Sholeen
UPDATE results SET candidate_id = '4ad253cb3a705acb' WHERE candidate_id = '8adf2aafaa69487d';  -- Toleda Hart
UPDATE results SET candidate_id = '84f051297ef3e6a0' WHERE candidate_id = 'c76dafddc2117fd8';  -- Tom Arra
UPDATE results SET candidate_id = 'aeacf3da01d70b67' WHERE candidate_id = '7a29fda288be9cfe';  -- Tom Chavez
UPDATE results SET candidate_id = '984ae9e708748404' WHERE candidate_id = '9f0280550ad726bf';  -- Tom Olson
UPDATE results SET candidate_id = 'b2c13b8d61852f81' WHERE candidate_id = '60a1062dc94d2ab4';  -- Tom Weber
UPDATE results SET candidate_id = '7d0f1debf52679da' WHERE candidate_id = 'c1aa40eda0978d26';  -- Tommy Hanson
UPDATE results SET candidate_id = 'd1230c70e455f92c' WHERE candidate_id = 'da238b54fd9ac5cb';  -- Tony Ciganek
UPDATE results SET candidate_id = '7a6c79f65e553a3b' WHERE candidate_id = '8dfbe2d260496889';  -- Tony Serratore
UPDATE results SET candidate_id = '1c53933526009f5d' WHERE candidate_id = 'e74b2d950b376ef2';  -- Tonya L. Reed
UPDATE results SET candidate_id = '4559eb6499ea272a' WHERE candidate_id = 'bc6c3fe52bcc7d1e';  -- Tori Garron
UPDATE results SET candidate_id = '50288a286052ae3c' WHERE candidate_id = 'd28851ad8d546350';  -- Tracy H. Bragg
UPDATE results SET candidate_id = '00aaaa631164f52c' WHERE candidate_id = '424beef7c31baa72';  -- Tracy Jennings
UPDATE results SET candidate_id = '234140f0d85c7f96' WHERE candidate_id = 'cbc0d75d0f02db49';  -- Tracy Katz Muhl
UPDATE results SET candidate_id = '234140f0d85c7f96' WHERE candidate_id = 'cb7934c15e1caffa';  -- Tracy Katz Muhl
UPDATE results SET candidate_id = '261368457fd15489' WHERE candidate_id = 'd90df7dd19ea801e';  -- Tracy Thurmond-Bosco
UPDATE results SET candidate_id = '5ea902ca4de1d852' WHERE candidate_id = '9e0779ee5b4f0d05';  -- Travis A Claybrooks
UPDATE results SET candidate_id = '46981b61812a29a1' WHERE candidate_id = '5d5df193a848623c';  -- Tyrone K. Hutson
UPDATE results SET candidate_id = '24d5be034b01ce6f' WHERE candidate_id = '7e804668a7bb9d30';  -- Under Votes
UPDATE results SET candidate_id = '24d5be034b01ce6f' WHERE candidate_id = '41842c9526735857';  -- Under Votes
UPDATE results SET candidate_id = '24d5be034b01ce6f' WHERE candidate_id = '6123e6d9f5918c82';  -- Under Votes
UPDATE results SET candidate_id = '24d5be034b01ce6f' WHERE candidate_id = '060713dc080db45d';  -- Under Votes
UPDATE results SET candidate_id = '24d5be034b01ce6f' WHERE candidate_id = '8cf36edf7572eb9a';  -- Under Votes
UPDATE results SET candidate_id = '24d5be034b01ce6f' WHERE candidate_id = 'c466e36ca447f6ce';  -- Under Votes
UPDATE results SET candidate_id = 'f1c46fa9d83c22b0' WHERE candidate_id = '06455d706b9c196c';  -- VALERIE RAMIREZ MUKHERJEE
UPDATE results SET candidate_id = 'ce6600a3e2985a8c' WHERE candidate_id = '1da340a6250bad01';  -- VICTOR SWANSON
UPDATE results SET candidate_id = '838123a6a3b7317c' WHERE candidate_id = '37d453608e67592b';  -- VICTORIA ONORATO
UPDATE results SET candidate_id = 'c720c91fe3417c1b' WHERE candidate_id = 'ca816cdcc6336f79';  -- Vance D. Wyatt
UPDATE results SET candidate_id = 'd4e0a76b46fcfef5' WHERE candidate_id = 'e8bd839bccac2615';  -- Venus Hurd Johnson
UPDATE results SET candidate_id = '2955870d6d0d5938' WHERE candidate_id = '5849fd9f0eb55979';  -- Vernard L. Alsberry, Jr.
UPDATE results SET candidate_id = '26540d7039730f13' WHERE candidate_id = '6b2e3a8ec8392dbd';  -- Vicki Baba
UPDATE results SET candidate_id = '73a9f6817deef7fc' WHERE candidate_id = 'd00fd9b92771438c';  -- Vickie L. Perkins
UPDATE results SET candidate_id = '94486f5094a487d0' WHERE candidate_id = 'a2d770107cd3f8c8';  -- Victor E. Blackwell
UPDATE results SET candidate_id = '46702132615a4980' WHERE candidate_id = 'ed58a65b73f89c8d';  -- Victoria Wolfinger
UPDATE results SET candidate_id = 'c272c74d109e82f8' WHERE candidate_id = 'ab29395529ce9611';  -- Victoria Zimmerman
UPDATE results SET candidate_id = 'c32e03eddbcc5310' WHERE candidate_id = 'e8ce257a057fd4be';  -- Vincent A. Pace
UPDATE results SET candidate_id = '49d74f4ba6bf3267' WHERE candidate_id = '654c34c5441fe1db';  -- Vincent E. Lockett
UPDATE results SET candidate_id = '2c6c3b277e03c791' WHERE candidate_id = '608768ec4fac4a56';  -- Vincent S. Fiorito
UPDATE results SET candidate_id = '5c154d610fc80857' WHERE candidate_id = '055bbfe4b1a4777e';  -- Virginia Brown
UPDATE results SET candidate_id = '942eae295043b1ea' WHERE candidate_id = '05f9b26bd5ce360b';  -- WILLIE L. WILSON
UPDATE results SET candidate_id = '942eae295043b1ea' WHERE candidate_id = '3cfe7c3f216e4f55';  -- WILLIE L. WILSON
UPDATE results SET candidate_id = '276205e29a955d58' WHERE candidate_id = 'cad12817f28c89ab';  -- Walt Mundt
UPDATE results SET candidate_id = 'a1e958be2a98b885' WHERE candidate_id = 'ab523fc247cdc95d';  -- Wendy Lux
UPDATE results SET candidate_id = '0e6c7e9d239a40d8' WHERE candidate_id = 'd586347a5c9c6950';  -- Wendy S. Meister
UPDATE results SET candidate_id = 'e133f95ac1034da1' WHERE candidate_id = '8ca0a2cb2913a1f8';  -- William Betz
UPDATE results SET candidate_id = '09aed3cb2e7a6032' WHERE candidate_id = 'b9c99bdd8dfc4d50';  -- William C. Love
UPDATE results SET candidate_id = '2f169eb31758e7e7' WHERE candidate_id = '3ff5f011bf94db49';  -- William D. McLeod
UPDATE results SET candidate_id = '350febae4586278a' WHERE candidate_id = '507e361985de99af';  -- William F. Kelley
UPDATE results SET candidate_id = '7ac2c767c5a7490b' WHERE candidate_id = 'ac22aa497a84c693';  -- William J. Pohlman
UPDATE results SET candidate_id = 'd40aba2202d2117f' WHERE candidate_id = '2c1c79ab58415d59';  -- William M. Griffin
UPDATE results SET candidate_id = '43172528f85cd158' WHERE candidate_id = 'a2a0a6244c2a5255';  -- Willie A. Jones
UPDATE results SET candidate_id = '4d5d6bfc1ac07e07' WHERE candidate_id = '2efba6c05182256e';  -- Write-in
UPDATE results SET candidate_id = '4d5d6bfc1ac07e07' WHERE candidate_id = 'ca4041362e0dff00';  -- Write-in
UPDATE results SET candidate_id = '4d5d6bfc1ac07e07' WHERE candidate_id = 'a0a151739cf224bd';  -- Write-in
UPDATE results SET candidate_id = '1f6b3228057681f8' WHERE candidate_id = 'a6105c0a611b41b0';  -- YES
UPDATE results SET candidate_id = '1f6b3228057681f8' WHERE candidate_id = '5f2c77e32ac41558';  -- YES
UPDATE results SET candidate_id = '1eb3f6e7ab720475' WHERE candidate_id = '4c6b890f9f4d3d43';  -- Yasmeen Bankole
UPDATE results SET candidate_id = 'e5a64d34176afef1' WHERE candidate_id = 'f837c2e1c108ad43';  -- Yesenia Lopez
UPDATE results SET candidate_id = '59e306dcfac4e0cc' WHERE candidate_id = 'ba631621274bd9fe';  -- Yolanda Bindert
UPDATE results SET candidate_id = '1c3acab904a0f79d' WHERE candidate_id = '7332e236ff05c8cf';  -- Yolanda Williams Corner
UPDATE results SET candidate_id = '0540608a63e65c55' WHERE candidate_id = '08344a4929a03420';  -- Yumeka Brown


-- ============================================================
-- STEP 2: Delete duplicate candidate entries
-- ============================================================

DELETE FROM candidates
WHERE id IN ('8375bbeb0a05dbb6', '6632397dde7c74af', 'fefd22a72d7a06e0', 'eed3dd18560030b4', '19690f9a8d0d184b', '805f450890f6d02c', '23ed927c3f34dde6', 'b495280186a53879', 'dea08a5752eed647', '1bd6b369caad06c2', '5c1fe4a8aca59202', 'ebcdfb34a748553e', '5ab0f84f3e515e6c', '319285a0366cf8dd', '4020edae195d061a', '515c736b21f6c7df', 'b48d862acb1afbdd', 'e27e613bfe2e5116', '939d1044a52bfb1d', 'ef8701af2dd97747', 'ccbe364db2836b0a', 'befb522afb177258', '7c919e13b494f99c', 'd4b0a9342ac26058', '67fafe2d93e2adb0', '9f8fea4b0bec32d6', '73f225f27a3fdff2', 'd281566113b4e34e', '2df4f47471ec0cbc', '464d8aaa6df5cb28', '2a5bea2dda736944', '3a08e45dead6a70e', '1361f3a045f1edab', '85d8844f2e7481a8', '6dc1e3651a0209fc', 'a8e9a6f3cbc3b536', '0cc8f5cb3302e1b2', '78dd885c0b5a7199', '203069e9149c7044', '4bb49a313253cdf8', '3b7f28475c2e74fb', '53eb71eae9e1faa9', 'db63376dbf0b9cde', 'c0993c4de1f25392', 'e4bf5abe6e660239', 'fa0a580713c8c732', '56ad77decf9eb52b', '218990c14e07cc9c', 'b9ef7c8e96e56a1b', 'eb59e36c8d49f847', 'fa52c53d2a3e53f7', '9f5bdc161e4cbff0', 'c711e72d03b1c494', '987afc24f3cc3175', 'db7e0f99d51e6d62', '30aaa6e3e115b978', 'd6db51d3ea527638', 'f2322f43e360cd81', '58c43369646b312f', 'c2aef63330c4996f', '22c67cfe82044eff', '06d2a72fe6f568cd', '5c63f659ec8b90e5', 'b0079320ae4e49d2', '136126122543127e', 'b37ed5eaf6819404', 'eb4a26c87c35b1d7', '007a7a5bd7a8f06f', 'ea4bea8445839f70', '7bb485375e4d8ca8', '6691be728692627f', 'fb812df2da6558e1', '7a4b0a1d7706634d', '66a0f0c92659bd49', 'a5be4df7cab51e76', 'e8f76171cb833233', 'cd6b5a0365736ef0', 'a6320160d45b2096', '5e1210c120f1661b', '1c6a1ba179baec30', 'f296bdb4ea9b4a60', 'e66e4f7cb7cada8b', '063745d2ed6266e2', 'e929b8331c2cfb09', 'e4d22bf6a35355e4', 'ffe5ba9238bf7214', '8e4464606820a1bb', 'ba2822fea64aa103', '5eebc37de3fac118', '7a2eac69435b2c3d', '877b322cf3303379', '9495152f67f46786', 'f57ab3694a8b66a1', '8a31544b73a2086c', '8756fd4aa2b398ff', '8deb6bece5a079b6', '65f0711884a89ea8', 'e324bea054cb3ea5', '088a1cc7488a5349', '9f99b37adc218271', '8019b839b36aaf6d', '7c07936b3ab22863', 'f3d76dd4bae433a0', '0b0e460d2c3840a1', '1939a3ea4c34f376', 'b7eaa5dc9c06b863', '5a3d9442af3638c9', 'a725ba2529d24124', 'b81bad94896391dd', '66e6c7e3142e5937', '51fe34afd9fa21de', '43f0184d48719794', '1d696e663ea55758', '1ec3c77584d5e1e7', '86bb4e88c3fed409', '3c304515e0968f9d', '568b3e6c8ea2b7dc', 'c3a5628dac7de2c4', '4da69bda6645929d', '1840fde0765a90bc', '0c3ddc7c7420f9da', '2dee6c2aa455d698', '7aa66e403249faea', 'b5c5ae02b8887701', 'c4cf798dfa9a5384', 'cc17644f269a9235', 'c58a741b53e86695', '8bc4a4ba1dcc8217', '48e968e24bbdf16b', 'b7245f4670896b0a', '9713db292ca05ddc', 'd7101a44f8f60cf5', '026e25baded40b9d', 'a69968d49305960f', '38b1a4bcde4509eb', '6bf4499242c27f69', 'd59b0f19a7a24299', 'ff25f9a7cd20998c', '63758be9cbdc1faa', '64a50954e70463cf', '222fa2c836cad0b9', 'a06d566d28ccdced', '782526a1f0fb225a', '3047504ac2f22954', 'a69ed56378942ebc', '2735c2014cd2539d', '63f82badea9a347b', 'f9182c847a6f4a39', 'de418207a2d3c30a', 'bd336c3e95dd5c4b', 'a02fcf7204599d3e', 'cd058f08ab4a4fa2', 'acea0734e7c2422f', 'bd776e969ec03cb1', 'beacbcb67debdcc4', 'dd58a8a4ff9f6879', 'd83c65e81ddf7c30', '29fc6b73c493e7a0', '3ec4740463ae5590', '3dbe2110cd78e01a', '97a18d4b61dd43ed', '6a8d1948ae32c238', 'bf9c26483829c161', 'e89db606c73cc2cc', 'f7895840cd02d733', '24887b7ac7bfd581', 'a027330d9db55b2c', '3a6bd80cd2694329', 'd21af8009faf6f69', '6a7d67c466b8fcf7', '5cbb6a306cc374ca', '8d9722a83f9383d9', '6f8cf349e93056a2', '4918874179496631', '08c1fc12a6d8c369', 'c85523aa6a8a08de', 'b65ef00df33e575f', '4a1ebc828aad2dae', 'a4704649cc4f9dda', 'e3962498c3b17301', '2ea5af39b00aa82b', 'f4fc5405ce9918ec', 'a0c1c20a6af37c75', 'ef0d4986cb191955', 'a1cf26832181776f', '1926f7e672359eeb', '97a98a35c6176493', '8bfd3179bb9a238e', '3eb61cf9ce675569', 'dfab544d1d9d910d', '38c2231bd0f8354f', 'c40c6607f35f059d', '20380d6348b53497', '85619bc0bbfd1c49', '533ce9aa95ce1b49', '7249fa56270f4d04', '68a4a9b2ad64dcc6', 'e171e79d30d41087', 'c80b7675e3a210ce', '51cd5534cfebafbf', '68205bf900648cee', 'c82b0329de229818', '87ed6bc7560e3885', 'db96d5965695b9e5', 'cb79b4d4c93e75c7', '361573578d36eacc', 'c8e7e4f94a2c7998', '2e00aef6f527f01e', 'e6a2e92d6793433e', '025be568b74aec28', '0e32e61322c95419', 'bffa8ad6b1b7d03c', 'a5ac6eb047aa8210', '3e53d4dd85876254', '1d63bb0b1b696aae', 'a351c5078fb72568', '82eb97ff09763c16', 'fe8cc274072737b1', 'e3f839dec081955b', 'db2f89772d82ae5f', 'fd2cac23e1efa645', '9323675682f236a4', '96ec1adb13420a85', '97ef77920f02e9d5', '900e93b2b251a4d8', '0506d574e0237e57', 'c742a966ef267127', 'db46fb4da5ff9a0b', '5271d4f0f8ec8630', 'c686f7754c51d7b6', '5784b31eba5f261e', 'cd10a9c2efd6d20f', '1c635e27f8a10980', '60e805907d0fb419', '571affa11e4059a5', 'e0092b98f9daf0f6', 'ff248139a6363e14', '84862f7e20529ee2', '3a073c4d58d1aade', '402c206684e8bd4a', '69e1e35565969dfb', 'c26951d2f2c55def', 'bf1e67a8c123b90f', 'cf832d2cee2056fb', '7ba7f5961d7d5fc3', '52fb79cfa1e1d276', '3e0ac85cc5f2c686', 'c15381e23e3e4965', 'f752440d7e903842', 'b162a98d309e78ba', '4a17f73ba4db7a6d', 'a0911251f0f50a89', 'f9802b0684707fe6', 'c610b54a7e12ecca', 'acb954bca8092682', '5160b58bf3853ad0', '29cae8f3475d8654', '507995dc973f9763', '5af1810b433631b2', '094ee42eb0932fe5', 'bcbbaf7bb0ba465a', 'e2e45edc22cb6797', 'fec06dbd13c9f991', 'b642246b253456f4', 'b4e4ee014606edc3', '0b0784a1ca81981e', '514b6954420810ad', '48c8ae0f0f00f0c0', '5a42940570766261', '92ba1b0357f769e8', '44fa9b0414fd6df1', '0652ac402fe6bef9', '73c3ee6047553ce3', '2b5b02f7c70ce11e', '19e5ce2122a40121', '632dfa8495b10781', 'ed11e040953a69e7', 'f691b55e9b01ab28', 'af463c52fa231f1e', 'e95d6f9a260b0db4', 'c5c1b4b1bb4caf45', 'e80dbac4ba49b2d0', '6d24b20cd0b253b2', '9fc73eb86a9897f4', 'd2ed71bcb167a6df', 'd96b48df5d044492', '7356cc46837f7617', '8b9199cfaca640cc', 'c2fdbd752a6d7051', 'c457a5714e1df310', '03124460e1cec7ac', 'b28f3c5edd753f9a', '9753f55e22f94656', '7ec6021aa453e1a3', '21fb80032a4f03b9', '7fbb42408373b18f', 'afacc2d3967552e9', '3778d1fa4032eda1', '1ace4f8cf54e00d9', '8c37c8380ffcc9f1', '690cfd1e369cceb3', '965a6dd16f3eecce', 'd365e9882160df8b', '5500986a7fc5b451', '8514450661165223', '134da44ee72fda73', 'bd7caabb49933c85', '8fc39739b28c2172', 'cd9089b345291f92', '9bd7fef52d5d129f', '18ec5be4e4bcf618', '00e20996aae45c91', 'aa1f9d252ca5871f', 'fad83157c5fd7352', 'a14a024ecf4300e9', '75fe44dea8da3fc1', 'a6f9037de8b4d712', 'c05777f9fde12c68', '6db3627091d59802', 'b5c13bbccc4e6a36', '92796b4663a3b61f', '83cb7d5e67430745', '3660e4ccb331119f', '7f873f01b8662a9a', 'be4030cb3d0cd193', 'b9b50f1f0fec6059', '76652bcda78c3f5b', '5ddc6aa5ad54150b', 'b2020114069e47ad', '40dba4c75b9765c0', '26f9a8600a2a3261', 'c9ed509e81732b69', 'a6e3ea4f6c8332d8', '05f4446632afbc47', '806a4cb402545909', '68d630955be5a5e0', 'eb4c396c0cc3fd03', 'c09f2d54c9b15694', 'ff6cbb240ac58f8b', 'ec3d73d1da2347f9', 'fe894ed89d359cc6', 'e3af22e47f77c60c', 'b0388f02bbeb2d38', 'e68daa4c24bd010c', 'a61f904ed74beb95', 'c7900dfd41b48e19', 'e31bdb7d6bc859fd', 'e87cc81709fc9d00', '6044d693840df3f6', 'a74d695795def0ab', '8ee8ecacf736741f', 'd6ba355e5f40022c', '90b5bf2e48604764', '8ab810e593b9ec1d', '18c2536a03e3aafb', '47c6d8df739a9b04', '5c136a8fa22cc463', '29cf6b98372b5e94', 'accdf3712919383e', 'c2b1ea729b6848af', '6004ce12c702843a', '010f4db06f127669', '2685835abd49ad63', '95879eb2111b7e07', '8ed93aab79a334fd', '9ec9bcd610ad9d0a', '3ad10dd7890bb307', '1989ceb490e9f5e4', 'e4e37da75bbe0a70', '67e7b185f907041d', '1b800b5a34f0d814', 'b6c6f941419ee6c4', '2fe45386e362d364', '785b604c75c2ba40', '3affea2f2d1dfda7', '20738d04f2d539ad', '82320cf7ae7c67e4', 'faf4553483584a8c', '0cceb4767ecebfc9', 'b27569553908f1b5', '22d6248f4de07204', '97d973df25b74135', '4d70506793a13422', '85e20bcd0552f72d', '2086585bfab85dba', '2258fc5748f9028b', 'd2f02ee4dda79207', '40e1775445b52650', '716b1c9181c4ce0f', '0d93c8f845b93733', 'f78b158f802c0eb2', 'c6e41f05eed9cb47', '9ceee80bcb9e8498', '1ae1d015b38a2e1b', 'bbea4692ac7bf92a', '2051726decd52de5', '1ca6ea7e0bbab706', '4e5bef5e6626beec', '1e9f08106ba208d6', '446feb98014a3879', '2ad7b537c3357bb8', '22b6909ee0109111', '1f608c55cbdf0a8a', '72abe2ad7ba1a770', 'e9abd0133d0c1597', 'c096eaa83bb104ad', 'f7e8ed05140279b3', 'adfd70fad361106a', 'a0afe5728a66e765', '1ea5c764f3b29ab4', '1b0735433ee40b7e', 'c2cde85359c9575c', 'd6d0f1905e0f9c47', 'ee6401918460a03c', '68daf046a030c8f2', 'd9a27fac7cb4aa7a', '439c974d981a04bc', '222aa02dc9274ea7', 'ddc491fac0ff52ac', '0c8673ea4a2a5aff', 'd50aa568b35c5d5a', 'c42b131307c9d0f8', '7b470bcd420175dc', '1b1c9867a929dcb0', 'edacdbd7da70d3e9', 'f6b62c747e33b165', 'e0a618346b4358f0', 'c3599a6ce8000cfe', 'f311fc92a30888f0', '20d262d82f968615', 'ec879f373214bbd4', '7bd5a00d33edc514', '9f91714665b45edf', '9e17adc8dcb08591', '659769838d407194', '2dde94349c942b46', 'f3d23c46fcd47e8f', 'ce4289e4e7966768', 'db150467625ed563', 'e70cc34ae436e126', '8b2aa7b74f1d2402', '56f46de6aa0dcde4', 'f1a3f353d800e486', 'f1d7bcf1ae3e3a3e', '2bc8196882a9197c', '40706b11e59dc5af', '11de3b3aab8a407c', 'f0449d389b2acabd', '40db257b0d35f8f0', '32122b9b382a70b5', '4422d4d3a6b5d3e3', '4b50016ba4c122bf', 'efb2963858700ad9', '3c1066dd68c06bb6', 'fb471c53a4fb83b0', 'f11e612ab48ef39d', '5f3ee8193157f891', '5e540e38461088d4', 'dbf9856cfcce0b81', '700da8bb10cd3ab5', 'c86526292f6253c2', '73ddf2018c4a8ea3', '5208b4ee4de196f2', 'e6d4d6c9cc15c410', 'e554d9e829a3f9af', '642c92b016c24925', '0514c44934f517b3', '2cbf914734de1694', '6458bb506e6eaf67', 'b5308b2a3f28d9f2', '123c2fe1363d01b7', 'e73008b4b7457d43', 'db5fec01ca59baa8', '9e64953162b51203', '58d76d0ee4d5f79e', '76faf9202bfbca87', 'ac0215092339c2a3', 'f79d355196eac269', '15b5479acab2d0da', 'cc2e84e2d4f14d98', '95087c42916f9d91', '33918c5a693b1e81', '9eb6f795921451ad', '3ee6ae04f2f257f3', 'a07faa5d84a09c63', '99de0a226c1b1c6d', 'f17e3104d87aa4dd', 'cc3ff252968bcd38', 'fd18911c5f39083b', 'f4a6a8276e845232', '87b806bc35016538', '408366fbe4f83f40', 'fbd5425acc4d726c', 'ac95f89aa20e04b4', '302a5e93e681769b', '84c4b7e966d5c9da', '0d4f5f38a18d799a', '90cc7c65bf39b7d1', '4bb0b581fa29e888', 'a00cc8409399c9e8', 'c119afc4d41354f4', '68fb69bf5d3562df', '4a30c10fdceb175a', 'd28cd393fab54c56', 'a842344266ac9ab3', '2cf7300a26257d94', 'd51d0c32500f6110', 'a407fabc752935a5', 'dce31a17ae59d2a1', 'd9f674601d60198f', '40993ae3b1aa9119', 'b72ce06c0e5e7e90', '4ed6d5890399cb91', 'a9fad5f834c42e7e', '0fdcabc8216e2b99', 'b156115ea18ee704', 'cb0c0c2daafd5482', '26e7094892efe6f4', '912d1625703017b1', '62becb6688a20ca6', '901dfbdffb50c683', 'f6e4e650bd051e4e', '9c9336fa84471de5', 'fe4c3f1ec3aca805', 'ebe4ab378b1d8a50', 'fc5a0fec0cfd9880', 'f7408bfac5c6e77a', '6cf4e4d1844d482a', 'ddda8bce11c69503', '100a77829759d6d7', '87d31d869bd3a04b', '56fe57963df75cc0', 'c262422363431997', '3c69941d7ef9ec6d', '13273d19ef6bc5f0', 'a11203ab673809a2', '0bd5135d2e5186dc', 'ab9677fec667fe93', 'ff27d65cd1048348', 'd8db2c714286765b', '79916c85803fef2c', 'ffac9b9f8802dfca', '13dc8b4a694ca4c6', '922ae7515dbcb1c5', '6a19aed58ff7ce4c', '9e9f14a4bc0909fe', '54b22479ac927f5c', 'e2739beb529d7e06', 'e059dc3b781d6137', '9a4a38d95c2b39d7', '9afd312ad9c85bef', 'f428a246fe0e0da8', '4fd9c5cd08f58036', '5a966be22df3a264', '4599d11c06143116', '7fe8a58e3f4231c8', 'd1f5b28849e5acb3', 'fb5115e9c8c52a9d', '552a81f5986b0fb1', '9183dd052d9b3fa8', 'b93cd238c6c7c1fb', 'ac3b5c43ced50953', '5898ea370e257b68', '7b100f68e6cb7488', '6212db5bd69ca635', '39b3585c5686256d', '50bf4f388eea5f36', 'fdbd444de73d3349', 'f15b6c03da1e9e17', '7518ef7ae4e1fb3c', '7ec0cdbf8d6da6ab', '44f52ef275a1053a', 'db245344c95d5ae0', 'e4cecaef4959a714', '7263d213c976a729', '4b7e4a4a76e882c9', '70e738c48cfb1748', 'afe9e0275de66fc9', '445edce643cd3c23', 'e94187ce027c8261', 'dd29d173dc2201c3', '2ab5adf79cc8e7cd', 'a0b2c5cd2002d87b', '824484cb1dcf83ad', '77b3156d1c9fdea5', 'bd383fadccf9658c', '9a5309a4634c670b', '4c62bd96ca48eb51', 'c0436c07424176e6', '1a3b873bae6cb6c1', 'ffaf860eae892eb4', '2495f98f45c3cedc', 'b68df2e808f87e10', 'ceb9296b2bdf6f57', '55e87a398d4f982a', '5bf5a49f8e7a9553', 'd808fe8793ccdd60', 'b0c07e752481ca43', 'd1b21178d6de94f8', 'b544cd9abb946952', '231ea4ef77904b64', 'b5c3a70562b7c469', 'f383a1f43fd454e9', 'c8e232f969ab6f85', 'f5382fb5b668383c', '32acece05095065f', '738d37c368458429', '6d099f090931aad9', 'cc29793aa3081b32', 'f09ba7a7595ea5dd', 'b55afe7c1a2c4d52', '8ac47362032be782', 'ffc7a78f6d6ee408', '186e71a92d4ad42b', '2dea491a986b652f', '012180d4be3989bd', 'a06c368cebf50a9f', '9db1242d69642bc3', '9e90bfaf927d14a9', '0a7f5f87682db04c', 'b38e9fa24447d2bf', '272b47e5a512d73b', 'b818cffeb20901d6', 'ab49dc9ea8b923d8', '0568b582b35246b2', 'a88858241d414549', '767d0caaa70ccc1f', '0337093316df9532', '2901673496e9c8c0', '0a55e7cc7dd8eb42', '58b069f3bac8a7da', '113902d198997e90', 'eed4b1c851eb5480', '925e5cb3c24833a5', 'b3e9ae861bca95f9', '1796dcddfbfdaf5c', '2ac2cb8bbf211838', 'fa5a476bddb78b19', 'ddbae09596e06263', 'a096d463eb9e3af2', 'e9b13cd14ebb1019', 'b3f3377fc15ac958', 'bc870e4785b54ac6', 'cb1ba6111a342d9e', '3687e432e241de7c', 'afa284ccda905d14', 'ed6d9901ca39f389', '59e088fcd2ce52a9', 'a3566fc28b8efb90', '2249ae119e63b965', '3c5b1aadaba9f8e5', '821c617356b3133f', 'ea47c4a26605c17e', '51303c2ed7f33462', '57ca7e2b6780f41e', '277416f1bd076678', 'ecd0821cfdbc6d72', 'f12e397b10b87dc2', 'd0295e9dfa9e3a6e', 'c3c49e9dbdca6ab2', 'd83f6da31dea7e3b', '22d7978e0226402d', '73855dd5de234e42', 'e92eb0027d7e26bd', '59672c2436ed0ac9', 'b6c84144f43b1233', '8e256c71e2cd558a', '8a32bbc4eba81085', 'dc12278d416c6228', 'cecea551fe2486dd', 'df7514ee5ebbcd54', '5e425c6b46a8798b', 'e88af8fe9a210cbc', '99dda83f29ce048e', 'daa52610ea48f57d', '7df0eaa89198ec93', 'dbe693dc68174538', '1164c5376db8cdb2', '17fd403ef4efc5cd', '1b7c5a1095cfd12a', 'badcd070910c6122', 'a3e9af99453259e2', '611f75029853efdd', '1fe3a9a3bb72f704', '5f86735da7bb6857', '118cd4dc9a53acea', '6ecee49f10648057', '1afbd25114d694ba', '1e74eba6606333a0', 'e1858d811999223d', '406b133dc9a7eb60', '68cf4d386e79f16b', '06f7e1225e5d86ab', 'c117bb2bb46551ff', 'a77ff15712911e25', 'ce3b352587b4efe1', 'a6e439208139a917', '1243394deabe2c89', '3d107357f244d671', '3b2bb60f164de0bf', '3293378d4cd05f48', '3dc4235dabf43f2d', '66390e016a17b200', '3575b605885ac369', 'fa9b3127702bc3a8', '42417f83c4bbb1f7', '92938333a590c25f', '728fe1f56c8a57cb', '7c91577558673db0', '1ad154d100395897', '0373f0062c3fff78', '61902ef52f5656ad', 'bc400bc222c8771e', 'c15c0d4c077692d4', 'bc05f0d5f0fb8a47', 'b87df4bba2889541', '1a3e0afb23f82e72', '474eb235880018c2', 'd06c33acb50b43e7', 'd0cdc0323e787fb9', '16140d4303229613', 'ef668a13a1e4dcf2', 'ecc294ed59e1918b', '0252139ec205582f', '74bc4805b20d94fe', 'b51fb8734011a68b', '8f60a9d49ba3a1eb', 'f628a0027dbbe1c9', 'c66c56b457ba44b2', '91c81f74b5ee29cd', '27a9ba4cc121e458', 'a05ecf86d566d5b9', '5e48e5aab4b1c8e4', '75b359bf69e5ed08', '60d90d939e87729d', 'c38366c78df410f5', 'ece555c98dbf778f', 'bc675ac1079e58b8', '6eeb525cde70e16c', '2ef62d4660676093', '61c2421c1a695d06', '06155bcd1ff5eaf8', '3d684694936e6da1', 'f67d9b6f26b36d34', '717c75daff1078cb', '613f0aadaf8d4194', 'df9b7a285242b313', '4b5a5965d10809b2', '52623d1b14ae9c46', '725f6196837e018f', '5b95812e06eaf3c5', 'f7d6b5fde4804252', '90048b132ac649bf', '5df8829f886ef9d5', 'c316fd030aa8a05f', 'bf366b85d024233e', '70a364d1a4d6ec73', 'e18ef714434da411', '85d98a4e51fa7b76', 'b6f44669a45db08d', 'd67d5647f8516c97', 'ec0b522ad9ab6a06', 'e7ae1c2676b00639', 'e0db893314cdf943', 'f1a40dccd10785f6', 'dae3b0d680d6c240', '2905ea901dc12a21', 'c8bf8e7d3ed7c953', '2f9530f1a7c8c0b4', 'a79f7ae96109aad2', 'ee4451e0bde6b268', '53475bf822ddf19e', '60a526df3eb0475a', '64d4b38e40e90500', 'dda152e0a6f6a15f', 'c509fca1aea2aa80', '5b5f67bc6b0bb45b', '6c51cfdf76f9bfbc', '2bc71bb86079cb01', 'b12e8df26629f9c6', 'd2b52ae4af265aaa', 'cf33c643a328d15b', 'ce644e048319ae47', '8eaef4ddb19bc167', '498b20d6795bf5b8', 'b6bcab8c48e6b88d', '826b6004de1f042e', 'b559ac55f3e96357', '7ae5d9b17a36d56c', 'aa158da21dff2d48', '6be24abd68aeb270', '588d4762ed341bee', 'cd6433382d8dd4c8', 'aa34e28b21aa5fe0', '621bfade0bd9808c', 'aa2e5652c96cc791', 'f390699726a6f331', '528a99af6bdf461c', 'ea433e79bb840c5b', 'eecec4430b90162d', 'f8fa2b7ea8bbcb8a', '13faaebf23703204', '35b197a57943a3d1', 'f497dcff84602363', '66b9c9d917fe75d4', '6250c18198120fba', 'd93ed23a3f42b23a', 'b110781445c7fdbb', 'd40d4cf2f60b2f29', 'abc2d9e97dadb408', 'd422d17de014a8ae', 'ec59e187603ee6eb', '138608ded54daa28', '9243419686b4ac73', '43ded3789e35532d', 'f318fbc536dd71b8', 'd521b259db048861', '9d2e3b48dae37da0', '09230cc27a0538f4', 'b923cc6ec2df7e1d', 'bef449fead70d6ab', '413dcd863b9c4414', '7fa3b767c460b54a', 'ff8ab8cb370dac25', 'e60530c2a26b5bd6', 'ff10da12f3cf4143', '69a32cecf5fccdce', '704b59f3f60967f9', '63ee098041e65692', '6c54ff80627cd369', '42d4f172080e461e', 'c5e33dbaf41c2a44', 'c1eb9ba37741e5a9', 'd4dc757dd6592a4a', 'cbfc2d33f8438bff', 'f1a1d65cb9ec7ec3', '12914d834eeca0cd', 'dc5d68721279789b', '9d53ae705296a04c', 'bd5b182d6b6be8b9', '693e598672ad2bee', 'a958c268d36a1ba9', '931c1d2d37533a90', 'fb2975d5665a1b99', 'f7db1c3885c22f45', '291bafe0401a1eef', 'e93b0d998056d7e9', '63eb9609113d614e', '3629a2224f46a40a', '6412663af0a3fbc9', 'ff3a3d66c8ee56ee', '9de507b7c992d6d6', 'eba169fa3714e653', '756a391f7591e94e', '54e04f575d4029c4', 'df2009b18f7c3fb1', '0b71e61e1e17c345', '989f2066e72f5b80', '9291cf28f26d2002', 'f9f43aae75ffd8de', '8caa4bc721d9c703', '725eafe8d6fef7f2', 'd42a76417ff6664f', 'e7e7c227d895c317', '011e50231ff0194d', '4283c735e8de24d1', '33d75c64fbfa6310', '1ae382a9c567af90', '45f0e3af4462c10c', 'f6c074e7b0316fb1', '2d55394d0b4ae9ac', '079b3795a1dcf5bf', 'ea55a05e21e10e2c', 'dc9012c9cb16a311', '50086e9c98491191', 'b63194130c101ad4', '77164ea0f42d7dde', 'a80427cb3fcb5f58', '859fcb8ad7102712', '39fa3f5baa7beb7e', 'e106df4b868cd104', '1a2ee13c1ce89803', '55ef00d1f827a397', '6b1f1c8b07fa313a', 'b720be7f626fc4ae', '8c0d8c3de52ad942', '6b384800742acd84', '17a180f07eb4c6be', 'bbee5d99f98c4c47', '41f6fd0f3a48e1b5', '127dcba959d978d3', 'e22403b48be2f8a1', '82b5b5fc8855137d', 'c2e6047353474bec', 'a28dd1b4e4647262', '7e199f6befc995ea', 'c2c896b480d13347', 'b746a128e2db14a0', '5008d9b138499e36', '9da169fc7c83c5e2', 'd3c640083834ed62', 'c6dc2c555ed11786', '31ae3fbee05702c6', '0241dce759937d42', '23e677aa94ecb0a0', '242fe264517a4653', 'cfbb8b2008f75005', '64c425d1df3af0fe', '6e4c5bedc20c9fbe', 'ad529238027cbfb5', '1624980346c5ba0c', '220d184ab69993e0', '18965aaa40b15700', '5a4de1628949103a', 'e7ac07b3e9cc9fb6', '39191cf64c39bcaa', '227a0720a2397ed3', 'a7d4f763fe8b3db4', 'ce8361057bd05772', '4a3352d17579855f', '1d6c97e4dbeb8f06', 'e41a4acf4002504f', 'dcf4fb57c560a968', 'b8a7c3deddda9110', '91e21d354709dbd4', '1cf4678c60158d78', 'f4796a09a2100360', '32d9487c75f8202a', 'e47a476f4ed867c7', 'df1b929036f6c5cb', 'bd5319737f4632b9', '1bca1ded135801b9', '4026eb0264a56199', 'cec1a74af86eca8a', 'dd6e1fd7fdaff065', 'd7d82982cd7a69cd', 'a881f5ec1c901a45', 'ff5ea11dc0b14a3a', 'c7ef3f93f5b56717', '71ae56dc44fec3c5', '9c562a1f66f1dc35', 'b84b4a97930c2a79', '9d20ef9c4efa5fb6', 'b70bac975b905e9f', '03e8ed0fbed39c4c', '09af805b17660797', 'c5e34976cb9fb0a7', 'a71a8fcd716f8053', 'e17eda2c71192dbe', '8d15d32dd35010d9', 'eb4549e7c78b4555', 'c775ddc268fa96af', '8474724218b44edd', 'bd9c6b6adadc6a1b', 'c9448a42af8d30c9', '75eac37fc35b8153', 'ec603f3e5cd23077', '1486c7bbcf33a69e', '3d933ef42c205b48', 'e3b6d60bfa5ba675', '658c227d6f0df9ea', '55da6f51acbcb980', 'f3c16207d66a59a8', '68c7557a1512881f', '5a4b227ec6075d83', 'a474580d6a68a70b', '9e3cdf4e78f8a26b', '931127e9582e45ff', 'a083ead4ba852762', '0478770e0147658e', '4d1139901caccb0f', 'f33f65b982126e69', 'af462c42e10336d3', '5ec172ad1ffcd9db', '8f17b854b1025144', 'bb3854d983bcfe4c', 'a6d3c4cf59f56303', '27578df03143988f', 'e184370ee18cf989', '7bc522488a638898', 'dbda8f18a2a6a348', '62edfee7933f1d89', 'cb515bbc2873277f', '3c5c5cdcaf091d7a', 'd0289ed0a259b1a7', '451681089ac65870', 'ceeb060ede974e80', '079aa99341d7f666', '27276932d287f65c', 'ec4ca4588f23ced8', '74608beaead82870', '7a7c3d4213bf733c', '08d1e34361f70395', 'cf567c73e696926b', '9fed434e0a72902f', 'a26df22d00ec753c', 'f90176dcf016186f', '4b76375147ce0cee', 'be803ae5d88ba2a8', '5a29b3bde15e10d6', 'bf3c1d013ab95f77', '21b53fe6da1e4e9b', '32719ed183fe3e10', '6c57f9e917cdb296', 'ccfe1aa7f700853c', '8bd9eb062edeff6a', '3eadf848ee70c3c5', 'a8b83bba22adc585', 'b7971d473a1e4b27', '08221436b87562d1', 'f2d7d5a811245690', 'c5d73f6c0e9a4c2f', 'fc32d595feed829d', 'e2c21a84b7a10b6b', '602c83735171d3a3', 'b07b9858f51927a5', '6c22b727deacc12c', 'ba6623b6d06ce2c8', 'a9e50446bd5a8299', 'c44f2687f54d02fe', 'f43bce3e2e7d4bc1', '8e48a934a6123066', '37333c81137da642', 'a58a30d49698119f', '94a429581b68f4d2', '8fbbfc2707e4fd5c', '63a4c6fdce0ff5d9', '61b60bb6f9af49ef', 'ab374891334fad61', '4ecc4609dec3655a', 'dcdd4b3aaffc2e02', 'cbde4efa97645a0a', 'bdfef774d6f7c103', '756ce68fc3e0a74e', 'ff2b24dcfe4dcbd6', 'beb6a7b05efc4130', 'c7c749986677c0ce', 'e8e78b7f2a9b5aa1', '6c217ec9ed2a4107', 'f945e43c65e70eba', 'f578eec871fb1244', 'e4878d543222c73b', '189a9d62bff62216', '51ad0ced822484f9', 'd6d4f7136f8af1f0', 'a08bb9d8316f0a40', 'c61340d1adb13287', 'ee81f1d584e1da31', '78dadda184d4afc9', '4ad01f604f4528ad', '918e2c8f2602f0c8', '586f2ea0a1685279', 'c4ae4c6972eead5f', 'f8e42901ad4821a4', 'dc9fa8a7c3b855b2', 'ee0c1060ccda81d4', '805e84e5feed48a6', '334b238af10f1706', 'b796b83c1dbaeb90', '7bc4966e0c6217a7', '5226229b2339304e', '5c1580d83513470b', 'ed4829a43d33fa0b', 'b3fef1132d7517e0', 'a6e6263960c62657', 'd3847065c974328c', '671d95859dfa6ec8', 'ed89174684b2b237', 'eb3b88dbe19099b5', 'd9df216b8eba8fe0', '5a4270df61031196', 'f4cc3803807c97d4', 'd691f06be1d52c8f', 'c1bf053c824d542b', 'ec6992376aee423c', 'b83dc9a3fbd33a0d', '5f137605c909db82', '69a62ae2c678423e', '9f7b055ccf00a8dd', '6268b260ef9d0b5f', 'd4524e0cb8db6949', 'df11dcd8e58a37cb', '4ec0a8849e2ee6b2', '951a59d69b21ca5e', '8adf2aafaa69487d', 'c76dafddc2117fd8', '7a29fda288be9cfe', '9f0280550ad726bf', '60a1062dc94d2ab4', 'c1aa40eda0978d26', 'da238b54fd9ac5cb', '8dfbe2d260496889', 'e74b2d950b376ef2', 'bc6c3fe52bcc7d1e', 'd28851ad8d546350', '424beef7c31baa72', 'cbc0d75d0f02db49', 'cb7934c15e1caffa', 'd90df7dd19ea801e', '9e0779ee5b4f0d05', '5d5df193a848623c', '7e804668a7bb9d30', '41842c9526735857', '6123e6d9f5918c82', '060713dc080db45d', '8cf36edf7572eb9a', 'c466e36ca447f6ce', '06455d706b9c196c', '1da340a6250bad01', '37d453608e67592b', 'ca816cdcc6336f79', 'e8bd839bccac2615', '5849fd9f0eb55979', '6b2e3a8ec8392dbd', 'd00fd9b92771438c', 'a2d770107cd3f8c8', 'ed58a65b73f89c8d', 'ab29395529ce9611', 'e8ce257a057fd4be', '654c34c5441fe1db', '608768ec4fac4a56', '055bbfe4b1a4777e', '05f9b26bd5ce360b', '3cfe7c3f216e4f55', 'cad12817f28c89ab', 'ab523fc247cdc95d', 'd586347a5c9c6950', '8ca0a2cb2913a1f8', 'b9c99bdd8dfc4d50', '3ff5f011bf94db49', '507e361985de99af', 'ac22aa497a84c693', '2c1c79ab58415d59', 'a2a0a6244c2a5255', '2efba6c05182256e', 'ca4041362e0dff00', 'a0a151739cf224bd', 'a6105c0a611b41b0', '5f2c77e32ac41558', '4c6b890f9f4d3d43', 'f837c2e1c108ad43', 'ba631621274bd9fe', '7332e236ff05c8cf', '08344a4929a03420');

-- Deleted 1144 duplicate candidate records

-- ============================================================
-- STEP 3: Normalize party labels across ALL candidates
-- ============================================================

UPDATE candidates SET party = 'Democratic'
WHERE party IN ('Democrat', 'DEM', 'DEMOCRATIC', 'Dem', 'democratic', 'dem');
UPDATE candidates SET party = 'Republican'
WHERE party IN ('REP', 'REPUBLICAN', 'Rep', 'republican', 'rep');
UPDATE candidates SET party = 'Non-Partisan'
WHERE party IN ('NON', 'NP', 'IND', 'Non-partisan', 'nonpartisan', 'Non-Partisan (NP)', 'Independent');
UPDATE candidates SET party = 'Green'
WHERE party IN ('GREEN', 'Grn');
UPDATE candidates SET party = 'Libertarian'
WHERE party IN ('LIB', 'LIBERTARIAN', 'Lib');

-- ============================================================
-- STEP 4: Verification
-- ============================================================

-- Should return 0 after fix:
SELECT name, COUNT(DISTINCT id) as id_count, array_agg(DISTINCT party) as parties
FROM candidates
GROUP BY name
HAVING COUNT(DISTINCT id) > 1
ORDER BY id_count DESC
LIMIT 20;

-- Party distribution after normalization:
SELECT party, COUNT(*) as count
FROM candidates
GROUP BY party
ORDER BY count DESC;