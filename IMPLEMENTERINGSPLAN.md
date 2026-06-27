# Implementeringsplan — SoS Brobygger Portal + Bifrost
**Version:** 2.0 — inkl. Microsoft Nonprofit-program  
**Dato:** 2026-04-29  
**Estimeret total tid:** 10–13 uger med én udvikler

---

## Forudsætninger inden opstart

Disse tre ting gøres af SoS **inden udvikleren starter**:

| # | Opgave | Ansvarlig | Tid |
|---|--------|-----------|-----|
| 1 | Opret nonprofit-konto på **nonprofit.microsoft.com** | SoS admin | 30 min |
| 2 | Aktivér **Azure-kreditter ($2.000/år)** via nonprofit-portalen | SoS admin | 15 min |
| 3 | Tilmeld **AccountGuard** (gratis trusselsvarsling) | SoS admin | 10 min |

---

## FASE 0 — Sikkerhed og fundament (uge 1)
*Gøres inden al anden udvikling. Kan køre parallelt med Fase 1.*

### 0.1 Gratis sikkerhedstjek (Microsoft Security Assessment)
- Book via nonprofit-portalen → Microsoft gennemgår hele SoS' digitale infrastruktur
- Output: prioriteret handlingsplan
- **Relevant for:** Brobygger-portalen (Art. 9 GDPR-data), Bifrost (økonomidata), eksisterende M365-opsætning
- ⏱ 1–2 uger fra booking til rapport

### 0.2 Microsoft Defender for Business
- **Pris:** $3/bruger/md → **$1,20/bruger/md med 60% nonprofit-rabat**
- For 40 medarbejdere: ~$48/md ≈ 350 kr./md
- Dækker: endpoint-beskyttelse på alle enheder der tilgår systemerne
- Aktiveres via Microsoft 365 Admin Center
- ⏱ 1 dag opsætning

### 0.3 Azure-infrastruktur oprettes (Bicep-deployment)
Kodebasen indeholder allerede `infra/main.bicep` — én kommando opretter:

```bash
az deployment sub create \
  --location northeurope \
  --template-file infra/main.bicep
```

Opretter automatisk:
- ✅ Azure Static Web Apps (frontend — **gratis tier**)
- ✅ App Service B1 (FastAPI backend — ~$13/md)
- ✅ PostgreSQL Flexible Server Burstable B1ms (~$25/md)
- ✅ Azure Key Vault (~$1/md)
- ✅ Application Insights (**gratis** op til 5 GB/md)
- ~~Azure SignalR~~ → **udgår**: SSE i egen backend (se 3.2) — $0, ingen ekstra tjeneste

**Total infrastruktur: ~$39/md = ~$470/år**
**Dækket af nonprofit-kreditterne i ~4 år**

---

## FASE 1 — Entra ID + Login (uge 1–2)
*Brobyggere logger ind med magic link. Rådgivere/admins med Microsoft-konto + MFA.*

### Opgaver
| Opgave | Detalje |
|--------|---------|
| Opret app-registrering i Entra ID | Azure Portal → Entra ID → App registrations |
| Konfigurér External Identities | Inviter-flow til brobyggere via email |
| Slå MFA til | Microsoft Authenticator + SMS-fallback |
| Gem `AZURE_CLIENT_ID` + `AZURE_TENANT_ID` | → GitHub Secrets + Key Vault |
| Test login-flow | Brobygger (magic link) + admin (Entra) |

### Sessioner
- Brobyggere: 30–90 dage på samme enhed (MFA usynlig i hverdagen)
- Rådgivere/admins: standard Entra-session (8 timer)

### Pris
- Entra ID External Identities: $0,00325/MAU
- 50 brobyggere = **~$2/md** (trækkes fra Azure-kreditterne)

---

## FASE 2 — Database + Backend aktiveres (uge 2–4)

### 2.1 Database
```bash
# Kør migrationer mod Azure PostgreSQL
make migrate   # svarer til: alembic upgrade head

# Seed demo-data til test
make seed
```

Migrationer 001–005 opretter automatisk:
- Alle tabeller (brobyggere, mennesker, aftaler, beskeder, samtykker...)
- pgcrypto-kryptering af helbredsnoter (Art. 9 GDPR)
- Row-Level Security på følsomme tabeller
- Audit-log med automatisk sletning efter 5 år
- Anonymisering af slettede mennesker efter 30 dage

### 2.2 Backend live
```python
# src/api/index.js
USE_BACKEND = true   # ← skift denne når alle endpoints er klar
```

