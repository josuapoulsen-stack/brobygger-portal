-- =============================================================================
-- SoS Brobygger Portal — Komplet PostgreSQL 16 Skema
--
-- Inkluderer: ENUM-types, tabeller, indexes, FK-constraints,
-- updated_at-triggers, row-level audit-trigger, views og seed-data.
--
-- Kræver: PostgreSQL 16+
-- Extensions: uuid-ossp, pgcrypto
--
-- Kør:
--   psql $DATABASE_URL -f db/schema.sql
--
-- For at køre uden at stoppe ved fejl (idempotent re-run):
--   psql $DATABASE_URL --set ON_ERROR_STOP=on -f db/schema.sql
-- =============================================================================

-- =============================================================================
-- EXTENSIONS
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   -- uuid_generate_v4() (fallback)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";    -- gen_random_uuid(), pgp_sym_encrypt/decrypt


-- =============================================================================
-- ENUM TYPES
-- =============================================================================

-- Brobygger-status
CREATE TYPE brobygger_status AS ENUM (
    'ny',       -- Nyregistreret — afventer onboarding
    'aktiv',    -- Aktiv og kan modtage matches
    'pause',    -- Midlertidigt utilgængelig
    'inaktiv'   -- Ikke længere frivillig
);

-- Menneske-status (forløbsstatus)
CREATE TYPE menneske_status AS ENUM (
    'ny',         -- Ny henvendelse — endnu ikke behandlet
    'venteliste', -- Venter på egnet brobygger
    'matched',    -- Tilknyttet brobygger — forløb ikke startet
    'aktiv',      -- Aktivt forløb i gang
    'afsluttet'   -- Forløbet er afsluttet
);

-- Aftale-status
CREATE TYPE aftale_status AS ENUM (
    'planlagt',
    'gennemfoert',
    'aflyst',
    'udsat'
);

-- Aftale-type
CREATE TYPE aftale_type AS ENUM (
    'moede',
    'aktivitet',
    'telefonopkald',
    'online'
);

-- Bruger-rolle (fra Azure Entra ID app roles)
CREATE TYPE bruger_rolle AS ENUM (
    'Brobygger',
    'Raadgiver',
    'Admin'
);

-- Køn
CREATE TYPE kon_type AS ENUM (
    'mand',
    'kvinde',
    'ikke-binaer',
    'oensker-ikke'
);

-- Notifikations-type
CREATE TYPE notif_type AS ENUM (
    'ny_aftale',
    'aftale_godkendt',
    'aftale_aflyst',
    'ny_besked',
    'match_forslag',
    'paamindelse',
    'system'
);

-- Kontaktlog-type
CREATE TYPE kontakt_type AS ENUM (
    'telefonisk',       -- Telefonisk kontakt
    'moede_brobygger',  -- Møde med brobygger
    'foelge_primaer',   -- Følge til primær aktivitet
    'foelge_sekundaer', -- Følge til sekundær aktivitet
    'notat',            -- Administrativt notat
    'andet'             -- Anden kontaktform
);


-- =============================================================================
-- HJÆLPEFUNKTION: opdatér updated_at
-- =============================================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


-- =============================================================================
-- TABEL: brugere
-- Alle systembrugere (rådgivere, admins, og evt. brobyggere der logger ind).
-- Identitet stammer fra Microsoft Entra ID — azure_oid er nøglen.
-- =============================================================================

