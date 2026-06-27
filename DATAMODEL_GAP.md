# Datamodel-gap: prototype vs. backend (FASE 2)

> Sammenligning juni 2026: prototypens datamodel (`Brobygger portal.html` + localStorage) vs. backend-schemaet (`db/schema.sql` + `backend/alembic/versions/`).
> **Konklusion:** backend-schemaet er fra et tidligere designtrin og **mangler stort set alle features tilføjet i prototypen siden**. Skal lukkes før FASE 2-API'erne bygges, ellers kan data ikke flyttes fra prototypen 1:1.

> **STATUS (juni 2026):** Lukket i **migration `006_prototype_alignment.py`** + `backend/orm_models.py` + `api/openapi.yaml` (nye component-skemaer). Verificeret: migration + ORM kompilerer, openapi er gyldig YAML.
> **Resterende FASE-2-follow-up:** (1) felt-tilføjelserne på de *eksisterende* `Menneske`/`Aftale` **API-request/response-skemaer** i openapi (selve DB-felterne findes), (2) faktiske endpoints/routers for de nye ressourcer, (3) kryptering af `konto_nr_enc` i service-laget, (4) seed/migrér `SoS_REFS` → `stamdata`-tabellen.

Status: `[ ]` mangler i backend · `[~]` delvist · `[x]` dækket

---

## 1. Manglende tabeller (nye features uden backend-model)

- [ ] **`henvendelser`** — flere henvendelser pr. menneske, førstegangshenvender til statistik/lavtærskel
  ```sql
  CREATE TABLE henvendelser (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    menneske_id UUID NOT NULL REFERENCES mennesker(id) ON DELETE CASCADE,
    type TEXT NOT NULL,            -- 'Personen selv' | 'Kommune' | 'Pårørende' | ...
    navn TEXT,                     -- fx pårørende/instans (valgfrit)
    dato DATE NOT NULL,            -- tidligste dato = førstegangshenvender
    note TEXT,
    oprettet_af_id UUID REFERENCES brugere(id),
    created_at TIMESTAMPTZ DEFAULT now()
  );
  CREATE INDEX ON henvendelser(menneske_id, dato);
  ```

- [ ] **`ucla_maalinger`** — UCLA-3 ensomhedsmåling (baseline + opfølgninger). Fravalg som flag på menneske.
  ```sql
  CREATE TYPE ucla_slags AS ENUM ('baseline', 'opfoelgning');
  CREATE TABLE ucla_maalinger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    menneske_id UUID NOT NULL REFERENCES mennesker(id) ON DELETE CASCADE,
    slags ucla_slags NOT NULL,
    q1 SMALLINT, q2 SMALLINT, q3 SMALLINT,   -- 1–3 hver
    sum SMALLINT NOT NULL,                    -- 3–9
    dato DATE NOT NULL,
    label TEXT,                               -- fx '3 mdr'
    oprettet_af_id UUID REFERENCES brugere(id),
    created_at TIMESTAMPTZ DEFAULT now()
  );
  -- + mennesker.ucla_fravalgt BOOLEAN DEFAULT false  (fravalgt = vises aldrig igen)
  ```

- [ ] **`udlaeg_konti`** — brobyggeres bankoplysninger til kreditor-oprettelse (følsomt → kryptér + rolle-tjek)
  ```sql
  CREATE TABLE udlaeg_konti (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brobygger_id UUID NOT NULL REFERENCES brobyggere(id) ON DELETE CASCADE,
    navn TEXT NOT NULL,
    email TEXT,
    reg_nr TEXT NOT NULL,            -- 4 cifre
    konto_nr_enc BYTEA NOT NULL,     -- KRYPTERET (som helbredsnoter_enc)
    aar SMALLINT NOT NULL,           -- til kreditorgruppe (år − 2020)
    kreditor_nr TEXT,                -- tildeles ved eksport
    indsendt_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (brobygger_id)
  );
  ```
  *Bemærk: kreditor-CSV-eksport skal autoriseres server-side (kun finans/admin).*

- [ ] **`opkald_log`** — telefonopkald med type, koblet til menneske ELLER brobygger
  ```sql
  CREATE TYPE opkald_type AS ENUM ('samtale_menneske', 'samtale_brobygger', 'ringeopgave');
  CREATE TABLE opkald_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type opkald_type NOT NULL,
    under_type TEXT,                 -- ringeopgave: 'bestil_tid' | 'forny_recept' | 'kontakt_forening' | 'andet'
    menneske_id UUID REFERENCES mennesker(id) ON DELETE SET NULL,
    brobygger_id UUID REFERENCES brobyggere(id) ON DELETE SET NULL,
    tlf TEXT,
    note TEXT NOT NULL,
    dato DATE NOT NULL, tid TEXT,
    oprettet_af_id UUID REFERENCES brugere(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    CHECK (menneske_id IS NOT NULL OR brobygger_id IS NOT NULL)   -- skal kobles til en person
  );
  ```

- [ ] **`besked_skabeloner`** — beskedskabeloner pr. rådgiver (flettefelter i teksten)
  ```sql
  CREATE TABLE besked_skabeloner (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ejer_id UUID NOT NULL REFERENCES brugere(id) ON DELETE CASCADE,
    navn TEXT NOT NULL,
    indsats TEXT DEFAULT 'alle',     -- 'alle' | 'social' | 'forening' | 'sundhed'
    tekst TEXT NOT NULL,             -- med {{flettefelter}}
    er_standard BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
  );
  ```

