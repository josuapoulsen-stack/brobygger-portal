-- =============================================================================
-- Migration 003 — Brugere og adgangskontrol
-- Kræver: 001, 002
--
-- Brobyggere og rådgivere er begge "brugere" — Azure Entra ID er kilde til
-- identitet (azure_oid). Rollerne tildeles som app-roller i Entra ID.
-- =============================================================================

CREATE TABLE brugere (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    azure_oid       TEXT UNIQUE NOT NULL,            -- Entra ID Object ID
    display_name    TEXT NOT NULL,
    email           TEXT,
    rolle           bruger_rolle NOT NULL,
    hq              TEXT,
    -- Kobling: brobyggere.azure_oid = brugere.azure_oid
    -- Rådgivere har ingen brobygger-post
    aktiv           BOOL NOT NULL DEFAULT TRUE,
    sidst_login     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_brugere_azure_oid ON brugere(azure_oid);
CREATE INDEX idx_brugere_rolle     ON brugere(rolle);
CREATE INDEX idx_brugere_hq        ON brugere(hq);

CREATE TRIGGER trg_brugere_updated BEFORE UPDATE ON brugere
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Tilføj FK fra beskeder og notifikationer
ALTER TABLE beskeder
    ADD CONSTRAINT fk_beskeder_bruger
    FOREIGN KEY (fra_bruger_id) REFERENCES brugere(id);

ALTER TABLE notifikationer
    ADD CONSTRAINT fk_notif_bruger
    FOREIGN KEY (bruger_id) REFERENCES brugere(id);

ALTER TABLE push_subscriptions
    ADD CONSTRAINT fk_push_bruger
    FOREIGN KEY (bruger_id) REFERENCES brugere(id);

-- Kobl mennesker.raadgiver_id
ALTER TABLE mennesker
    ADD CONSTRAINT fk_mennesker_raadgiver
    FOREIGN KEY (raadgiver_id) REFERENCES brugere(id);

-- =============================================================================
-- AUDIT LOG — alle ændringer i følsomme tabeller
-- =============================================================================

CREATE TABLE audit_log (
    id              BIGSERIAL PRIMARY KEY,
    tidspunkt       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    bruger_id       UUID REFERENCES brugere(id),
    azure_oid       TEXT,                            -- backup hvis brugere-FK fejler
    handling        TEXT NOT NULL,                   -- 'create', 'update', 'delete'
    tabel           TEXT NOT NULL,
    rekord_id       UUID NOT NULL,
    aendringer      JSONB,                           -- { felt: [fra, til] }
    ip_adresse      TEXT,
    user_agent      TEXT
);

CREATE INDEX idx_audit_tidspunkt ON audit_log(tidspunkt DESC);
CREATE INDEX idx_audit_rekord    ON audit_log(tabel, rekord_id);

-- Trigger-funktion til automatisk audit af mennesker og aftaler
CREATE OR REPLACE FUNCTION audit_changes()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO audit_log (handling, tabel, rekord_id, aendringer)
    VALUES (
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        jsonb_build_object('old', row_to_json(OLD), 'new', row_to_json(NEW))
    );
    RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER audit_mennesker
    AFTER INSERT OR UPDATE OR DELETE ON mennesker
    FOR EACH ROW EXECUTE FUNCTION audit_changes();

CREATE TRIGGER audit_aftaler
    AFTER INSERT OR UPDATE OR DELETE ON aftaler
    FOR EACH ROW EXECUTE FUNCTION audit_changes();
