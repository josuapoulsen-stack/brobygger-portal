# Teknisk Review — SoS Brobygger Portal

**Formål:** Ekstern udvikler-gennemgang inden Azure-opsætning  
**Dato:** 2026-04-29  
**Codebase:** https://github.com/josuapoulsen-stack/brobygger-portal  
**Kontaktperson:** Josua Poulsen

---

## 1. Hvad er systemet?

En webapplikation til frivilligorganisationen SoS, der koordinerer "brobyggere" (frivillige) med "mennesker" (borgere med behov for støtte). Systemet håndterer:

- Matchmaking mellem borger og frivillig
- Aftalebooking og kalender
- Beskeder og notifikationer
- Statistik og SROI-beregning
- GDPR-kompliant registrering af følsomme helbredsoplysninger

---

## 2. Systemarkitektur — overblik

```
Browser (React 18 PWA)
        │
        │  HTTPS
        ▼
Azure Static Web Apps          ← frontend-hosting
        │
        │  REST + JWT
        ▼
Azure App Service (FastAPI)    ← backend API
        │
        ├──► Azure Database for PostgreSQL  ← primær datakilde
        ├──► Azure SignalR Service           ← realtids-beskeder
        ├──► Microsoft Graph (Mail.Send)     ← magic link emails
        ├──► Azure Key Vault                 ← secrets
        └──► Azure Application Insights     ← logging/monitoring
```

**Nuværende tilstand (FASE 1):**  
`USE_BACKEND = false` i `src/api/index.js` — frontenden kører mod localStorage-mockdata. Backend returnerer `503` på alle endpoints. Skifter til FASE 2 når Azure er klar.

---

## 3. Teknisk stack

| Lag | Teknologi | Version |
|-----|-----------|---------|
| Frontend | React | 18.3 |
| Build | Vite | 5 |
| Auth | MSAL.js + Entra ID External Identities | 3.x |
| Backend | FastAPI + Uvicorn/Gunicorn | 0.111 |
| Sprog | Python | 3.12 |
| ORM | SQLAlchemy + Alembic | 2.0 |
| Database | PostgreSQL | 16 |
| Realtime | Azure SignalR (REST-kald fra backend) | — |
| Push | Web Push API + VAPID (pywebpush) | — |
| PWA | vite-plugin-pwa + Service Worker | — |
| IaC | Azure Bicep | — |
| CI/CD | GitHub Actions | — |

---

## 4. Autentifikation og autorisation

### 4.1 Login-flow (brobygger)
```
Bruger → Magic link email (Microsoft Graph)
       → Klikker link → backend validerer token_hash
       → Returnerer JWT (HS256, 60 min)
       → Frontend gemmer token, sender som Bearer header
```

### 4.2 Login-flow (rådgiver / admin)
```
Bruger → Microsoft Entra ID External Identities
       → MFA via Microsoft Authenticator eller SMS
       → Azure udsteder JWT med AD-gruppe-claims
       → Backend validerer mod JWKS-endpoint
       → getRoleFromClaims() mapper til: brobygger | raadgiver | admin | superadmin
```

### 4.3 Roller og adgang
| Rolle | Adgang |
|-------|--------|
| `brobygger` | Egne aftaler, kalender, beskeder, profil |
| `raadgiver` | Alle mennesker + brobyggere i eget HQ |
| `admin` | Alle HQ'er, statistik, matching |
| `superadmin` | Alt inkl. brugerstyring |

**Spørgsmål til reviewer:** Er rolle-granulariteten tilstrækkelig? Bør der være field-level RLS frem for kun tabel-level?

### 4.4 Tokens
- Magic link tokens: SHA-256 hashes gemt i DB (aldrig råt token)
- JWT: HS256 i dev, RS256 (Entra JWKS) i prod
- Udløb: 60 min access, ingen refresh-token implementeret endnu

**Spørgsmål til reviewer:** Bør der tilføjes refresh-tokens, eller er Entras session-håndtering tilstrækkelig?

---

## 5. Datasikkerhed

### 5.1 Følsomme data (GDPR art. 9)
Helbredsoplysninger behandles som særlig kategori:

```sql
-- backend/migrations/001_initial_schema.sql
helbredsnoter_enc BYTEA  -- krypteret med pgcrypto (AES-256)
cpr_hash          TEXT   -- SHA-256 af CPR — aldrig råt CPR i DB
```

- `pgcrypto`-extension aktiveret i PostgreSQL
- Krypteringsnøgle hentes fra Azure Key Vault (aldrig i kode)
- Felter anonymiseres automatisk efter 30 dages sletning (trigger `anonymiser_slettede_mennesker()`)

