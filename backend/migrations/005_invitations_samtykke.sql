-- =============================================================================
-- Migration 005 — Magic link invitations + GDPR-samtykke
-- Kræver: 001, 002, 003, 004
-- =============================================================================

-- =============================================================================
-- INVITATIONS (magic link tokens til brobyggere)
-- =============================================================================

CREATE TABLE invitations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           TEXT NOT NULL,
    navn            TEXT NOT NULL,
    hq              TEXT,
    -- Token gemmes kun som hash — det rå token sendes i email og opbevares aldrig
    token_hash      TEXT NOT NULL UNIQUE,   -- sha256 af det signerede token
    sendt_af        UUID REFERENCES brugere(id),
    expires_at      TIMESTAMPTZ NOT NULL,
    brugt           BOOL NOT NULL DEFAULT FALSE,
    brugt_at        TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_invitations_email   ON invitations(email);
CREATE INDEX idx_invitations_expires ON invitations(expires_at) WHERE NOT brugt;

-- Ryd udløbne invitations (kør som dagligt job)
CREATE OR REPLACE FUNCTION ryd_udloebne_invitations()
RETURNS INT LANGUAGE plpgsql AS $$
DECLARE antal INT;
BEGIN
    DELETE FROM invitations WHERE expires_at < NOW() AND NOT brugt;
    GET DIAGNOSTICS antal = ROW_COUNT;
    RETURN antal;
END;
$$;

-- =============================================================================
-- SAMTYKKE (GDPR Art. 6 + 9)
-- Registrerer hvornår, af hvem, og til hvad samtykke er givet
-- =============================================================================

CREATE TABLE samtykker (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    menneske_id     UUID NOT NULL REFERENCES mennesker(id),
    -- Version af samtykkeerklæringen (dato-baseret versionering)
    version         TEXT NOT NULL,          -- fx "2025-01-01"
    givet_af        TEXT,                   -- navn på koordinator/rådgiver der indhentede
    -- Hvad der er givet samtykke til
    helbredsdata    BOOL NOT NULL DEFAULT FALSE,  -- Art. 9 — kræver eksplicit samtykke
    kontakt_data    BOOL NOT NULL DEFAULT TRUE,   -- Art. 6 — standardsamtykke
    -- Kontekst (til auditformål)
    ip_adresse      TEXT,
    enhed           TEXT,                   -- user-agent
    -- Tilbagekaldelse
    trukket_tilbage BOOL NOT NULL DEFAULT FALSE,
    trukket_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_samtykke_menneske ON samtykker(menneske_id);
CREATE INDEX idx_samtykke_version  ON samtykker(version);

-- Trigger: log samtykke-ændringer i audit
CREATE TRIGGER audit_samtykker
    AFTER INSERT OR UPDATE ON samtykker
    FOR EACH ROW EXECUTE FUNCTION audit_changes();

-- =============================================================================
-- Tilføj AZURE_CLIENT_SECRET til App Service settings
-- (Huskeliste — håndteres i infra/main.bicep ved Key Vault-integration)
-- =============================================================================

-- Kommenter til fremtidig reference:
-- App Service skal have:
--   AZURE_CLIENT_SECRET  → fra Key Vault reference
--   Tilladelse i Entra ID: Mail.Send (application permission)
