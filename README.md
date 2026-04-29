# SoS Brobygger Portal

Intern platform til koordinering af frivillige brobyggere og mennesker med behov for hjælp. Udviklet for **Social Sundhed (SoS)**.

---

## Arkitektur

```
brobygger-portal/
├── Brobygger portal.html   # Prototype (React 18 + Babel, kørende nu)
├── src/                    # Produktion Vite/JSX (FASE 2)
│   ├── api/index.js        # USE_BACKEND=false → prototype-data, true → FastAPI
│   ├── auth/               # MSAL (Entra ID) + magic link
│   ├── components/         # shared/ + brobygger/ + admin/
│   ├── hooks/              # useApi, useSignalR, usePush, useMatching
│   ├── styles/tokens.js    # SoS design system
│   └── utils/              # dates, sroi, validation
├── backend/                # FastAPI (Python 3.12)
│   ├── main.py             # App + CORS + routers
│   ├── routers/            # mennesker, brobyggere, aftaler, beskeder, ...
│   ├── services/           # email, push, signalr, matching
│   ├── migrations/         # SQL 001–005
│   ├── seeds/demo_data.sql
│   └── tests/
├── infra/main.bicep        # Azure IaC
├── docker-compose.yml      # Lokal full-stack
└── .github/workflows/      # CI/CD (SWA + App Service)
```

**Tech stack:**
- Frontend: React 18 + Vite 5 + MSAL.js v3 + vite-plugin-pwa
- Backend: Python 3.12 + FastAPI + SQLAlchemy + Alembic
- Database: PostgreSQL 16
- Auth: Microsoft Entra ID External Identities + magic link (brobyggere)
- Realtime: Azure SignalR
- Push: Web Push API (VAPID)
- Hosting: Azure Static Web Apps + Azure App Service

---

## Kom i gang (lokal udvikling)

### Forudsætninger

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 4.x+
- Node.js 20+ (kun hvis du kører frontend uden Docker)
- Python 3.12+ (kun hvis du kører backend uden Docker)

### 1. Klon og konfigurér

```bash
git clone https://github.com/josuapoulsen-stack/brobygger-portal.git
cd brobygger-portal
cp .env.example .env
```

`.env` er forudkonfigureret til lokal udvikling — du behøver ikke ændre noget for at starte.

### 2. Start databasen og kør migrationer (første gang)

```bash
# Start kun databasen
docker compose up -d db

# Kør SQL-migrationer
docker compose run --rm migrate

# Indlæs demo-data
docker compose run --rm seed
```

### 3. Start hele stacken

```bash
docker compose up
```

| Service | URL |
|---------|-----|
| Frontend (Vite) | http://localhost:5173 |
| Backend (FastAPI) | http://localhost:8000 |
| API-dokumentation | http://localhost:8000/docs |
| Database | localhost:5432 |

> **Tip:** Ændringer i `backend/` og `src/` afspejles straks (live reload).

### 4. Kun prototypen (ingen Docker)

Åbn `Brobygger portal.html` direkte i en browser — ingen installation nødvendig.

---

## Miljøvariabler

Se `.env.example` for komplet liste. Vigtigste variabler:

| Variabel | Beskrivelse | Lokal default |
|----------|-------------|---------------|
| `DATABASE_URL` | PostgreSQL-forbindelsesstreng | `postgresql://bbadmin:devpassword123@db:5432/brobygger` |
| `ENVIRONMENT` | `development` / `production` | `development` |
| `JWT_SECRET` | Min. 32 tegn | Forudsat i `.env.example` |
| `AZURE_CLIENT_ID` | Entra ID app-ID | `TODO_CLIENT_ID` |
| `AZURE_TENANT_ID` | Entra ID tenant-ID | `TODO_TENANT_ID` |
| `VAPID_PUBLIC_KEY` | Web Push public key | Forudsat (real nøgle) |
| `VAPID_PRIVATE_KEY` | Web Push private key | Forudsat (real nøgle) |
| `SIGNALR_CONNECTION_STRING` | Azure SignalR | Tom (realtime deaktiveret lokalt) |

---