CREATE TABLE brugere (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    azure_oid       TEXT        UNIQUE NOT NULL,     -- Entra ID Object ID
    display_name    TEXT        NOT NULL,
    email           TEXT,
    rolle           bruger_rolle NOT NULL,
    hq              TEXT,                            -- Koordinatorkontor
    aktiv           BOOLEAN     NOT NULL DEFAULT TRUE,
    sidst_login     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_brugere_azure_oid ON brugere(azure_oid);
CREATE INDEX idx_brugere_rolle     ON brugere(rolle);
CREATE INDEX idx_brugere_hq        ON brugere(hq) WHERE hq IS NOT NULL;
CREATE INDEX idx_brugere_aktiv     ON brugere(aktiv) WHERE aktiv = TRUE;

CREATE TRIGGER trg_brugere_updated
    BEFORE UPDATE ON brugere
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =============================================================================
-- TABEL: brobyggere
-- Frivillige brobyggere — kan have et tilknyttet brugere-login via azure_oid.
-- =============================================================================

CREATE TABLE brobyggere (
    id               UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Kobling til login: brobygger med brugerkonto har azure_oid her
    azure_oid        TEXT           UNIQUE,
    bruger_id        UUID           REFERENCES brugere(id) ON DELETE SET NULL,
    -- Stamoplysninger
    navn             TEXT           NOT NULL,
    email            TEXT,
    telefon          TEXT,
    typer            TEXT[]         NOT NULL DEFAULT '{}',
    sprog            TEXT[]         NOT NULL DEFAULT '{"dansk"}',
    hq               TEXT,
    kon              kon_type,
    bio              TEXT,
    avatar_url       TEXT,
    -- Kapacitet
    status           brobygger_status NOT NULL DEFAULT 'ny',
    active           INTEGER        NOT NULL DEFAULT 0 CHECK (active >= 0),
    max_active       INTEGER        NOT NULL DEFAULT 3 CHECK (max_active > 0),
    -- Tilgængelighed
    tilgaengelig_fra DATE,
    naeste_tid       TEXT,
    -- Metadata
    startdato        DATE,
    seneste_moede    DATE,
    noter            TEXT,
    -- Soft delete / deaktivering sker via status = 'inaktiv'
    created_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_brobygger_active_lte_max CHECK (active <= max_active)
);

CREATE INDEX idx_brobyggere_status        ON brobyggere(status);
CREATE INDEX idx_brobyggere_hq            ON brobyggere(hq) WHERE hq IS NOT NULL;
CREATE INDEX idx_brobyggere_azure_oid     ON brobyggere(azure_oid) WHERE azure_oid IS NOT NULL;
CREATE INDEX idx_brobyggere_aktiv_kapacitet
    ON brobyggere(status, active, max_active)
    WHERE status = 'aktiv';

CREATE TRIGGER trg_brobyggere_updated
    BEFORE UPDATE ON brobyggere
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =============================================================================
-- TABEL: mennesker
-- Borgere/klienter der søger social kontakt via brobygning.
-- GDPR Art. 9: helbredsdata krypteres med pgcrypto.
-- =============================================================================

CREATE TABLE mennesker (
    id                UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Stamoplysninger
    navn              TEXT           NOT NULL,
    alder             INTEGER        CHECK (alder IS NULL OR (alder >= 0 AND alder <= 120)),
    kon               kon_type,
    email             TEXT,
    telefon           TEXT,
    adresse           TEXT,
    -- Behov og profil
    typer             TEXT[]         NOT NULL DEFAULT '{}',
    sprog             TEXT[]         NOT NULL DEFAULT '{"dansk"}',
    noter             TEXT,
    -- Helbred — krypteret (GDPR Art. 9)
    -- Kryptér ved skriv: pgp_sym_encrypt(data, current_setting('app.encryption_key'))
    -- Dekryptér ved læs: pgp_sym_decrypt(helbredsnoter_enc, current_setting('app.encryption_key'))
    -- Returneres ALDRIG i listevisninger — kun via dedikeret endpoint med auditlog.
    helbredsnoter_enc BYTEA,
    -- Status og matching
    status            menneske_status NOT NULL DEFAULT 'ny',
    matched_with      UUID           REFERENCES brobyggere(id) ON DELETE SET NULL,
    matched_at        TIMESTAMPTZ,
    forloeb_startet_at TIMESTAMPTZ,
    forloeb_afsluttet_at TIMESTAMPTZ,
    afslutning_note   TEXT,
    -- Koordinator og kontor
    raadgiver_id      UUID           REFERENCES brugere(id) ON DELETE SET NULL,
    hq                TEXT,
    -- GDPR: blødt slet — anonymiseres 30 dage efter deleted_at
    created_at        TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    deleted_at        TIMESTAMPTZ,
    anonymized_at     TIMESTAMPTZ
);

CREATE INDEX idx_mennesker_status        ON mennesker(status);
CREATE INDEX idx_mennesker_matched_with  ON mennesker(matched_with) WHERE matched_with IS NOT NULL;
CREATE INDEX idx_mennesker_raadgiver     ON mennesker(raadgiver_id) WHERE raadgiver_id IS NOT NULL;
CREATE INDEX idx_mennesker_hq            ON mennesker(hq) WHERE hq IS NOT NULL;
CREATE INDEX idx_mennesker_aktive        ON mennesker(status, created_at)
    WHERE deleted_at IS NULL AND status NOT IN ('afsluttet');
CREATE INDEX idx_mennesker_ikke_slettet  ON mennesker(deleted_at)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_mennesker_ventende      ON mennesker(status, created_at)
    WHERE status IN ('ny', 'venteliste') AND matched_with IS NULL AND deleted_at IS NULL;

CREATE TRIGGER trg_mennesker_updated
    BEFORE UPDATE ON mennesker
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =============================================================================
-- TABEL: aftaler
-- Planlagte og afholdte møder/aktiviteter.
-- =============================================================================

CREATE TABLE aftaler (
    id           UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    brobygger_id UUID          NOT NULL REFERENCES brobyggere(id) ON DELETE CASCADE,
    menneske_id  UUID          NOT NULL REFERENCES mennesker(id)  ON DELETE CASCADE,
    dato         TIMESTAMPTZ   NOT NULL,
    varighed     INTEGER       NOT NULL DEFAULT 60 CHECK (varighed >= 5),  -- minutter
    type         aftale_type   NOT NULL DEFAULT 'moede',
    sted         TEXT,
    beskrivelse  TEXT,
    status       aftale_status NOT NULL DEFAULT 'planlagt',
    notes        TEXT          NOT NULL DEFAULT '',
    created_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    -- Bagudkompatibilitet: reference til HQ
    hq           TEXT
);

CREATE INDEX idx_aftaler_brobygger  ON aftaler(brobygger_id);
CREATE INDEX idx_aftaler_menneske   ON aftaler(menneske_id);
CREATE INDEX idx_aftaler_dato       ON aftaler(dato DESC);
CREATE INDEX idx_aftaler_status     ON aftaler(status);
CREATE INDEX idx_aftaler_uge        ON aftaler(date_trunc('week', dato), status);
CREATE INDEX idx_aftaler_planlagte  ON aftaler(dato, brobygger_id)
    WHERE status = 'planlagt';

CREATE TRIGGER trg_aftaler_updated
    BEFORE UPDATE ON aftaler
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =============================================================================
-- TABEL: kontakt_log
-- Løbende kontaktregistrering — brobyggere og rådgivere logger al kontakt.
-- =============================================================================

CREATE TABLE kontakt_log (
    id                 UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    menneske_id        UUID         NOT NULL REFERENCES mennesker(id) ON DELETE CASCADE,
    brobygger_id       UUID         REFERENCES brobyggere(id) ON DELETE SET NULL,
    oprettet_af_id     UUID         REFERENCES brugere(id) ON DELETE SET NULL,
    type               kontakt_type NOT NULL,
    dato               DATE         NOT NULL DEFAULT CURRENT_DATE,
    varighed_minutter  INTEGER      CHECK (varighed_minutter IS NULL OR varighed_minutter >= 0),
    notat              TEXT,
    naeste_skridt      TEXT,
    created_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_kontaktlog_menneske   ON kontakt_log(menneske_id, dato DESC);
CREATE INDEX idx_kontaktlog_brobygger  ON kontakt_log(brobygger_id) WHERE brobygger_id IS NOT NULL;
CREATE INDEX idx_kontaktlog_dato       ON kontakt_log(dato DESC);
CREATE INDEX idx_kontaktlog_type       ON kontakt_log(type);

CREATE TRIGGER trg_kontaktlog_updated
    BEFORE UPDATE ON kontakt_log
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =============================================================================
-- TABEL: besked_traade
-- Interne beskedtråde mellem brobyggere og rådgivere.
-- =============================================================================

CREATE TABLE besked_traade (
    id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    titel          TEXT        NOT NULL,
    brobygger_id   UUID        REFERENCES brobyggere(id) ON DELETE SET NULL,
    from_brobygger BOOLEAN     NOT NULL DEFAULT FALSE,
    official       BOOLEAN     NOT NULL DEFAULT FALSE,
    ulaest_count   INTEGER     NOT NULL DEFAULT 0 CHECK (ulaest_count >= 0),
    sidste_besked  TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_traade_brobygger ON besked_traade(brobygger_id) WHERE brobygger_id IS NOT NULL;
CREATE INDEX idx_traade_updated   ON besked_traade(updated_at DESC);
CREATE INDEX idx_traade_official  ON besked_traade(official) WHERE official = TRUE;

CREATE TRIGGER trg_traade_updated
    BEFORE UPDATE ON besked_traade
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- =============================================================================
-- TABEL: beskeder
-- Individuelle beskeder i tråde.
-- =============================================================================

CREATE TABLE beskeder (
    id             UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    traad_id       UUID         NOT NULL REFERENCES besked_traade(id) ON DELETE CASCADE,
    from_rolle     bruger_rolle NOT NULL,
    fra_bruger_id  UUID         REFERENCES brugere(id) ON DELETE SET NULL,
    tekst          TEXT         NOT NULL,
    sent_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    laest_af       UUID[]       NOT NULL DEFAULT '{}',  -- array af bruger-UUIDs
    signalr_msg_id TEXT         -- Azure SignalR correlation ID
);

CREATE INDEX idx_beskeder_traad   ON beskeder(traad_id, sent_at ASC);
CREATE INDEX idx_beskeder_sent_at ON beskeder(sent_at DESC);
CREATE INDEX idx_beskeder_bruger  ON beskeder(fra_bruger_id) WHERE fra_bruger_id IS NOT NULL;


-- =============================================================================
-- TABEL: notifikationer
-- In-app notifikationer til brugere. Knyttes til Web Push via push_subscriptions.
-- =============================================================================

CREATE TABLE notifikationer (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    bruger_id     UUID        NOT NULL REFERENCES brugere(id) ON DELETE CASCADE,
    type          notif_type  NOT NULL,
    titel         TEXT        NOT NULL,
    tekst         TEXT        NOT NULL,
    link          TEXT,                              -- Navigation-target i appen
    unread        BOOLEAN     NOT NULL DEFAULT TRUE,
    push_sendt    BOOLEAN     NOT NULL DEFAULT FALSE,
    push_sendt_at TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notif_bruger       ON notifikationer(bruger_id, created_at DESC);
CREATE INDEX idx_notif_ulaest       ON notifikationer(bruger_id, unread)
    WHERE unread = TRUE;
CREATE INDEX idx_notif_push_pending ON notifikationer(push_sendt, created_at)
    WHERE push_sendt = FALSE;


-- =============================================================================
-- TABEL: push_subscriptions
-- Web Push VAPID-subscriptions per bruger/enhed.
-- =============================================================================

CREATE TABLE push_subscriptions (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    bruger_id    UUID        NOT NULL REFERENCES brugere(id) ON DELETE CASCADE,
    endpoint     TEXT        NOT NULL UNIQUE,
    p256dh       TEXT        NOT NULL,
    auth_key     TEXT        NOT NULL,
    user_agent   TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at TIMESTAMPTZ
);

CREATE INDEX idx_push_bruger ON push_subscriptions(bruger_id);


-- =============================================================================
-- TABEL: samtykker
-- GDPR Art. 6 (kontaktdata) og Art. 9 (helbredsdata) samtykker.
-- =============================================================================

CREATE TABLE samtykker (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    menneske_id      UUID        NOT NULL REFERENCES mennesker(id) ON DELETE CASCADE,
    version          TEXT        NOT NULL,          -- fx "2025-01-01"
    givet_af         TEXT,                          -- Navn på koordinator der indhentede
    helbredsdata     BOOLEAN     NOT NULL DEFAULT FALSE,  -- Art. 9
    kontakt_data     BOOLEAN     NOT NULL DEFAULT TRUE,   -- Art. 6
    ip_adresse       TEXT,
    enhed            TEXT,                          -- User-agent
    trukket_tilbage  BOOLEAN     NOT NULL DEFAULT FALSE,
    trukket_at       TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_samtykke_menneske ON samtykker(menneske_id);
CREATE INDEX idx_samtykke_version  ON samtykker(version);
CREATE INDEX idx_samtykke_aktivt   ON samtykker(menneske_id, helbredsdata)
    WHERE trukket_tilbage = FALSE;


-- =============================================================================
-- TABEL: invitations
-- Magic-link/email-invitations til nye brugere.
-- =============================================================================

CREATE TABLE invitations (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    email       TEXT        NOT NULL,
    navn        TEXT        NOT NULL,
    hq          TEXT,
    rolle       bruger_rolle NOT NULL DEFAULT 'Brobygger',
    token_hash  TEXT        NOT NULL UNIQUE,  -- sha256 af det signerede token
    sendt_af    UUID        REFERENCES brugere(id) ON DELETE SET NULL,
    expires_at  TIMESTAMPTZ NOT NULL,
    brugt       BOOLEAN     NOT NULL DEFAULT FALSE,
    brugt_at    TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_invitations_email   ON invitations(email);
CREATE INDEX idx_invitations_aktive  ON invitations(expires_at, brugt)
    WHERE NOT brugt;


-- =============================================================================
-- TABEL: encryption_key_log
-- Compliance-log over krypteringsnøgle-rotationer.
-- =============================================================================

CREATE TABLE encryption_key_log (
    id          SERIAL      PRIMARY KEY,
    roteret_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    roteret_af  UUID        REFERENCES brugere(id) ON DELETE SET NULL,
    note        TEXT
);


-- =============================================================================
-- TABEL: audit_log
-- Automatisk auditlog over alle ændringer i følsomme tabeller.
-- Populated via trigger-funktion nedenfor.
-- =============================================================================

CREATE TABLE audit_log (
    id          BIGSERIAL   PRIMARY KEY,
    tidspunkt   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    bruger_id   UUID        REFERENCES brugere(id) ON DELETE SET NULL,
    azure_oid   TEXT,                              -- Backup hvis FK fejler
    handling    TEXT        NOT NULL,              -- INSERT, UPDATE, DELETE
    tabel       TEXT        NOT NULL,
    rekord_id   UUID        NOT NULL,
    aendringer  JSONB,                             -- { old: {...}, new: {...} }
    ip_adresse  TEXT,
    user_agent  TEXT
);

CREATE INDEX idx_audit_tidspunkt ON audit_log(tidspunkt DESC);
CREATE INDEX idx_audit_rekord    ON audit_log(tabel, rekord_id);
CREATE INDEX idx_audit_bruger    ON audit_log(bruger_id) WHERE bruger_id IS NOT NULL;


-- =============================================================================
-- TRIGGER: row-level audit
-- Logges på: mennesker, aftaler, kontakt_log, samtykker, brugere
-- Bruger session-variabel 'app.current_user_id' sat af API-laget
-- =============================================================================

CREATE OR REPLACE FUNCTION audit_changes()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER AS $$
DECLARE
    v_bruger_id UUID;
    v_azure_oid TEXT;
BEGIN
    -- Forsøg at hente aktuel bruger fra session-variabel (sat af FastAPI)
    BEGIN
        v_bruger_id := current_setting('app.current_user_id', TRUE)::UUID;
    EXCEPTION WHEN others THEN
        v_bruger_id := NULL;
    END;

    BEGIN
        v_azure_oid := current_setting('app.current_azure_oid', TRUE);
    EXCEPTION WHEN others THEN
        v_azure_oid := NULL;
    END;

    INSERT INTO audit_log (
        bruger_id,
        azure_oid,
        handling,
        tabel,
        rekord_id,
        aendringer,
        ip_adresse,
        user_agent
    ) VALUES (
        v_bruger_id,
        v_azure_oid,
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        jsonb_build_object(
            'old', CASE WHEN TG_OP = 'INSERT' THEN NULL ELSE row_to_json(OLD) END,
            'new', CASE WHEN TG_OP = 'DELETE' THEN NULL ELSE row_to_json(NEW) END
        ),
        current_setting('app.client_ip', TRUE),
        current_setting('app.user_agent', TRUE)
    );

    RETURN COALESCE(NEW, OLD);
END;
$$;

-- Audit triggers for følsomme tabeller
CREATE TRIGGER audit_mennesker
    AFTER INSERT OR UPDATE OR DELETE ON mennesker
    FOR EACH ROW EXECUTE FUNCTION audit_changes();

CREATE TRIGGER audit_aftaler
    AFTER INSERT OR UPDATE OR DELETE ON aftaler
    FOR EACH ROW EXECUTE FUNCTION audit_changes();

CREATE TRIGGER audit_kontaktlog
    AFTER INSERT OR UPDATE OR DELETE ON kontakt_log
    FOR EACH ROW EXECUTE FUNCTION audit_changes();

CREATE TRIGGER audit_samtykker
    AFTER INSERT OR UPDATE ON samtykker
    FOR EACH ROW EXECUTE FUNCTION audit_changes();

CREATE TRIGGER audit_brugere
    AFTER INSERT OR UPDATE OR DELETE ON brugere
    FOR EACH ROW EXECUTE FUNCTION audit_changes();


-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- Brobyggere kan kun se egne aftaler, kontaktlog-entries og eget menneske.
-- Rådgivere og admins ser alt inden for eget HQ (håndhæves i API-laget).
--
-- Forudsætning: FastAPI sætter session-variabler ved hvert API-kald:
--   SET LOCAL app.current_user_id  = '<bruger-uuid>';
--   SET LOCAL app.current_rolle    = 'Brobygger';   -- eller Raadgiver/Admin
--   SET LOCAL app.current_hq       = 'København N'; -- eller NULL
-- =============================================================================

ALTER TABLE aftaler ENABLE ROW LEVEL SECURITY;

CREATE POLICY rls_aftaler ON aftaler
    USING (
        current_setting('app.current_rolle', TRUE) IN ('Admin', 'Raadgiver')
        OR brobygger_id IN (
            SELECT id FROM brobyggere
            WHERE azure_oid = current_setting('app.current_azure_oid', TRUE)
               OR bruger_id::TEXT = current_setting('app.current_user_id', TRUE)
        )
    );

ALTER TABLE kontakt_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY rls_kontaktlog ON kontakt_log
    USING (
        current_setting('app.current_rolle', TRUE) IN ('Admin', 'Raadgiver')
        OR brobygger_id IN (
            SELECT id FROM brobyggere
            WHERE azure_oid = current_setting('app.current_azure_oid', TRUE)
               OR bruger_id::TEXT = current_setting('app.current_user_id', TRUE)
        )
        OR oprettet_af_id::TEXT = current_setting('app.current_user_id', TRUE)
    );

ALTER TABLE mennesker ENABLE ROW LEVEL SECURITY;

CREATE POLICY rls_mennesker ON mennesker
    USING (
        deleted_at IS NULL
        AND (
            current_setting('app.current_rolle', TRUE) IN ('Admin', 'Raadgiver')
            OR matched_with IN (
                SELECT id FROM brobyggere
                WHERE azure_oid = current_setting('app.current_azure_oid', TRUE)
                   OR bruger_id::TEXT = current_setting('app.current_user_id', TRUE)
            )
        )
    );


-- =============================================================================
-- HJÆLPEFUNKTIONER
-- =============================================================================

-- Anonymisér slettede mennesker (kørsel: månedligt cron-job)
CREATE OR REPLACE FUNCTION anonymiser_slettede_mennesker()
RETURNS INTEGER
LANGUAGE plpgsql AS $$
DECLARE
    antal INTEGER;
BEGIN
    UPDATE mennesker SET
        navn              = 'Anonymiseret',
        email             = NULL,
        telefon           = NULL,
        adresse           = NULL,
        helbredsnoter_enc = NULL,
        noter             = NULL,
        alder             = NULL,
        kon               = NULL,
        anonymized_at     = NOW()
    WHERE
        deleted_at IS NOT NULL
        AND deleted_at < NOW() - INTERVAL '30 days'
        AND anonymized_at IS NULL;

    GET DIAGNOSTICS antal = ROW_COUNT;
    RETURN antal;
END;
$$;

-- Ryd gammel audit-log (bevar 5 år per Datatilsynets vejledning)
CREATE OR REPLACE FUNCTION ryd_gammel_audit()
RETURNS INTEGER
LANGUAGE plpgsql AS $$
DECLARE
    antal INTEGER;
BEGIN
    DELETE FROM audit_log WHERE tidspunkt < NOW() - INTERVAL '5 years';
    GET DIAGNOSTICS antal = ROW_COUNT;
    RETURN antal;
END;
$$;

-- Ryd udløbne invitations
CREATE OR REPLACE FUNCTION ryd_udloebne_invitations()
RETURNS INTEGER
LANGUAGE plpgsql AS $$
DECLARE
    antal INTEGER;
BEGIN
    DELETE FROM invitations WHERE expires_at < NOW() AND NOT brugt;
    GET DIAGNOSTICS antal = ROW_COUNT;
    RETURN antal;
END;
$$;

-- Opdatér brobygger.active ved match-ændringer (tæller aktive mennesker)
CREATE OR REPLACE FUNCTION sync_brobygger_active_count()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    -- Hvis matched_with er ændret, genberegn active for berørte brobyggere
    IF TG_OP = 'UPDATE' THEN
        IF OLD.matched_with IS DISTINCT FROM NEW.matched_with THEN
            -- Dekrementér den gamle brobygger
            IF OLD.matched_with IS NOT NULL THEN
                UPDATE brobyggere
                SET active = GREATEST(0, (
                    SELECT COUNT(*) FROM mennesker
                    WHERE matched_with = OLD.matched_with
                      AND status IN ('matched', 'aktiv')
                      AND deleted_at IS NULL
                ))
                WHERE id = OLD.matched_with;
            END IF;
            -- Opdatér den nye brobygger
            IF NEW.matched_with IS NOT NULL THEN
                UPDATE brobyggere
                SET active = (
                    SELECT COUNT(*) FROM mennesker
                    WHERE matched_with = NEW.matched_with
                      AND status IN ('matched', 'aktiv')
                      AND deleted_at IS NULL
                )
                WHERE id = NEW.matched_with;
            END IF;
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_sync_brobygger_active
    AFTER UPDATE ON mennesker
    FOR EACH ROW EXECUTE FUNCTION sync_brobygger_active_count();

-- Opdatér besked_traade.ulaest_count og sidste_besked ved ny besked
CREATE OR REPLACE FUNCTION sync_traad_ved_ny_besked()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE besked_traade SET
        sidste_besked = LEFT(NEW.tekst, 120),
        ulaest_count  = ulaest_count + 1,
        updated_at    = NOW()
    WHERE id = NEW.traad_id;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_besked_til_traad
    AFTER INSERT ON beskeder
    FOR EACH ROW EXECUTE FUNCTION sync_traad_ved_ny_besked();


-- =============================================================================
-- VIEWS
-- =============================================================================

-- Aktive brobyggere med kapacitetsinfo
CREATE VIEW v_active_brobyggere AS
SELECT
    b.*,
    (b.max_active - b.active) AS ledig_kapacitet,
    (b.active < b.max_active AND b.status = 'aktiv') AS har_kapacitet,
    COALESCE(br.email, b.email)       AS login_email,
    COALESCE(br.azure_oid, b.azure_oid) AS oid
FROM brobyggere b
LEFT JOIN brugere br ON br.id = b.bruger_id
WHERE b.status NOT IN ('inaktiv');

-- Umatchede mennesker klar til matching (bruges af matching-endpoint)
CREATE VIEW v_unmatched_mennesker AS
SELECT
    m.*,
    br.display_name AS raadgiver_navn,
    br.email        AS raadgiver_email,
    EXTRACT(DAY FROM NOW() - m.created_at)::INTEGER AS dage_ventet
FROM mennesker m
LEFT JOIN brugere br ON br.id = m.raadgiver_id
WHERE m.status IN ('ny', 'venteliste')
  AND m.matched_with IS NULL
  AND m.deleted_at IS NULL
ORDER BY m.created_at ASC;

-- Ugeoversigt (alle aftaler i løbende uge)
CREATE VIEW v_uge_oversigt AS
SELECT
    a.id,
    a.dato,
    a.varighed,
    a.type,
    a.sted,
    a.status,
    a.notes,
    a.brobygger_id,
    b.navn  AS brobygger_navn,
    b.hq    AS hq,
    a.menneske_id,
    m.navn  AS menneske_navn,
    date_trunc('week', a.dato AT TIME ZONE 'Europe/Copenhagen')::DATE AS uge_start,
    EXTRACT(WEEK  FROM a.dato AT TIME ZONE 'Europe/Copenhagen')::INTEGER AS uge_nr,
    EXTRACT(YEAR  FROM a.dato AT TIME ZONE 'Europe/Copenhagen')::INTEGER AS aar
FROM aftaler a
JOIN brobyggere b ON b.id = a.brobygger_id
JOIN mennesker  m ON m.id = a.menneske_id
WHERE a.dato >= date_trunc('week', NOW() AT TIME ZONE 'Europe/Copenhagen')
  AND a.dato <  date_trunc('week', NOW() AT TIME ZONE 'Europe/Copenhagen') + INTERVAL '7 days';

-- Dashboard KPI (bruges af /v1/rapporter/dashboard)
CREATE VIEW v_dashboard_kpi AS
SELECT
    -- Brobyggere
    COUNT(DISTINCT b.id) FILTER (WHERE b.status = 'aktiv')
        AS aktive_brobyggere,
    COUNT(DISTINCT b.id) FILTER (WHERE b.status = 'aktiv' AND b.active < b.max_active)
        AS ledige_brobyggere,
    -- Mennesker
    COUNT(DISTINCT m.id) FILTER (WHERE m.status = 'aktiv' AND m.deleted_at IS NULL)
        AS aktive_mennesker,
    COUNT(DISTINCT m.id) FILTER (WHERE m.status IN ('ny', 'venteliste') AND m.matched_with IS NULL AND m.deleted_at IS NULL)
        AS ventende_mennesker,
    -- Aftaler
    COUNT(DISTINCT a_uge.id)
        AS planlagte_aftaler_denne_uge,
    COUNT(DISTINCT a_dag.id)
        AS aftaler_i_dag,
    -- Match-rate (pct. af alle aktive/matchede ud af alle ikke-slettede)
    ROUND(
        100.0 * COUNT(DISTINCT m.id) FILTER (WHERE m.status IN ('matched', 'aktiv') AND m.deleted_at IS NULL)
        / NULLIF(COUNT(DISTINCT m.id) FILTER (WHERE m.deleted_at IS NULL), 0),
        1
    ) AS match_rate
FROM brobyggere b
CROSS JOIN mennesker m
LEFT JOIN aftaler a_uge ON a_uge.status = 'planlagt'
    AND a_uge.dato >= date_trunc('week', NOW() AT TIME ZONE 'Europe/Copenhagen')
    AND a_uge.dato <  date_trunc('week', NOW() AT TIME ZONE 'Europe/Copenhagen') + INTERVAL '7 days'
LEFT JOIN aftaler a_dag ON a_dag.status = 'planlagt'
    AND a_dag.dato::DATE = (NOW() AT TIME ZONE 'Europe/Copenhagen')::DATE;

-- Aktiv kontaktlog per menneske (nyeste entry pr. menneske)
CREATE VIEW v_seneste_kontakt AS
SELECT DISTINCT ON (k.menneske_id)
    k.menneske_id,
    k.id            AS kontakt_id,
    k.dato          AS seneste_dato,
    k.type          AS seneste_type,
    k.notat,
    k.naeste_skridt,
    b.navn          AS brobygger_navn,
    m.navn          AS menneske_navn
FROM kontakt_log k
JOIN mennesker   m ON m.id = k.menneske_id
LEFT JOIN brobyggere b ON b.id = k.brobygger_id
WHERE m.deleted_at IS NULL
ORDER BY k.menneske_id, k.dato DESC;


-- =============================================================================
-- SEED DATA — Testdata til lokal udvikling og staging
-- =============================================================================

-- Ryd eksisterende testdata (idempotent)
DO $$
BEGIN
    -- Sæt RLS-bypass for seed-kørsel
    PERFORM set_config('app.current_rolle', 'Admin', TRUE);
END;
$$;

-- Fjern afhængigheder i rækkefølge
TRUNCATE TABLE
    audit_log,
    encryption_key_log,
    samtykker,
    invitations,
    push_subscriptions,
    notifikationer,
    beskeder,
    besked_traade,
    kontakt_log,
    aftaler,
    mennesker,
    brobyggere,
    brugere
RESTART IDENTITY CASCADE;


-- ── Brugere (rådgivere og admins) ──────────────────────────────────────────

INSERT INTO brugere (id, azure_oid, display_name, email, rolle, hq) VALUES
    ('00000000-0001-0000-0000-000000000000',
     'ENTRA_OID_LINDA',     'Linda Sørensen',    'linda@sos.dk',   'Raadgiver', 'København N'),
    ('00000000-0002-0000-0000-000000000000',
     'ENTRA_OID_ADMIN',     'Admin SoS',          'admin@sos.dk',   'Admin',     NULL),
    ('00000000-0003-0000-0000-000000000000',
     'ENTRA_OID_HANNE',     'Hanne Vestergaard',  'hanne@sos.dk',   'Raadgiver', 'Aarhus C');


-- ── Brobyggere ──────────────────────────────────────────────────────────────

INSERT INTO brobyggere (id, azure_oid, navn, email, telefon, typer, sprog, hq, status, active, max_active, startdato, naeste_tid) VALUES
    ('b0000000-0001-0000-0000-000000000000',
     'ENTRA_OID_MAJA',
     'Maja Lindberg',       'maja@example.com',       '+45 28 11 22 33',
     ARRAY['en-til-en', 'cafe-gruppe'],    ARRAY['dansk', 'engelsk'],
     'København N', 'aktiv', 2, 3, '2023-09-01', 'Tirsdag kl. 14-16'),

    ('b0000000-0002-0000-0000-000000000000',
     NULL,
     'Thomas Eriksen',      'thomas@example.com',     '+45 40 55 66 77',
     ARRAY['en-til-en'],                  ARRAY['dansk'],
     'Aarhus C',    'aktiv', 1, 2, '2022-06-15', 'Torsdag kl. 09-11'),

    ('b0000000-0003-0000-0000-000000000000',
     NULL,
     'Amira Osman',         'amira@example.com',      '+45 51 88 99 00',
     ARRAY['en-til-en', 'netvaerk'],      ARRAY['dansk', 'arabisk', 'engelsk'],
     'København S', 'aktiv', 3, 3, '2023-01-20', 'Mandag kl. 10-12'),

    ('b0000000-0004-0000-0000-000000000000',
     NULL,
     'Peter Nørgaard',      'peter@example.com',      '+45 26 33 44 55',
     ARRAY['gruppe', 'cafe-gruppe'],      ARRAY['dansk'],
     'Odense C',    'pause', 0, 4, '2021-11-01', NULL),

    ('b0000000-0005-0000-0000-000000000000',
     NULL,
     'Sara Christoffersen', 'sara@example.com',       '+45 61 22 33 44',
     ARRAY['en-til-en'],                  ARRAY['dansk', 'tysk'],
     'København N', 'aktiv', 1, 3, '2024-02-01', 'Onsdag kl. 13-15');


-- ── Mennesker ───────────────────────────────────────────────────────────────

INSERT INTO mennesker (id, navn, alder, typer, sprog, status, matched_with, matched_at, hq, raadgiver_id) VALUES
    ('m0000000-0001-0000-0000-000000000000',
     'Ahmad K.', 38,
     ARRAY['en-til-en'],              ARRAY['arabisk', 'dansk'],
     'aktiv', 'b0000000-0001-0000-0000-000000000000', NOW() - INTERVAL '45 days',
     'København N', '00000000-0001-0000-0000-000000000000'),

    ('m0000000-0002-0000-0000-000000000000',
     'Sofie B.', 27,
     ARRAY['en-til-en', 'netvaerk'],  ARRAY['dansk'],
     'aktiv', 'b0000000-0005-0000-0000-000000000000', NOW() - INTERVAL '20 days',
     'København N', '00000000-0001-0000-0000-000000000000'),

    ('m0000000-0003-0000-0000-000000000000',
     'Yusuf M.', 45,
     ARRAY['cafe-gruppe'],            ARRAY['arabisk', 'dansk'],
     'ny', NULL, NULL,
     'Aarhus C', '00000000-0003-0000-0000-000000000000'),

    ('m0000000-0004-0000-0000-000000000000',
     'Maria T.', 31,
     ARRAY['en-til-en'],              ARRAY['dansk', 'polsk'],
     'venteliste', NULL, NULL,
     'København S', '00000000-0001-0000-0000-000000000000'),

    ('m0000000-0005-0000-0000-000000000000',
     'Lars H.', 52,
     ARRAY['gruppe'],                 ARRAY['dansk'],
     'matched', 'b0000000-0002-0000-0000-000000000000', NOW() - INTERVAL '7 days',
     'Aarhus C', '00000000-0003-0000-0000-000000000000');

-- Registrér samtykker for alle mennesker
INSERT INTO samtykker (menneske_id, version, givet_af, kontakt_data, helbredsdata) VALUES
    ('m0000000-0001-0000-0000-000000000000', '2025-01-01', 'Linda Sørensen',    TRUE, TRUE),
    ('m0000000-0002-0000-0000-000000000000', '2025-01-01', 'Linda Sørensen',    TRUE, FALSE),
    ('m0000000-0003-0000-0000-000000000000', '2025-01-01', 'Hanne Vestergaard', TRUE, FALSE),
    ('m0000000-0004-0000-0000-000000000000', '2025-01-01', 'Linda Sørensen',    TRUE, FALSE),
    ('m0000000-0005-0000-0000-000000000000', '2025-01-01', 'Hanne Vestergaard', TRUE, FALSE);


-- ── Aftaler ─────────────────────────────────────────────────────────────────

INSERT INTO aftaler (id, brobygger_id, menneske_id, dato, varighed, type, sted, status, notes) VALUES
    ('a0000000-0001-0000-0000-000000000000',
     'b0000000-0001-0000-0000-000000000000', 'm0000000-0001-0000-0000-000000000000',
     NOW() + INTERVAL '1 day',  60, 'moede',        'Cafe Nørreport',       'planlagt',    ''),

    ('a0000000-0002-0000-0000-000000000000',
     'b0000000-0001-0000-0000-000000000000', 'm0000000-0001-0000-0000-000000000000',
     NOW() - INTERVAL '7 days', 90, 'aktivitet',    'Fælledparken',         'gennemfoert', 'God tur. Ahmad var i godt humør og åbnede sig mere.'),

    ('a0000000-0003-0000-0000-000000000000',
     'b0000000-0005-0000-0000-000000000000', 'm0000000-0002-0000-0000-000000000000',
     NOW() + INTERVAL '3 days', 60, 'telefonopkald', NULL,                  'planlagt',    ''),

    ('a0000000-0004-0000-0000-000000000000',
     'b0000000-0002-0000-0000-000000000000', 'm0000000-0005-0000-0000-000000000000',
     NOW() - INTERVAL '14 days',120,'moede',         'Biblioteket Aarhus',  'gennemfoert', 'Første møde. Lars virkede nervøs men interesseret.'),

    ('a0000000-0005-0000-0000-000000000000',
     'b0000000-0003-0000-0000-000000000000', 'm0000000-0001-0000-0000-000000000000',
     NOW() - INTERVAL '30 days', 60,'moede',         'SoS kontor',          'aflyst',      'Ahmad afbød pga. sygdom.');


-- ── Kontaktlog ──────────────────────────────────────────────────────────────

INSERT INTO kontakt_log (id, menneske_id, brobygger_id, oprettet_af_id, type, dato, varighed_minutter, notat, naeste_skridt) VALUES
    ('k0000000-0001-0000-0000-000000000000',
     'm0000000-0001-0000-0000-000000000000',
     'b0000000-0001-0000-0000-000000000000',
     NULL,
     'moede_brobygger',
     CURRENT_DATE - 7, 90,
     'God tur i Fælledparken. Ahmad talte om sine interesser og nød frisk luft.',
     'Planlæg næste møde på cafe'),

    ('k0000000-0002-0000-0000-000000000000',
     'm0000000-0001-0000-0000-000000000000',
     'b0000000-0001-0000-0000-000000000000',
     NULL,
     'telefonisk',
     CURRENT_DATE - 14, 15,
     'Hurtig opringning for at bekræfte næste møde. Ahmad er positiv.',
     NULL),

    ('k0000000-0003-0000-0000-000000000000',
     'm0000000-0002-0000-0000-000000000000',
     'b0000000-0005-0000-0000-000000000000',
     NULL,
     'moede_brobygger',
     CURRENT_DATE - 10, 60,
     'Sofie og Sara mødtes på biblioteket. Sofie er meget engageret i at finde en jobklub.',
     'Undersøg muligheder for jobklub i København N'),

    ('k0000000-0004-0000-0000-000000000000',
     'm0000000-0005-0000-0000-000000000000',
     'b0000000-0002-0000-0000-000000000000',
     NULL,
     'moede_brobygger',
     CURRENT_DATE - 14, 120,
     'Første møde med Lars på biblioteket. Han er interesseret i kulturelle arrangementer.',
     'Tag med til et arrangement næste måned'),

    ('k0000000-0005-0000-0000-000000000000',
     'm0000000-0003-0000-0000-000000000000',
     NULL,
     '00000000-0003-0000-0000-000000000000',
     'notat',
     CURRENT_DATE - 3, NULL,
     'Yusuf Murat er ny henvendelse. Søger cafe-gruppe. Taler arabisk og lidt dansk. Henvist af socialrådgiver.',
     'Find egnet cafe-gruppe og brobygger med arabisk'),

    ('k0000000-0006-0000-0000-000000000000',
     'm0000000-0001-0000-0000-000000000000',
     NULL,
     '00000000-0001-0000-0000-000000000000',
     'notat',
     CURRENT_DATE - 45, NULL,
     'Ahmad Hassan henvist via jobcenter. Ønsker én-til-én brobygning. Taler arabisk og dansk.',
     'Match med brobygger med arabisk sprogkompetence');


-- ── Beskedtråde og beskeder ─────────────────────────────────────────────────

INSERT INTO besked_traade (id, titel, brobygger_id, from_brobygger, official, ulaest_count, sidste_besked) VALUES
    ('t0000000-0001-0000-0000-000000000000',
     'Nyhedsbrev — maj 2026', NULL, FALSE, TRUE, 0,
     'Kære alle — her er nyheder fra maj...'),

    ('t0000000-0002-0000-0000-000000000000',
     'Frivilligkursus 14. juni', NULL, FALSE, TRUE, 1,
     'Husk tilmelding til frivilligkurset senest fredag.'),

    ('t0000000-0003-0000-0000-000000000000',
     'Spørgsmål til Linda',
     'b0000000-0001-0000-0000-000000000000', TRUE, FALSE, 0,
     'Selvfølgelig! Ring til mig i morgen formiddag.');

INSERT INTO beskeder (traad_id, from_rolle, fra_bruger_id, tekst, sent_at) VALUES
    ('t0000000-0001-0000-0000-000000000000',
     'Raadgiver', '00000000-0001-0000-0000-000000000000',
     'Kære alle — her er nyheder fra maj. Vi har fået 3 nye frivillige og 5 nye borgere i forløb. Fantastisk arbejde!',
     NOW() - INTERVAL '5 days'),

    ('t0000000-0002-0000-0000-000000000000',
     'Raadgiver', '00000000-0001-0000-0000-000000000000',
     'Husk tilmelding til frivilligkurset senest på fredag. Svar på denne besked hvis du deltager.',
     NOW() - INTERVAL '2 days'),

    ('t0000000-0003-0000-0000-000000000000',
     'Brobygger', NULL,
     'Hej Linda, jeg er lidt i tvivl om næste møde med Ahmad. Har du tid til en snak i morgen?',
     NOW() - INTERVAL '25 hours'),

    ('t0000000-0003-0000-0000-000000000000',
     'Raadgiver', '00000000-0001-0000-0000-000000000000',
     'Selvfølgelig! Ring til mig i morgen formiddag mellem 9 og 11.',
     NOW() - INTERVAL '23 hours');


-- ── Notifikationer ──────────────────────────────────────────────────────────

INSERT INTO notifikationer (id, bruger_id, type, titel, tekst, unread, link) VALUES
    ('n0000000-0001-0000-0000-000000000000',
     '00000000-0001-0000-0000-000000000000',
     'ny_aftale', 'Ny aftale oprettet',
     'Ahmad K.: Møde på Cafe Nørreport i morgen kl. 14',
     TRUE, '/kalender'),

    ('n0000000-0002-0000-0000-000000000000',
     '00000000-0001-0000-0000-000000000000',
     'ny_besked', 'Ny besked fra Maja',
     'Maja spørger om næste møde med Ahmad',
     TRUE, '/beskeder'),

    ('n0000000-0003-0000-0000-000000000000',
     '00000000-0001-0000-0000-000000000000',
     'system', 'Frivilligkursus 14. juni',
     'Tilmeld dig senest på fredag',
     FALSE, '/beskeder'),

    ('n0000000-0004-0000-0000-000000000000',
     '00000000-0003-0000-0000-000000000000',
     'match_forslag', 'Ny borger klar til matching',
     'Yusuf M. søger cafe-gruppe med arabisk. 3 brobyggere matcher.',
     TRUE, '/matching');


-- =============================================================================
-- AFSLUTNING
-- =============================================================================

-- Verificér seed
DO $$
DECLARE
    b_count INTEGER;
    m_count INTEGER;
    a_count INTEGER;
    k_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO b_count FROM brobyggere;
    SELECT COUNT(*) INTO m_count FROM mennesker;
    SELECT COUNT(*) INTO a_count FROM aftaler;
    SELECT COUNT(*) INTO k_count FROM kontakt_log;
    RAISE NOTICE 'Seed fuldført: % brobyggere, % mennesker, % aftaler, % kontaktlog-entries',
        b_count, m_count, a_count, k_count;
END;
$$;