- [ ] **`stamdata`** — admin-redigerbart reference-data (ERSTATTER `SoS_REFS`). Generisk tabel der dækker ALT:
  ```sql
  CREATE TABLE stamdata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kategori TEXT NOT NULL,          -- 'hovedsaeder'|'afdelinger'|'aftaletyper'|'henvendere'|
                                     -- 'modtagere'|'transportplaner'|'aflysningsaarsager'|
                                     -- 'aflystAf'|'finansieringskilder'|'samarbejdspartnere'|'brobygningstyper'
    navn TEXT NOT NULL,
    hovedsaede TEXT,                 -- hq-specifik (afdelinger, samarbejdspartnere); NULL/'Alle' = landsdækkende
    farve TEXT,                      -- stamdata-farve pr. post
    sort_order INT DEFAULT 0,
    aktiv BOOLEAN DEFAULT true
  );
  CREATE INDEX ON stamdata(kategori);
  ```
  → dækker på én gang: **samarbejdspartnere pr. hovedsæde**, **afdelinger{navn,hovedsaede}**, **stamdata-farver**, og resten af de admin-redigerbare lister.

- [ ] **`kontaktpersoner`** — pårørende/instans pr. menneske (prototypen har `kontaktperson(er)`)
  ```sql
  CREATE TABLE kontaktpersoner (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    menneske_id UUID NOT NULL REFERENCES mennesker(id) ON DELETE CASCADE,
    rolle TEXT, navn TEXT, tlf TEXT
  );
  ```

---

## 2. Manglende kolonner på eksisterende tabeller

### `mennesker` — tilføj
- [ ] `afdeling TEXT` (har kun `hq`)
- [ ] `kilde TEXT` (henvisningskilde — bruges til statistik/førstegangshenvender-seed)
- [ ] `meetpoint TEXT` (mødested, separat fra `adresse`)
- [ ] `sroi_maalgruppe TEXT`, `helbreds_kategorier TEXT[]`
- [ ] `praeferencer JSONB` (tidspunkt/frekvens)
- [ ] `afslut_trivsel SMALLINT`, `afslut_aarsag TEXT` (har kun `afslutning_note`)
- [ ] `ucla_fravalgt BOOLEAN DEFAULT false`
- [ ] **`telefon` som identifikator:** tilføj `telefon_norm TEXT` (kanonisk, sidste 8 cifre) + `CREATE INDEX ON mennesker(telefon_norm)` til genkendelse/dedup på tværs af forløb. (Ikke UNIQUE — familier kan dele nummer; brug til opslag + menneskelig bekræftelse.)
- [~] `noter`/`needs`: prototypen har `needs[]` + tidsstemplede `notes[]` → overvej `noter`-tabel i stedet for TEXT.

### `aftaler` — tilføj (prototypen har langt flere felter end backend)
- [ ] `aftaletype TEXT` (Fysisk følgeskab / Ringeopgave / …) — ≠ backendens `type`-enum
- [ ] `brobygningstype TEXT` (Social/Forening/Sundhed)
- [ ] `henvender TEXT`, `modtager TEXT`, `finansiering TEXT`, `samarbejdspartner TEXT`, `afdeling TEXT`
- [ ] `aflyst_af TEXT`, `aflysnings_aarsag TEXT`, `transportplan TEXT`
- [ ] `aktivitets_tid TEXT`, `fremmoede_type TEXT`, `gentagelse TEXT`, `aftale_form TEXT`
- [ ] `brobygger_note TEXT` (briefing til brobygger — gemt på aftalen)
- [ ] `raadgiver_opfoelgning TEXT`
- [ ] **`aftale_log`** (brobyggerLog) — udfald + varighed + note + logged_at (kolonner eller sub-tabel):
  `udfald TEXT ('gennemfoert'|'afbud'|'ikke-modt'), varighed_min INT, log_note TEXT, logged_at TIMESTAMPTZ`
- [ ] **Status-taksonomi:** prototypens `aftale_status` (kladde/pending/confirmed/gennemfoert/aflyst/afslaaet/brudt) er rigere end backendens (planlagt/gennemfoert/aflyst/udsat) — afstem ENUM.

### `brobyggere` — mindre
- [ ] `afdeling TEXT`, `telefon_norm` (samme dedup-idé som mennesker, hvis ønsket)

---

## 3. Det der ER dækket ✅
- Kerne: `mennesker`, `brobyggere`, `aftaler`, `brugere`, `kontakt_log`
- Beskeder/notifikationer/push: `besked_traade`, `beskeder`, `notifikationer`, `push_subscriptions`
- GDPR: `samtykker`, `audit_log`, soft-delete + anonymisering (migration 004), krypteret `helbredsnoter_enc`
- Invitationer: `invitations` (magic links)

---

## 4. Anbefalet rækkefølge (FASE 2)
1. **`stamdata`-tabel først** — den låser referencer (samarbejdspartnere pr. hq, farver, afdelinger) som resten peger på.
2. Udvid **`mennesker`** + **`aftaler`** med de manglende kolonner + afstem ENUM'er.
3. Nye tabeller: `henvendelser`, `ucla_maalinger`, `opkald_log`, `besked_skabeloner`, `udlaeg_konti`, `kontaktpersoner`.
4. **Følsomme felter krypteres** (bank-kontonr som helbredsnoter) og eksport/adgang autoriseres server-side.
5. Tilføj `telefon_norm` + index til telefon-genkendelse.
6. Skriv migration **006** (samlet) + opdatér `orm_models.py` + `api/openapi.yaml`.

---

*Genereret juni 2026 ud fra sammenligning af prototype og `db/schema.sql` + alembic-migrationer. Ingen kode ændret — dette er et FASE-2-designgrundlag.*