## Backend (FastAPI)

### Kør tests

```bash
# I Docker
docker compose run --rm api pytest backend/tests/ -v

# Eller direkte (kræver venv)
python -m venv venv
venv/Scripts/pip install -r backend/requirements.txt
pytest backend/tests/ -v
```

### Kør migrationer manuelt

```bash
docker compose run --rm migrate
# Svarer til: alembic upgrade head
```

### Reset database

```bash
docker compose down -v      # fjerner postgres_data volume
docker compose up -d db
docker compose run --rm migrate
docker compose run --rm seed
```

### API-nøglepunkter

```
GET  /health                        → Sundhedstjek
GET  /docs                          → Swagger UI

POST /v1/auth/invite                → Send magic link til brobygger
POST /v1/auth/magic?token=...       → Validér magic link → JWT
POST /v1/auth/refresh               → Forny JWT

GET  /v1/mennesker                  → Liste (kræver rådgiver/admin)
POST /v1/mennesker                  → Opret nyt menneske
GET  /v1/mennesker/{id}             → Detaljer

GET  /v1/brobyggere                 → Liste
GET  /v1/matching/suggest/{id}      → Foreslå brobyggere til et menneske
POST /v1/matching/confirm           → Bekræft matching → opret aftale

GET  /v1/aftaler                    → Liste
POST /v1/aftaler/{id}/status        → Opdatér status

GET  /v1/beskeder/threads           → Beskedtråde
POST /v1/beskeder/threads/{id}/send → Send besked

POST /v1/push/subscribe             → Registrér push-subscription
```

> **FASE 1:** Alle endpoints returnerer `503 Backend ikke aktivt endnu`.
> Aktiveres én router ad gangen i FASE 2 ved at skifte `USE_BACKEND = true` i `src/api/index.js`.

---

## Frontend (Vite)

### Kør uden Docker

```bash
npm install
npm run dev         # http://localhost:5173
npm run build       # Produk­tions­byg
npm run preview     # Preview af build
```

### FASE 1 vs FASE 2

`src/api/index.js` har ét flag øverst:

```js
const USE_BACKEND = false;   // false = prototype-data (localStorage)
                             // true  = rigtige API-kald til /v1/...
```

Skift til `true` når alle nødvendige endpoints er klar med DB-logik.

---

## CI/CD

| Workflow | Trigger | Hvad |
|----------|---------|------|
| `.github/workflows/deploy.yml` | Push til `master` (src/**) | Build + deploy til Azure Static Web Apps |
| `.github/workflows/deploy-backend.yml` | Push til `master` (backend/**) | pytest → zip → deploy til Azure App Service |

Begge workflows kræver GitHub Secrets:
- `AZURE_STATIC_WEB_APPS_API_TOKEN`
- `AZURE_WEBAPP_PUBLISH_PROFILE`

Workflows kører grønt (tests + build) selvom secrets mangler — deploy-steget skippes.

---

## Azure Infrastructure

```bash
# Deploy Azure-infrastruktur (kræver Azure CLI + adgang)
az login
az group create --name rg-brobygger-prod --location westeurope
az deployment group create \
  --resource-group rg-brobygger-prod \
  --template-file infra/main.bicep
```

Estimeret månedlig pris (dev-tier): **~445 DKK/md**

---

## GDPR & sikkerhed

- Art. 9-data (helbredsnoter) krypteres på kolonne-niveau med `pgcrypto`
- Row-Level Security (RLS) isolerer brobygger-data
- Samtykker logges i `samtykker`-tabellen (version, dato, tilbagetrækning)
- Anonymisering kører automatisk 30 dage efter sletning (`anonymiser_slettede_mennesker()`)
- Audit-log på alle ændringer til `mennesker` og `aftaler`
- Se `GDPR_COMPLIANCE.md` for komplet tjekliste og go-live-krav

---

## Kontakt & adgang

- **GitHub:** https://github.com/josuapoulsen-stack/brobygger-portal
- **Prototype (live):** https://josuapoulsen-stack.github.io/brobygger-portal/
- **Azure (produktion):** Oprettes ved go-live