Aktiverer alle FastAPI-endpoints (returnerer nu 503-stubs → rigtig logik):
- `/mennesker` — CRUD med GDPR-felter
- `/brobyggere` — profil + vagter
- `/aftaler` — booking + status
- `/matching/suggest` — scoringsalgoritme (0–100)
- `/beskeder` — tråde + SSE-broadcast (egen backend)
- `/statistik/sroi` — SROI-beregning

### 2.3 CI/CD genaktiveres
Workflow-filerne gendannes fra git og push-triggeren slås til:
```bash
git show <commit>:.github/workflows/deploy.yml > .github/workflows/deploy.yml
```

GitHub Actions bygger og deployer automatisk ved hvert push til `master`.

---

## FASE 3 — Notifikationer + Realtid (uge 4–5)

### 3.1 Web Push (VAPID)
VAPID-nøgler er allerede genereret (se `.env.example`).  
Brobyggere modtager push-notifikationer når:
- Ny aftale oprettes (matching bekræftet)
- Koordinator sender besked
- Påmindelse 24 timer før aftale

### 3.2 Realtids-beskeder — SSE i egen backend (Azure SignalR UDGÅR)
**Beslutning (juni 2026):** Vi bruger **Server-Sent Events (SSE) i vores egen FastAPI-backend** i stedet for Azure SignalR.

- **Mønster:** beskeder gemmes i PostgreSQL (kilde) → SSE pusher "ny besked"-event til åbne klienter → klienten henter siden-sidst ved (gen)forbindelse. Afsendelse via almindelig autentificeret POST.
- **Web Push** (3.1) håndterer notifikationer når appen er lukket — SSE betyder kun noget mens appen er åben.
- **Begrundelse:** ved vores skala (~50 medarbejdere samtidigt, 50–500 beskeder/dag) giver SignalR ingen mærkbar UX-gevinst for slutbrugeren, men koster ~$580/år og tilføjer en ekstra komponent der behandler beskeddata. SSE er $0 oveni App Service, holder data i egen backend (GDPR-rent), er ren HTTPS, og browserens `EventSource` genforbinder automatisk.
- **Forbehold:** valider Entra ID-token ved forbindelse + autorisér hvilke tråde brugeren må følge; send keepalive ~hvert 30. sek. (Azure idle-timeout ~230 sek.); kører vi nogensinde på **flere App Service-instanser**, tilføj **Postgres `LISTEN/NOTIFY`** (eller Redis) som backplane; aktivér **HTTP/2** på den host der serverer SSE (App Service-indstilling) — fjerner browserens "6 forbindelser pr. host"-grænse.
- **Oprydning ved FASE 2-build:** fjern `azure-signalr` (requirements), `Microsoft.SignalRService/signalR` (`infra/main.bicep`) og `SIGNALR_CONNECTION_STRING` (`backend/config.py`).

### 3.3 Magic link emails
Via Microsoft Graph `Mail.Send`:
- Brobygger-invitation med login-link
- Aftaleberkræftelse til borger (via koordinator)
- Kræver Graph API-tilladelse (`Mail.Send`) i Entra-app-registreringen
- **`aiosmtplib`/SMTP udgår:** vi sender via Graph (mere sikkert — ingen mailboks-password; Microsoft udfaser SMTP basic-auth). Allerede påbegyndt i `backend/services/email.py`.

---

## FASE 4 — Bifrost (NGO-økonomi + rapportering) (uge 5–8)
*Kører parallelt med eller efter Brobygger FASE 2–3*

### Infrastruktur (samme Azure-abonnement)
| Ressource | Estimat/md |
|-----------|------------|
| App Service B1 (Bifrost API) | ~$13 |
| PostgreSQL database (deles eller separat) | ~$0–25 |
| **Tillæg til eksisterende regning** | **~$13–38/md** |

**Samlet med Brobygger: ~$52–77/md = godt under $2.000/år**

### Bifrost-aktivering
- Migrationer 001–014 kører mod Azure PostgreSQL
- JWT-auth skifter fra dev-tilstand til Entra RS256 JWKS
- APScheduler aktiveres (`SCHEDULER_ENABLED=true`)
  - Dagligt: tjek budgetalerter
  - Ugentligt: dispatch notifikationer
  - Månedligt: ryd gamle tokens