**Spørgsmål til reviewer:** Er pgcrypto-baseret kryptering tilstrækkelig, eller bør vi bruge Azure Always Encrypted / Transparent Data Encryption på column-niveau?

### 5.2 Row-Level Security (RLS)
```sql
-- Aktiveret på mennesker og aftaler
ALTER TABLE aftaler   ENABLE ROW LEVEL SECURITY;
ALTER TABLE mennesker ENABLE ROW LEVEL SECURITY;

-- Kun service-account (bbadmin) har adgang
CREATE POLICY aftaler_service ON aftaler USING (current_user = 'bbadmin');
```

**Spørgsmål til reviewer:** RLS-policyen er i dag udelukkende baseret på database-bruger. Bør vi udvide til bruger-ID via `SET LOCAL app.current_user_id = '...'` så RLS slår igennem på rækkeniveau?

### 5.3 Audit-log
Alle INSERT/UPDATE/DELETE på `mennesker`, `aftaler` og `samtykker` logges automatisk via trigger:

```sql
-- Gemmer: tabel, række-id, handling, gamle data (JSONB), nye data (JSONB), tidsstempel
CREATE TRIGGER mennesker_audit AFTER INSERT OR UPDATE OR DELETE ON mennesker
FOR EACH ROW EXECUTE FUNCTION audit_changes();
```

Audit-log slettes automatisk efter 5 år (`ryd_gammel_audit()`).

### 5.4 Transport og headers
- HTTPS krævet (Azure SWA + App Service enforcer TLS)
- Security headers sat i `staticwebapp.config.json`:
  - `Content-Security-Policy`
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Strict-Transport-Security`

### 5.5 Secrets-håndtering
| Secret | Placering |
|--------|-----------|
| DATABASE_URL | Azure Key Vault → App Service env |
| VAPID_PRIVATE_KEY | Azure Key Vault → App Service env |
| JWT_SECRET (dev) | .env (ikke committet) |
| Azure Client ID/Tenant | GitHub Secrets → CI/CD |

---

## 6. API-struktur

### 6.1 Endpoints (FastAPI)
Base URL: `https://<app-service>.azurewebsites.net`

```
GET  /health                     → { status, version, db }
GET  /docs                       → OpenAPI UI (deaktiveres i prod)

POST /auth/token                 → { access_token, token_type }
POST /auth/magic-link/send       → afsender magic-link email
POST /auth/magic-link/verify     → validerer token → returnerer JWT

GET  /mennesker                  → liste (pagineret, HQ-filtreret)
POST /mennesker                  → opret ny (IntakeFlow)
GET  /mennesker/{id}             → detaljer
PUT  /mennesker/{id}             → opdater
DEL  /mennesker/{id}             → soft-delete (deleted_at sættes)

GET  /brobyggere                 → liste
GET  /brobyggere/{id}            → detaljer + åbne vagter

GET  /aftaler                    → liste (filtreret på bruger/HQ)
POST /aftaler                    → opret (MatchingFlow)
PUT  /aftaler/{id}               → opdater status

GET  /beskeder/traade            → liste af tråde
GET  /beskeder/traade/{id}       → tråd med beskeder
POST /beskeder                   → send besked (→ SignalR broadcast)

GET  /matching/suggest/{id}      → scorede brobygger-forslag til menneske
POST /matching/confirm           → bekræft match → opretter aftale

GET  /profil                     → egen profil
PUT  /profil                     → opdater

GET  /statistik/sroi             → SROI-beregning (aggregeret)
GET  /statistik/dashboard        → nøgletal
```

**Spørgsmål til reviewer:** Bør `/matching/suggest` returnere resultater direkte, eller er et async job-pattern (POST → polling) bedre ved mange brobyggere?

### 6.2 Autentifikations-flow for API-kald
```
Frontend                Backend
  │                       │
  │  POST /auth/token     │
  │  { token fra Entra }  │
  │──────────────────────►│
  │                       │ validerer JWT mod JWKS
  │  { access_token }     │ mapper claims → rolle
  │◄──────────────────────│
  │                       │
  │  GET /mennesker       │
  │  Authorization: Bearer <token>
  │──────────────────────►│
  │                       │ validerer signatur + udløb
  │  [{ ... }]            │ kontrollerer rolle + HQ
  │◄──────────────────────│
```

### 6.3 Realtid (SignalR)
```
Afsender besked
  → POST /beskeder (backend)
  → backend kalder SignalR REST API
  → SignalR pusher til alle forbundne klienter i gruppe
  → Frontend-hook (useSignalR.js) modtager → opdaterer UI
```

