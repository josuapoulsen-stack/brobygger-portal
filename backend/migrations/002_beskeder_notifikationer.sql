-- =============================================================================
-- Migration 002 — Beskeder, notifikationer og Web Push-subscriptions
-- Kræver: 001_initial_schema.sql
-- =============================================================================

-- =============================================================================
-- BESKEDTRÅDE
-- =============================================================================

CREATE TABLE besked_traade (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    titel           TEXT NOT NULL,
    brobygger_id    UUID REFERENCES brobyggere(id),
    -- Beskedtyper: officiel info fra koordinator, eller brobygger→koordinator
    from_brobygger  BOOL NOT NULL DEFAULT FALSE,
    official        BOOL NOT NULL DEFAULT FALSE,
    ulaest_count    INT  NOT NULL DEFAULT 0,
    sidste_besked   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_traade_brobygger ON besked_traade(brobygger_id);

CREATE TRIGGER trg_traade_updated BEFORE UPDATE ON besked_traade
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =============================================================================
-- BESKEDER (indhold i tråde)
-- =============================================================================

CREATE TABLE beskeder (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    traad_id        UUID NOT NULL REFERENCES besked_traade(id) ON DELETE CASCADE,
    from_rolle      bruger_rolle NOT NULL,
    fra_bruger_id   UUID,                            -- FK til brugere (003)
    tekst           TEXT NOT NULL,
    sent_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    laest_af        UUID[],                          -- array af bruger-IDs der har læst
    -- SignalR correlation
    signalr_msg_id  TEXT
);

CREATE INDEX idx_beskeder_traad   ON beskeder(traad_id);
CREATE INDEX idx_beskeder_sent_at ON beskeder(sent_at DESC);

-- =============================================================================
-- NOTIFIKATIONER (in-app + push)
-- =============================================================================

CREATE TYPE notif_type AS ENUM (
    'ny_aftale', 'aftale_godkendt', 'aftale_aflyst',
    'ny_besked', 'match_forslag', 'paamindelse',
    'system'
);

CREATE TABLE notifikationer (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bruger_id       UUID NOT NULL,                   -- modtager
    type            notif_type NOT NULL,
    titel           TEXT NOT NULL,
    tekst           TEXT NOT NULL,
    link            TEXT,                            -- navigation-target i appen
    unread          BOOL NOT NULL DEFAULT TRUE,
    -- Push-status
    push_sendt      BOOL NOT NULL DEFAULT FALSE,
    push_sendt_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notif_bruger  ON notifikationer(bruger_id);
CREATE INDEX idx_notif_unread  ON notifikationer(bruger_id, unread) WHERE unread = TRUE;

-- =============================================================================
-- WEB PUSH SUBSCRIPTIONS (VAPID)
-- =============================================================================

CREATE TABLE push_subscriptions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bruger_id       UUID NOT NULL,
    endpoint        TEXT NOT NULL UNIQUE,
    p256dh          TEXT NOT NULL,
    auth_key        TEXT NOT NULL,
    user_agent      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at    TIMESTAMPTZ
);

CREATE INDEX idx_push_bruger ON push_subscriptions(bruger_id);