### Integration med Brobygger-portalen (fremtidig)
Når begge systemer er live på Azure:
```
Brobygger-portal (Azure)
  └─ GET /statistik/sroi?periode=Q1-2026
       │ JSON: { kontakter, sroi_dkk, aktive_brobyggere }
       ▼
Bifrost (Azure)
  └─ POST /aktivitet/import
       │ opretter aktivitetslinjer på relevant grant
       ▼
  Generer rapport til Velux / UM / bestyrelse
```

Manuel JSON-eksport er alternativet indtil direkte integration er bygget.

---

## FASE 5 — GDPR-afslutning + go-live (uge 8–10)

### Teknisk tjekliste
| Punkt | Status |
|-------|--------|
| Sikkerhedstjek-rapport gennemgået og handlingsplan udført | ⬜ |
| Defender for Business aktivt på alle enheder | ⬜ |
| AccountGuard tilmeldt | ⬜ |
| HTTPS enforced på alle endpoints | ⬜ |
| Key Vault indeholder alle secrets (ingen i kode) | ⬜ |
| Audit-log verificeret (INSERT/UPDATE/DELETE logges) | ⬜ |
| RLS testet (brobygger kan ikke se andres data) | ⬜ |
| Anonymiserings-trigger testet | ⬜ |
| Backup konfigureret (PostgreSQL geo-redundant) | ⬜ |

### GDPR-tjekliste
| Punkt | Status |
|-------|--------|
| Privatlivspolitik publiceret (`PRIVACY_POLICY.md` → website) | ⬜ |
| Databehandleraftale (DPA) underskrevet med Microsoft | ⬜ |
| Samtykke-flow testet (IntakeFlow trin 4) | ⬜ |
| Ret til indsigt-endpoint implementeret (`GET /mig/data`) | ⬜ |
| Ret til sletning testet (soft-delete + 30-dages anonymisering) | ⬜ |
| DPIA gennemgået og godkendt internt | ⬜ |

### Kommunikation
- [ ] Onboarding-guide til brobyggere (magic link + app-installation)
- [ ] Træning af rådgivere/admins (MatchingFlow + IntakeFlow)
- [ ] Supportkontakt defineret

---

## Økonomi — samlet oversigt

### Månedlige driftsomkostninger
| Post | Pris/md |
|------|---------|
| Azure Static Web Apps (frontend) | Gratis |
| App Service B1 × 2 (Brobygger + Bifrost) | ~$26 |
| PostgreSQL Flexible Server | ~$25 |
| Key Vault | ~$1 |
| Realtid (SSE i egen backend) | Gratis — SignalR udgår |
| Application Insights | Gratis |
| Entra ID External Identities (50 MAU) | ~$2 |
| **Subtotal Azure** | **~$54/md** |
| Defender for Business (40 brugere × $1,20) | ~$48/md |
| **TOTAL** | **~$102/md ≈ $1.224/år** |

### Nonprofit-kreditter
- **Azure-grant:** $2.000/år
- **Dækker:** Azure-infrastruktur (~$648/år) + Entra (~$24/år) = ~$672/år
- **Overskud af kreditter:** ~$1.328/år til vækst
- **Defender faktureres separat** via M365 Admin (~$576/år ≈ 4.200 kr./år for 40 brugere)

---

## Tidsplan (samlet)

```
Uge 1     Nonprofit-registrering · Sikkerhedstjek bookes · Azure infrastruktur · Defender aktiveres
Uge 1–2   Entra ID login · MFA · AccountGuard
Uge 2–4   Database live · Backend aktiveres · CI/CD genaktiveres
Uge 4–5   Push-notifikationer · SSE realtid (egen backend) · Magic link emails
Uge 5–8   Bifrost på Azure · APScheduler · JWT production
Uge 8–10  GDPR-afslutning · Sikkerhedstjek-handlingsplan · Go-live
Uge 10–13 Fejlretning · Monitorering · Bifrost–Brobygger integration (valgfrit)
```

---

## Kontakter og links

| Ressource | URL |
|-----------|-----|
| Microsoft Nonprofit-portal | nonprofit.microsoft.com |
| Azure-kreditter aktivering | nonprofit.microsoft.com/azure |
| Gratis sikkerhedstjek | microsoft.com/en-us/nonprofits/security |
| AccountGuard tilmelding | microsoft.com/en-us/accountguard |
| Defender for Business | via Microsoft 365 Admin Center |
| GitHub repo (kodebase) | github.com/josuapoulsen-stack/brobygger-portal |
| Teknisk review-dokument | TECH_REVIEW.md i repo |