FASE 1: `BroadcastChannel` (samme faneblad/browser, ingen server)  
FASE 2: Azure SignalR med negotiate-endpoint

---

## 7. Database-skema (oversigt)

```
brobyggere          — frivillige
mennesker           — borgere (helbredsnoter_enc krypteret)
aftaler             — planlagte møder
besked_traade       — samtaler
besked_deltagere    — m2m: tråd ↔ bruger
beskeder            — individuelle beskeder
notifikationer      — push/email-køen
push_subscriptions  — Web Push endpoint + auth-nøgler
brugere             — login-konti (azure_oid + rolle)
invitationer        — magic link tokens (kun hash gemt)
samtykker           — GDPR art. 6 + art. 9 samtykker
audit_log           — automatisk revisionsspor
```

Migrationer: Alembic (`backend/alembic/versions/001–005`)  
Seed-data: `backend/seeds/demo_data.sql`

---

## 8. GDPR-checkliste (overordnet)

| Krav | Status |
|------|--------|
| Formålsbegrænsning dokumenteret | ✅ GDPR_COMPLIANCE.md |
| Art. 9 samtykke-flow | ✅ IntakeFlow trin 4 |
| Samtykke-tabel med version + tilbagetrækningsstatus | ✅ migration 005 |
| Anonymisering efter sletning (30 dage) | ✅ trigger i migration 004 |
| Audit-log med automatisk sletning (5 år) | ✅ trigger i migration 004 |
| RLS på mennesker og aftaler | ✅ migration 004 |
| Krypterede helbredsnoter | ✅ pgcrypto BYTEA |
| CPR aldrig gemt i klartekst | ✅ kun SHA-256 hash |
| Privatlivspolitik | ✅ PRIVACY_POLICY.md |
| DPIA udkast | ✅ GDPR_COMPLIANCE.md |
| Ret til indsigt / sletning | ⬜ endpointets ikke implementeret endnu |
| Databehandleraftale (DPA) med Microsoft | ⬜ afventer Azure-opsætning |

---

## 9. Nøglefiler til review

| Fil | Hvad reviewer bør kigge på |
|-----|---------------------------|
| `src/api/index.js` | Mock vs. live flag, API-kontrakter |
| `src/auth/msalInstance.js` | MSAL-konfiguration, scope-definitioner |
| `backend/routers/auth.py` | Token-validering, JWKS-integration |
| `backend/routers/magic_link.py` | Token-generering, hash-lagring, udløb |
| `backend/services/matching.py` | Scoring-algoritme, bias-risiko |
| `backend/migrations/001_initial_schema.sql` | Datamodel, indekser, ENUMs |
| `backend/migrations/004_gdpr_anonymisering.sql` | GDPR-triggers, RLS-policies |
| `backend/orm_models.py` | Relationer, cascade-regler |
| `infra/main.bicep` | Azure-ressourcer, netværksisolation |
| `staticwebapp.config.json` | Security headers, SPA-routing |
| `public/sw.js` | Service Worker — caching, push-handler |
| `GDPR_COMPLIANCE.md` | Compliance-tjekliste og DPIA |

---

## 10. Konkrete spørgsmål til reviewer

1. **RLS-granularitet:** Bør row-level security udvides til bruger-ID-niveau (ikke kun db-bruger), så en brobygger kun kan se egne aftaler direkte i DB-laget?

2. **Kryptering:** Er pgcrypto (AES-256 i PostgreSQL) tilstrækkelig til GDPR art. 9-data, eller bør vi bruge Azure Confidential Computing / column-level encryption?

3. **Magic link-sikkerhed:** Tokens udløber efter 48 timer og kan kun bruges én gang. Er det acceptabelt, eller bør vi kortere udløb + rate-limiting på endpointet?

4. **Refresh tokens:** Vi har kun access tokens (60 min). Bør brobyggere have længere sessioner via refresh tokens, eller håndteres det af Entras session-cookie?

5. **Matching-algoritme og bias:** Scoring-algoritmen sorterer på type, sprog, kapacitet og kontinuitet. Kan denne rangering skabe systematisk bias mod bestemte grupper?

6. **SignalR vs. polling:** Er Azure SignalR den rette løsning til ~50 samtidige brugere, eller ville Server-Sent Events (SSE) være billigere og enklere?

7. **Dataeksport (art. 20):** Retten til dataportabilitet er ikke implementeret. Hvad er den anbefalede form (JSON-download, CSV)?

8. **Penetrationstest:** Bør der laves en simpel pentest inden go-live, og hvem er ansvarlig?
