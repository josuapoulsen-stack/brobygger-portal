-- =============================================================================
-- demo_data.sql — Demo-seed til SoS Brobygger Portal
--
-- Spejler prototype-globals (window.SoS_BROBYGGERE, window.SoS_MENNESKER etc.)
-- så UI'et ser identisk ud med og uden backend.
--
-- Kør EFTER alle migrations:
--   psql $DATABASE_URL -f backend/seeds/demo_data.sql
-- =============================================================================

-- Ryd eksisterende demo-data (idempotent)
TRUNCATE TABLE beskeder, besked_traade, notifikationer, aftaler,
               mennesker, brugere, brobyggere
RESTART IDENTITY CASCADE;

-- =============================================================================
-- BROBYGGERE
-- =============================================================================

INSERT INTO brobyggere (id, azure_oid, navn, email, telefon, typer, sprog, hq, status, active, max_active, startdato, naeste_tid)
VALUES
  ('b00-0000-0000-0001', NULL, 'Maja Lindberg',    'maja@example.com',    '+45 28 11 22 33', ARRAY['en-til-en', 'cafe-gruppe'],    ARRAY['dansk', 'engelsk'],           'København N',  'aktiv',    2, 3, '2023-09-01', 'Tirsdag kl. 14-16'),
  ('b00-0000-0000-0002', NULL, 'Thomas Eriksen',   'thomas@example.com',  '+45 40 55 66 77', ARRAY['en-til-en'],                   ARRAY['dansk'],                      'Aarhus C',     'aktiv',    1, 2, '2022-06-15', 'Torsdag kl. 09-11'),
  ('b00-0000-0000-0003', NULL, 'Amira Osman',      'amira@example.com',   '+45 51 88 99 00', ARRAY['en-til-en', 'netvaerk'],       ARRAY['dansk', 'arabisk', 'engelsk'],'København S',  'aktiv',    3, 3, '2023-01-20', 'Mandag kl. 10-12'),
  ('b00-0000-0000-0004', NULL, 'Peter Norgaard',   'peter@example.com',   '+45 26 33 44 55', ARRAY['gruppe', 'cafe-gruppe'],       ARRAY['dansk'],                      'Odense C',     'pause',    0, 4, '2021-11-01', NULL),
  ('b00-0000-0000-0005', NULL, 'Sara Christoffersen','sara@example.com',  '+45 61 22 33 44', ARRAY['en-til-en'],                   ARRAY['dansk', 'tysk'],              'København N',  'aktiv',    1, 3, '2024-02-01', 'Onsdag kl. 13-15');

-- =============================================================================
-- BRUGERE (rådgivere og admins)
-- =============================================================================

INSERT INTO brugere (id, azure_oid, display_name, email, rolle, hq)
VALUES
  ('u00-0000-0000-0001', 'TODO_AZURE_OID_LINDA', 'Linda Sørensen',  'linda@sos.dk',  'Raadgiver', 'København N'),
  ('u00-0000-0000-0002', 'TODO_AZURE_OID_ADMIN', 'Admin SoS',       'admin@sos.dk',  'Admin',     NULL),
  ('u00-0000-0000-0003', 'TODO_AZURE_OID_HANNE', 'Hanne Vestergaard','hanne@sos.dk', 'Raadgiver', 'Aarhus C');

-- =============================================================================
-- MENNESKER (anonymiserede demo-profiler)
-- =============================================================================

INSERT INTO mennesker (id, navn, alder, typer, sprog, status, matched_with, hq, raadgiver_id)
VALUES
  ('m00-0000-0000-0001', 'Ahmad K.',      38, ARRAY['en-til-en'],             ARRAY['arabisk', 'dansk'], 'matched',    'b00-0000-0000-0001', 'København N', 'u00-0000-0000-0001'),
  ('m00-0000-0000-0002', 'Sofie B.',      27, ARRAY['en-til-en', 'netvaerk'], ARRAY['dansk'],            'aktiv',      'b00-0000-0000-0005', 'København N', 'u00-0000-0000-0001'),
  ('m00-0000-0000-0003', 'Yusuf M.',      45, ARRAY['cafe-gruppe'],           ARRAY['arabisk', 'dansk'], 'ny',          NULL,                'Aarhus C',    'u00-0000-0000-0003'),
  ('m00-0000-0000-0004', 'Maria T.',      31, ARRAY['en-til-en'],             ARRAY['dansk', 'polsk'],   'venteliste',  NULL,                'København S', 'u00-0000-0000-0001'),
  ('m00-0000-0000-0005', 'Lars H.',       52, ARRAY['gruppe'],                ARRAY['dansk'],            'matched',    'b00-0000-0000-0002', 'Aarhus C',    'u00-0000-0000-0003');

