-- =============================================================================
-- Migration 001 — Initialt skema for SoS Brobygger Portal
--
-- Kør med:
--   psql $DATABASE_URL -f backend/migrations/001_initial_schema.sql
--
-- Rækkefølge: denne fil SKAL køres før alle andre migrations.
-- =============================================================================

-- Aktiver nødvendige extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- Til kryptering af sundhedsdata (Art. 9)

-- =============================================================================
-- ENUM types
-- =============================================================================

CREATE TYPE menneske_status  AS ENUM ('ny', 'matched', 'aktiv', 'afsluttet', 'venteliste');
CREATE TYPE brobygger_status AS ENUM ('ny', 'aktiv', 'pause', 'inaktiv');
CREATE TYPE aftale_status    AS ENUM ('planlagt', 'gennemfoert', 'aflyst', 'udsat');
CREATE TYPE aftale_type      AS ENUM ('moede', 'aktivitet', 'telefonopkald', 'online');
CREATE TYPE bruger_rolle     AS ENUM ('Brobygger', 'Raadgiver', 'Admin');
CREATE TYPE kon_type         AS ENUM ('mand', 'kvinde', 'ikke-binaer', 'oensker-ikke');

-- =============================================================================
-- BROBYGGERE (frivillige)
-- =============================================================================

CREATE TABLE brobyggere (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    azure_oid       TEXT UNIQUE,                    -- Azure Entra ID Object ID
    navn            TEXT NOT NULL,
    email           TEXT,
    telefon         TEXT,
    -- Profil
    typer           TEXT[]  NOT NULL DEFAULT '{}',  -- ['en-til-en', 'gruppe', ...]
    sprog           TEXT[]  NOT NULL DEFAULT '{"dansk"}',
    hq              TEXT,                            -- Koordinatorkontor
    kon             kon_type,
    bio             TEXT,
    avatar_url      TEXT,
    -- Kapacitet
    status          brobygger_status NOT NULL DEFAULT 'ny',
    active          INT  NOT NULL DEFAULT 0 CHECK (active >= 0),
    max_active      INT  NOT NULL DEFAULT 3 CHECK (max_active > 0),
    -- Tilgængelighed
    tilgaengelig_fra DATE,
    naeste_tid       TEXT,
    -- Metadata
    startdato       DATE,
    seneste_moede   DATE,
    noter           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_brobyggere_status ON brobyggere(status);
CREATE INDEX idx_brobyggere_hq     ON brobyggere(hq);

-- =============================================================================
-- MENNESKER (borgere/klienter)
-- GDPR Art. 9: helbredsdata krypteres med pgcrypto
-- =============================================================================

CREATE TABLE mennesker (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    navn            TEXT NOT NULL,
    alder           INT,
    kon             kon_type,
    email           TEXT,
    telefon         TEXT,
    adresse         TEXT,
    -- Behov
    typer           TEXT[]  NOT NULL DEFAULT '{}',
    sprog           TEXT[]  NOT NULL DEFAULT '{"dansk"}',
    noter           TEXT,
    -- Helbred — krypteret (GDPR Art. 9)
    -- Kryptér ved indsætning: pgp_sym_encrypt(data, current_setting('app.encryption_key'))
    -- Dekryptér ved læsning: pgp_sym_decrypt(helbredsnoter_enc, current_setting('app.encryption_key'))
    helbredsnoter_enc BYTEA,                         -- krypteret helbredsdata
    -- Status og matching
    status          menneske_status NOT NULL DEFAULT 'ny',
    matched_with    UUID REFERENCES brobyggere(id),
    -- Koordinator
    raadgiver_id    UUID,                            -- FK til brugere-tabel (Step 2)
    hq              TEXT,
    -- Metadata
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- GDPR: blødt slet — anonymiseres 30 dage efter sletning
    deleted_at      TIMESTAMPTZ,
    anonymized_at   TIMESTAMPTZ
);

CREATE INDEX idx_mennesker_status     ON mennesker(status);
CREATE INDEX idx_mennesker_matched    ON mennesker(matched_with);
CREATE INDEX idx_mennesker_deleted    ON mennesker(deleted_at) WHERE deleted_at IS NULL;

-- =============================================================================
-- AFTALER (møder og aktiviteter)
-- =============================================================================

CREATE TABLE aftaler (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brobygger_id    UUID NOT NULL REFERENCES brobyggere(id),
    menneske_id     UUID NOT NULL REFERENCES mennesker(id),
    dato            TIMESTAMPTZ NOT NULL,
    varighed        INT  NOT NULL DEFAULT 60,        -- minutter
    type            aftale_type NOT NULL DEFAULT 'moede',
    sted            TEXT,
    beskrivelse     TEXT,
    status          aftale_status NOT NULL DEFAULT 'planlagt',
    notes           TEXT NOT NULL DEFAULT '',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_aftaler_brobygger ON aftaler(brobygger_id);
CREATE INDEX idx_aftaler_menneske  ON aftaler(menneske_id);
CREATE INDEX idx_aftaler_dato      ON aftaler(dato);
CREATE INDEX idx_aftaler_status    ON aftaler(status);

-- =============================================================================
-- Trigger: opdatér updated_at automatisk
-- =============================================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_brobyggere_updated BEFORE UPDATE ON brobyggere
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_mennesker_updated BEFORE UPDATE ON mennesker
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_aftaler_updated BEFORE UPDATE ON aftaler
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
