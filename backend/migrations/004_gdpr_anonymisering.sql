-- =============================================================================
-- Migration 004 — GDPR-anonymisering og dataretentionspolitik
-- Kræver: 001, 002, 003
--
-- Implementerer:
--   • Anonymiseringsfunktion for slettet data (30-dages grace period)
--   • Sletningspolitik for audit-logs (5 år jf. Datatilsynets vejledning)
--   • Row-level security (RLS) — brobyggere ser kun egne data
-- =============================================================================

-- =============================================================================
-- ANONYMISERING
-- Kørsel: planlagt job (fx månedligt via cron / pg_cron)
-- =============================================================================

CREATE OR REPLACE FUNCTION anonymiser_slettede_mennesker()
RETURNS INT LANGUAGE plpgsql AS $$
DECLARE
    antal INT;
BEGIN
    UPDATE mennesker SET
        navn             = 'Anonymiseret',
        email            = NULL,
        telefon          = NULL,
        adresse          = NULL,
        helbredsnoter_enc = NULL,
        noter            = NULL,
        alder            = NULL,
        kon              = NULL,
        anonymized_at    = NOW()
    WHERE
        deleted_at IS NOT NULL
        AND deleted_at < NOW() - INTERVAL '30 days'
        AND anonymized_at IS NULL;

    GET DIAGNOSTICS antal = ROW_COUNT;
    RETURN antal;
END;
$$;

-- =============================================================================
-- RETENTION: Ryd gammel audit-log (bevar 5 år)
-- =============================================================================

CREATE OR REPLACE FUNCTION ryd_gammel_audit()
RETURNS INT LANGUAGE plpgsql AS $$
DECLARE
    antal INT;
BEGIN
    DELETE FROM audit_log WHERE tidspunkt < NOW() - INTERVAL '5 years';
    GET DIAGNOSTICS antal = ROW_COUNT;
    RETURN antal;
END;
$$;

-- =============================================================================
-- ROW-LEVEL SECURITY
-- Brobyggere kan kun se egne aftaler og beskeder.
-- Rådgivere og admins ser alt inden for deres HQ.
--
-- Forudsætning: app sætter session-variabel ved API-kald:
--   SET LOCAL app.current_user_id = '<uuid>';
--   SET LOCAL app.current_rolle = 'Brobygger';
-- =============================================================================

ALTER TABLE aftaler ENABLE ROW LEVEL SECURITY;

CREATE POLICY brobygger_egne_aftaler ON aftaler
    USING (
        current_setting('app.current_rolle', TRUE) = 'Admin'
        OR current_setting('app.current_rolle', TRUE) = 'Raadgiver'
        OR brobygger_id = current_setting('app.current_user_id', TRUE)::UUID
    );

ALTER TABLE mennesker ENABLE ROW LEVEL SECURITY;

CREATE POLICY brobygger_egne_mennesker ON mennesker
    USING (
        current_setting('app.current_rolle', TRUE) = 'Admin'
        OR current_setting('app.current_rolle', TRUE) = 'Raadgiver'
        OR matched_with = current_setting('app.current_user_id', TRUE)::UUID
    );

-- =============================================================================
-- KRYPTERINGSNØGLE-ROTATION LOG (til compliance-dokumentation)
-- =============================================================================

CREATE TABLE encryption_key_log (
    id          SERIAL PRIMARY KEY,
    roteret_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    roteret_af  UUID REFERENCES brugere(id),
    note        TEXT
);