-- =============================================================================
-- AFTALER
-- =============================================================================

INSERT INTO aftaler (id, brobygger_id, menneske_id, dato, varighed, type, sted, status)
VALUES
  ('a00-0000-0000-0001', 'b00-0000-0000-0001', 'm00-0000-0000-0001', NOW() + INTERVAL '1 day',    60,  'moede',       'Cafe Nørreport',     'planlagt'),
  ('a00-0000-0000-0002', 'b00-0000-0000-0001', 'm00-0000-0000-0001', NOW() - INTERVAL '7 days',   90,  'aktivitet',   'Fælledparken',       'gennemfoert'),
  ('a00-0000-0000-0003', 'b00-0000-0000-0005', 'm00-0000-0000-0002', NOW() + INTERVAL '3 days',   60,  'telefonopkald', NULL,               'planlagt'),
  ('a00-0000-0000-0004', 'b00-0000-0000-0002', 'm00-0000-0000-0005', NOW() - INTERVAL '14 days',  120, 'moede',       'Biblioteket Aarhus', 'gennemfoert'),
  ('a00-0000-0000-0005', 'b00-0000-0000-0003', 'm00-0000-0000-0001', NOW() - INTERVAL '30 days',  60,  'moede',       'SoS kontor',         'aflyst');

-- =============================================================================
-- BESKEDTRÅDE
-- =============================================================================

INSERT INTO besked_traade (id, titel, brobygger_id, from_brobygger, official, ulaest_count)
VALUES
  ('t-info-maj',   'Nyhedsbrev — maj 2025',        NULL,                FALSE, TRUE, 0),
  ('t-kursus',     'Frivilligkursus 14. juni',      NULL,                FALSE, TRUE, 1),
  ('t-bb-linda',   'Spørgsmål til Linda',           'b00-0000-0000-0001',TRUE, FALSE, 0);

-- =============================================================================
-- BESKEDER (i tråde)
-- =============================================================================

INSERT INTO beskeder (traad_id, from_rolle, fra_bruger_id, tekst, sent_at)
VALUES
  ('t-info-maj', 'Raadgiver', 'u00-0000-0000-0001',
    'Kære alle — her er nyheder fra maj. Vi har fået 3 nye frivillige og 5 nye borgere i forløb.',
    NOW() - INTERVAL '5 days'),
  ('t-kursus', 'Raadgiver', 'u00-0000-0000-0001',
    'Husk tilmelding til frivilligkurset senest fredag. Svar på denne besked.',
    NOW() - INTERVAL '2 days'),
  ('t-bb-linda', 'Brobygger', NULL,
    'Hej Linda, jeg er lidt i tvivl om næste møde med Ahmad. Har du tid til en snak?',
    NOW() - INTERVAL '1 day'),
  ('t-bb-linda', 'Raadgiver', 'u00-0000-0000-0001',
    'Selvfølgelig! Ring til mig i morgen formiddag.',
    NOW() - INTERVAL '23 hours');

-- =============================================================================
-- NOTIFIKATIONER (til Maja / b00-0000-0000-0001)
-- =============================================================================

INSERT INTO notifikationer (id, bruger_id, type, titel, tekst, unread, link)
VALUES
  ('n00-0000-0000-0001', 'u00-0000-0000-0001', 'ny_aftale',   'Ny aftale oprettet',       'Ahmad: Møde i morgen kl. 10',             TRUE, '/kalender'),
  ('n00-0000-0000-0002', 'u00-0000-0000-0001', 'ny_besked',   'Ny besked fra Maja',        'Maja spørger om næste møde med Ahmad',    TRUE, '/beskeder'),
  ('n00-0000-0000-0003', 'u00-0000-0000-0001', 'system',      'Frivilligkursus 14. juni', 'Tilmeld dig senest på fredag',             FALSE, '/beskeder');
