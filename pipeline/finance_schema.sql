-- ═══════════════════════════════════════════════════════════════
-- Campaign Finance Heatmap Schema
-- 5 tables + materialized view + 3 RPC functions
-- Designed to sit alongside the existing 10 election tables
-- Uses the same precinct_id (MD5 hash) — no geometry duplication
-- ═══════════════════════════════════════════════════════════════

-- 1. finance_elections — one row per election cycle we track finance data for
CREATE TABLE IF NOT EXISTS finance_elections (
    id          TEXT PRIMARY KEY,              -- e.g. '2022_general_hd18'
    name        TEXT NOT NULL,                 -- 'HD-18 2022 General'
    race_label  TEXT NOT NULL,                 -- 'IL House District 18'
    year        INTEGER NOT NULL,
    type        TEXT NOT NULL,                 -- 'general'
    cycle_start DATE NOT NULL,                 -- contribution window start
    cycle_end   DATE NOT NULL,                 -- contribution window end (election day)
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 2. finance_committees — one row per committee we track
CREATE TABLE IF NOT EXISTS finance_committees (
    id              TEXT PRIMARY KEY,          -- e.g. 'gabel_22260'
    sbe_id          INTEGER NOT NULL,          -- IL SBE Committee ID
    committee_name  TEXT NOT NULL,
    candidate_name  TEXT NOT NULL,             -- normalized candidate name
    party           TEXT NOT NULL,             -- 'D' or 'R'
    status          TEXT NOT NULL DEFAULT 'active',  -- 'active' or 'final'
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- 3. finance_contributions — fact table, one row per itemized contribution
CREATE TABLE IF NOT EXISTS finance_contributions (
    id              BIGSERIAL PRIMARY KEY,
    finance_election_id TEXT NOT NULL REFERENCES finance_elections(id),
    committee_id    TEXT NOT NULL REFERENCES finance_committees(id),
    donor_name      TEXT,
    donor_address   TEXT,
    donor_city      TEXT,
    donor_state     TEXT,
    donor_zip       TEXT,
    amount          NUMERIC(12,2) NOT NULL,
    receipt_date    DATE NOT NULL,
    sbe_receipt_id  TEXT,                      -- original SBE row ID for dedup
    geocode_status  TEXT DEFAULT 'pending',    -- pending, matched, out_of_area, failed
    precinct_id     TEXT,                      -- FK to precincts.id (NULL if not geocoded yet)
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    created_at      TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT uq_finance_contrib_sbe UNIQUE(sbe_receipt_id)
);

CREATE INDEX IF NOT EXISTS idx_fc_election ON finance_contributions(finance_election_id);
CREATE INDEX IF NOT EXISTS idx_fc_committee ON finance_contributions(committee_id);
CREATE INDEX IF NOT EXISTS idx_fc_precinct ON finance_contributions(precinct_id) WHERE precinct_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_fc_geocode ON finance_contributions(geocode_status);

-- 4. finance_precinct_summary — aggregated per (precinct, election, committee)
CREATE TABLE IF NOT EXISTS finance_precinct_summary (
    id                  BIGSERIAL PRIMARY KEY,
    finance_election_id TEXT NOT NULL REFERENCES finance_elections(id),
    committee_id        TEXT NOT NULL REFERENCES finance_committees(id),
    precinct_id         TEXT NOT NULL,
    total_dollars       NUMERIC(12,2) NOT NULL DEFAULT 0,
    donor_count         INTEGER NOT NULL DEFAULT 0,
    avg_donation        NUMERIC(12,2) NOT NULL DEFAULT 0,
    max_donation        NUMERIC(12,2) NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT uq_fps UNIQUE(finance_election_id, committee_id, precinct_id)
);

CREATE INDEX IF NOT EXISTS idx_fps_election ON finance_precinct_summary(finance_election_id);
CREATE INDEX IF NOT EXISTS idx_fps_precinct ON finance_precinct_summary(precinct_id);

-- 5. finance_precinct_race_summary — cross-candidate metrics per (precinct, election)
CREATE TABLE IF NOT EXISTS finance_precinct_race_summary (
    id                  BIGSERIAL PRIMARY KEY,
    finance_election_id TEXT NOT NULL REFERENCES finance_elections(id),
    precinct_id         TEXT NOT NULL,
    total_dollars       NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_donors        INTEGER NOT NULL DEFAULT 0,
    top_committee_id    TEXT REFERENCES finance_committees(id),
    dollar_margin       NUMERIC(12,2) NOT NULL DEFAULT 0,  -- positive = top committee leads
    donor_margin        NUMERIC(6,4) NOT NULL DEFAULT 0,    -- -1 to +1 normalized
    created_at          TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT uq_fprs UNIQUE(finance_election_id, precinct_id)
);

CREATE INDEX IF NOT EXISTS idx_fprs_election ON finance_precinct_race_summary(finance_election_id);
CREATE INDEX IF NOT EXISTS idx_fprs_precinct ON finance_precinct_race_summary(precinct_id);


-- ═══════════════════════════════════════════════════════════════
-- Materialized View: pre-joined for frontend queries
-- ═══════════════════════════════════════════════════════════════

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_finance_precinct AS
SELECT
    fps.finance_election_id,
    fps.committee_id,
    fc.candidate_name,
    fc.party,
    fps.precinct_id,
    fps.total_dollars,
    fps.donor_count,
    fps.avg_donation,
    fps.max_donation,
    fprs.total_dollars   AS race_total_dollars,
    fprs.total_donors    AS race_total_donors,
    fprs.top_committee_id,
    fprs.dollar_margin,
    fprs.donor_margin
FROM finance_precinct_summary fps
JOIN finance_committees fc ON fc.id = fps.committee_id
LEFT JOIN finance_precinct_race_summary fprs
    ON fprs.finance_election_id = fps.finance_election_id
    AND fprs.precinct_id = fps.precinct_id;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_fp_lookup
    ON mv_finance_precinct(finance_election_id, committee_id, precinct_id);


-- ═══════════════════════════════════════════════════════════════
-- RPC Function 1: get_finance_race_list
-- Returns available finance election cycles for the dropdown
-- ═══════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION get_finance_race_list()
RETURNS TABLE(
    id TEXT,
    name TEXT,
    race_label TEXT,
    year INTEGER,
    type TEXT
)
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path TO 'public'
AS $$
    SELECT id, name, race_label, year, type
    FROM finance_elections
    ORDER BY year DESC, type;
$$;


-- ═══════════════════════════════════════════════════════════════
-- RPC Function 2: get_finance_candidates
-- Returns committees for a given finance election
-- ═══════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION get_finance_candidates(p_election_id TEXT)
RETURNS TABLE(
    committee_id TEXT,
    committee_name TEXT,
    candidate_name TEXT,
    party TEXT,
    total_dollars NUMERIC,
    total_donors BIGINT
)
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path TO 'public'
AS $$
    SELECT
        fc.id AS committee_id,
        fc.committee_name,
        fc.candidate_name,
        fc.party,
        COALESCE(SUM(fps.total_dollars), 0) AS total_dollars,
        COALESCE(SUM(fps.donor_count), 0)::BIGINT AS total_donors
    FROM finance_committees fc
    LEFT JOIN finance_precinct_summary fps
        ON fps.committee_id = fc.id
        AND fps.finance_election_id = p_election_id
    GROUP BY fc.id, fc.committee_name, fc.candidate_name, fc.party
    HAVING COALESCE(SUM(fps.total_dollars), 0) > 0
       OR EXISTS (
           SELECT 1 FROM finance_contributions fcon
           WHERE fcon.committee_id = fc.id
             AND fcon.finance_election_id = p_election_id
       )
    ORDER BY COALESCE(SUM(fps.total_dollars), 0) DESC;
$$;


-- ═══════════════════════════════════════════════════════════════
-- RPC Function 3: get_finance_map
-- Main map data function — 8 modes, same return shape as get_race_map
-- ═══════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION get_finance_map(
    p_election_id      TEXT,
    p_mode             TEXT,
    p_committee_id_a   TEXT DEFAULT NULL,
    p_committee_id_b   TEXT DEFAULT NULL,
    p_election_id_prev TEXT DEFAULT NULL
)
RETURNS TABLE(
    precinct_id     TEXT,
    metric_value    NUMERIC,
    display_label   TEXT,
    party           TEXT,
    total_dollars   NUMERIC,
    donor_count     INTEGER,
    dollar_margin   NUMERIC,
    donor_margin    NUMERIC
)
LANGUAGE plpgsql STABLE SECURITY DEFINER
SET search_path TO 'public'
AS $$
BEGIN
    -- MODE: supporters — donor share (committee A donors / total precinct donors)
    IF p_mode = 'supporters' THEN
        RETURN QUERY
        SELECT
            mv.precinct_id,
            CASE WHEN mv.race_total_donors > 0
                 THEN ROUND(mv.donor_count::NUMERIC / mv.race_total_donors, 4)
                 ELSE 0 END AS metric_value,
            mv.donor_count || ' of ' || mv.race_total_donors || ' donors' AS display_label,
            mv.party,
            mv.total_dollars,
            mv.donor_count::INTEGER,
            mv.dollar_margin,
            mv.donor_margin
        FROM mv_finance_precinct mv
        WHERE mv.finance_election_id = p_election_id
          AND mv.committee_id = p_committee_id_a;

    -- MODE: whales — total dollars raised by committee A per precinct
    ELSIF p_mode = 'whales' THEN
        RETURN QUERY
        SELECT
            mv.precinct_id,
            mv.total_dollars AS metric_value,
            '$' || TRIM(TO_CHAR(mv.total_dollars, '999,999,999')) AS display_label,
            mv.party,
            mv.total_dollars,
            mv.donor_count::INTEGER,
            mv.dollar_margin,
            mv.donor_margin
        FROM mv_finance_precinct mv
        WHERE mv.finance_election_id = p_election_id
          AND mv.committee_id = p_committee_id_a;

    -- MODE: donor_margin — normalized donor margin (-1 to +1)
    ELSIF p_mode = 'donor_margin' THEN
        RETURN QUERY
        SELECT DISTINCT ON (fprs.precinct_id)
            fprs.precinct_id,
            fprs.donor_margin AS metric_value,
            CASE WHEN fprs.donor_margin >= 0
                 THEN 'D+' || ROUND(ABS(fprs.donor_margin * 100))::TEXT || '%'
                 ELSE 'R+' || ROUND(ABS(fprs.donor_margin * 100))::TEXT || '%'
            END AS display_label,
            CASE WHEN fprs.donor_margin >= 0 THEN 'D' ELSE 'R' END AS party,
            fprs.total_dollars,
            fprs.total_donors::INTEGER AS donor_count,
            fprs.dollar_margin,
            fprs.donor_margin
        FROM finance_precinct_race_summary fprs
        WHERE fprs.finance_election_id = p_election_id;

    -- MODE: candidate — total dollars for committee A (same as whales but different color scale)
    ELSIF p_mode = 'candidate' THEN
        RETURN QUERY
        SELECT
            mv.precinct_id,
            mv.total_dollars AS metric_value,
            mv.candidate_name || ': $' || TRIM(TO_CHAR(mv.total_dollars, '999,999,999')) AS display_label,
            mv.party,
            mv.total_dollars,
            mv.donor_count::INTEGER,
            mv.dollar_margin,
            mv.donor_margin
        FROM mv_finance_precinct mv
        WHERE mv.finance_election_id = p_election_id
          AND mv.committee_id = p_committee_id_a;

    -- MODE: vs — dollar share comparison between two committees
    ELSIF p_mode = 'vs' THEN
        RETURN QUERY
        WITH combined AS (
            SELECT
                mv.precinct_id,
                SUM(CASE WHEN mv.committee_id = p_committee_id_a THEN mv.total_dollars ELSE 0 END) AS dollars_a,
                SUM(CASE WHEN mv.committee_id = p_committee_id_b THEN mv.total_dollars ELSE 0 END) AS dollars_b,
                MAX(CASE WHEN mv.committee_id = p_committee_id_a THEN mv.party END) AS party_a,
                MAX(CASE WHEN mv.committee_id = p_committee_id_a THEN mv.candidate_name END) AS name_a,
                MAX(CASE WHEN mv.committee_id = p_committee_id_b THEN mv.candidate_name END) AS name_b,
                SUM(mv.total_dollars) AS total,
                MAX(mv.dollar_margin) AS dollar_margin,
                MAX(mv.donor_margin) AS donor_margin,
                SUM(mv.donor_count) AS donor_count
            FROM mv_finance_precinct mv
            WHERE mv.finance_election_id = p_election_id
              AND mv.committee_id IN (p_committee_id_a, p_committee_id_b)
            GROUP BY mv.precinct_id
        )
        SELECT
            c.precinct_id,
            CASE WHEN c.total > 0 THEN ROUND(c.dollars_a / c.total, 4) ELSE 0.5 END AS metric_value,
            COALESCE(c.name_a,'A') || ': $' || TRIM(TO_CHAR(c.dollars_a, '999,999')) || ' vs ' ||
            COALESCE(c.name_b,'B') || ': $' || TRIM(TO_CHAR(c.dollars_b, '999,999')) AS display_label,
            c.party_a AS party,
            c.total AS total_dollars,
            c.donor_count::INTEGER,
            c.dollar_margin,
            c.donor_margin
        FROM combined c;

    -- MODE: money_delta — change in dollars between two cycles
    ELSIF p_mode = 'money_delta' THEN
        RETURN QUERY
        WITH curr AS (
            SELECT precinct_id, SUM(total_dollars) AS dollars
            FROM finance_precinct_summary
            WHERE finance_election_id = p_election_id AND committee_id = p_committee_id_a
            GROUP BY precinct_id
        ),
        prev AS (
            SELECT precinct_id, SUM(total_dollars) AS dollars
            FROM finance_precinct_summary
            WHERE finance_election_id = p_election_id_prev AND committee_id = p_committee_id_a
            GROUP BY precinct_id
        )
        SELECT
            COALESCE(c.precinct_id, p.precinct_id) AS precinct_id,
            COALESCE(c.dollars, 0) - COALESCE(p.dollars, 0) AS metric_value,
            '$' || TRIM(TO_CHAR(COALESCE(c.dollars, 0) - COALESCE(p.dollars, 0), 'S999,999')) AS display_label,
            (SELECT fc.party FROM finance_committees fc WHERE fc.id = p_committee_id_a) AS party,
            COALESCE(c.dollars, 0) AS total_dollars,
            0::INTEGER AS donor_count,
            0::NUMERIC AS dollar_margin,
            0::NUMERIC AS donor_margin
        FROM curr c FULL OUTER JOIN prev p ON c.precinct_id = p.precinct_id;

    -- MODE: swing — change in donor margin between two cycles
    ELSIF p_mode = 'swing' THEN
        RETURN QUERY
        WITH curr AS (
            SELECT precinct_id, donor_margin FROM finance_precinct_race_summary
            WHERE finance_election_id = p_election_id
        ),
        prev AS (
            SELECT precinct_id, donor_margin FROM finance_precinct_race_summary
            WHERE finance_election_id = p_election_id_prev
        )
        SELECT
            COALESCE(c.precinct_id, p.precinct_id) AS precinct_id,
            COALESCE(c.donor_margin, 0) - COALESCE(p.donor_margin, 0) AS metric_value,
            CASE
                WHEN COALESCE(c.donor_margin, 0) - COALESCE(p.donor_margin, 0) >= 0
                THEN 'D+' || ROUND(ABS((COALESCE(c.donor_margin,0) - COALESCE(p.donor_margin,0)) * 100))::TEXT || '%'
                ELSE 'R+' || ROUND(ABS((COALESCE(c.donor_margin,0) - COALESCE(p.donor_margin,0)) * 100))::TEXT || '%'
            END AS display_label,
            CASE WHEN COALESCE(c.donor_margin,0) - COALESCE(p.donor_margin,0) >= 0 THEN 'D' ELSE 'R' END AS party,
            0::NUMERIC AS total_dollars,
            0::INTEGER AS donor_count,
            0::NUMERIC AS dollar_margin,
            COALESCE(c.donor_margin, 0) - COALESCE(p.donor_margin, 0) AS donor_margin
        FROM curr c FULL OUTER JOIN prev p ON c.precinct_id = p.precinct_id;

    -- MODE: votes (finance analogue) — raw dollars per precinct in the race
    ELSIF p_mode = 'votes' THEN
        RETURN QUERY
        SELECT DISTINCT ON (fprs.precinct_id)
            fprs.precinct_id,
            fprs.total_dollars AS metric_value,
            '$' || TRIM(TO_CHAR(fprs.total_dollars, '999,999,999')) AS display_label,
            CASE WHEN fprs.donor_margin >= 0 THEN 'D' ELSE 'R' END AS party,
            fprs.total_dollars,
            fprs.total_donors::INTEGER AS donor_count,
            fprs.dollar_margin,
            fprs.donor_margin
        FROM finance_precinct_race_summary fprs
        WHERE fprs.finance_election_id = p_election_id;

    ELSE
        RAISE EXCEPTION 'Unknown finance mode: %', p_mode;
    END IF;
END;
$$;


-- ═══════════════════════════════════════════════════════════════
-- RLS Policies — allow anon read access (same as existing tables)
-- ═══════════════════════════════════════════════════════════════

ALTER TABLE finance_elections ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_committees ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_contributions ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_precinct_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_precinct_race_summary ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "anon_read_finance_elections" ON finance_elections FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "anon_read_finance_committees" ON finance_committees FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "anon_read_finance_contributions" ON finance_contributions FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "anon_read_finance_precinct_summary" ON finance_precinct_summary FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "anon_read_finance_precinct_race_summary" ON finance_precinct_race_summary FOR SELECT USING (true);

-- Grant execute on new functions
GRANT EXECUTE ON FUNCTION get_finance_race_list TO anon, authenticated;
GRANT EXECUTE ON FUNCTION get_finance_candidates TO anon, authenticated;
GRANT EXECUTE ON FUNCTION get_finance_map TO anon, authenticated;
