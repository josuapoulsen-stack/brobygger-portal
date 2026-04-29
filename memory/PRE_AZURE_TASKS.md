# Pre-Azure opgaveliste — SoS Brobygger Portal

Alt der kan laves **uden** Azure-adgang.
Opdateres løbende. Marker med ✅ når done.

---

## ✅ Allerede leveret

| Fil/feature | Beskrivelse |
|-------------|-------------|
| `src/api/index.js` | API-abstraktion med `USE_BACKEND=false` flag |
| `backend/main.py` | FastAPI skeleton med alle routers (503-stubs) |
| `backend/config.py` | Pydantic-Settings, alle env-vars |
| `backend/database.py` | SQLAlchemy engine + `get_db` dep + `Base` |
| `backend/models/` | Pydantic-modeller: mennesker, brobyggere, aftaler, beskeder, profil, matching, statistik |
| `backend/routers/auth.py` | Bearer token + JWKS-placeholder |
| `backend/routers/magic_link.py` | Magic link flow til brobyggere |
| `backend/migrations/001–005` | Komplet SQL-skema: tabeller, ENUMs, triggers, RLS, GDPR-anonymisering, samtykker |
| `backend/seeds/demo_data.sql` | Demo-data (brobyggere, mennesker, aftaler, beskeder, notifikationer) |
| `backend/requirements.txt` | Alle Python-afhængigheder |
| `backend/startup.txt` | Gunicorn-kommando til Azure App Service |
| `backend/orm_models.py` | SQLAlchemy ORM med alle relationer |
| `backend/services/email.py` | Microsoft Graph Mail.Send (magic link + bekræftelse) |
| `backend/services/push.py` | pywebpush til Web Push-notifikationer |
| `backend/services/signalr.py` | Azure SignalR REST API |
| `backend/services/matching.py` | Scoring-algoritme 0–100 (type/sprog/kapacitet/kontinuitet) |
| `backend/tests/conftest.py` | pytest TestClient fixture |
| `backend/tests/test_health.py` | Health + OpenAPI tests |
| `backend/tests/test_mennesker.py` | 503-assertions + FASE 2-skabelon |
| `backend/tests/test_aftaler.py` | 503-assertions |
| `backend/tests/test_beskeder.py` | 503-assertions |
| `backend/Dockerfile` | Python 3.12-slim til lokal + Azure App Service |
| `backend/alembic/env.py` + `alembic.ini` | Alembic migration-setup |
| `docker-compose.yml` | Lokal full-stack: db + migrate + seed + api + frontend |
| `package.json` | React 18 + MSAL + Vite + vite-plugin-pwa |
| `vite.config.js` | Vite 5 + PWA + proxy + chunk splitting |
| `src/main.jsx` | SW-registrering + MsalProvider |
| `src/App.jsx` | Auth gate med rolle-routing |
| `src/auth/msalInstance.js` | MSAL config + `getRoleFromClaims()` |
| `src/hooks/useApi.js` | Generisk data-fetching hook |
| `src/hooks/useSignalR.js` | SignalR hook (FASE 1: BroadcastChannel) |
| `src/hooks/usePush.js` | Web Push subscription management |
| `src/styles/tokens.js` | SoS design tokens (farver, radii, skygger, typografi) |
| `src/utils/dates.js` | Dansk datoformatering (Intl API) |
| `src/utils/sroi.js` | SROI-beregning + formattering |
| `src/components/shared/Button.jsx` | primary/secondary/ghost/danger, sm/md/lg, loading |
| `src/components/shared/Card.jsx` | Klikbar/hover, active-kant, shadow-niveau |
| `src/components/shared/Avatar.jsx` | Initialer-avatar + OnlineDot badge |
| `src/components/shared/EmptyState.jsx` | Tom-liste-visning |
| `src/components/shared/index.js` | Barrel export |
| `src/components/brobygger/BrobyggerApp.jsx` | Shell: TabBar + placeholder-skærme + notif-badge |
| `src/components/brobygger/HomeScreen.jsx` | Placeholder (return null) |
| `src/components/brobygger/KalenderScreen.jsx` | Placeholder (return null) |
| `src/components/brobygger/MessagesList.jsx` | Placeholder (return null) |
| `src/components/brobygger/ProfileScreen.jsx` | Placeholder (return null) |
| `src/components/admin/DesktopMennesker.jsx` | Placeholder |
| `src/components/admin/DesktopBrobyggere.jsx` | Placeholder |
| `src/components/admin/MatchingFlow.jsx` | Placeholder |
| `src/components/admin/IntakeFlow.jsx` | Placeholder |
| `public/sw.js` | Service worker: app-shell caching, push handler, background sync |
| `staticwebapp.config.json` | SPA fallback + security headers |
| `.env.example` | Alle env-vars dokumenteret med VAPID-nøgler |
| `GDPR_COMPLIANCE.md` | Art. 9-tjekliste + DPIA + 10-punkt go-live |
| `PRIVACY_POLICY.md` | GDPR-privatlivspolitik-skabelon |
| `openapi.yaml` | Komplet OpenAPI 3.1 spec |
| `infra/main.bicep` | Azure IaC: SWA + App Service + PostgreSQL + Key Vault + App Insights |
| `.github/workflows/deploy.yml` | Frontend CI/CD til Azure SWA |
| `.github/workflows/deploy-backend.yml` | Backend CI/CD: pytest + zip + App Service |
| `.gitignore` | .env, node_modules, dist, venv, *.url |

---

## 🔴 Høj prioritet — lille indsats

| # | Status | Fil | Beskrivelse |
|---|--------|-----|-------------|
| 1 | ✅ | `.gitattributes` | Stopper CRLF-advarsel på hvert commit |
| 2 | ✅ | `README.md` | Developer setup-guide: Docker Compose, env, test, deploy |
| 3 | ✅ | `src/utils/validation.js` | CPR-tjek, dansk telefon, email — bruges i alle formularer |

## 🟠 Mellemstort — klar gevinst

| # | Status | Fil | Beskrivelse |
|---|--------|-----|-------------|
| 4 | ✅ | `src/components/shared/TopBar.jsx` | Bruges på alle skærme; mangler i shared-laget |
| 5 | ✅ | `src/components/shared/Pill.jsx` | Status-pills brugt overalt (aktiv, ny, afventer, ...) |
| 6 | ✅ | `src/components/shared/Icon.jsx` | Fælles ikon-komponent (erstatter inline SVG i alle filer) |
| 7 | ✅ | `src/components/brobygger/HomeScreen.jsx` | Rigtig migration fra prototype (FASE 1, ingen backend) |
| 8 | ✅ | `backend/tests/test_matching.py` | Unit-test af scoring-algoritme (ingen database) |
| 9 | ✅ | `src/hooks/useMatching.js` | React hook der wrapper matching-API + loading/error |

## 🟡 Nyttigt — kan vente

| # | Status | Fil | Beskrivelse |
|---|--------|-----|-------------|
| 10 | ✅ | `src/components/admin/AdminApp.jsx` | Admin/rådgiver shell parallel til BrobyggerApp |
| 11 | ✅ | `Makefile` | `make dev`, `make migrate`, `make seed`, `make test` |
| 12 | ✅ | `backend/alembic/versions/001–005` | Konverteret til rigtige Alembic Python-migrations |
| 13 | ✅ | `src/components/brobygger/KalenderScreen.jsx` | Fuld migration: månedsgrid, dag-valg, aftaler/vagter |
| 14 | ✅ | `src/components/brobygger/ProfileScreen.jsx` | Fuld migration: profil, notif-toggles, push, privatliv |
| 15 | ✅ | `src/components/admin/MatchingFlow.jsx` | Rigtig migration fra prototype (manuel matching) |
| 16 | ✅ | `src/components/admin/IntakeFlow.jsx` | Rigtig migration fra prototype (ny-menneske-flow) |
| 17 | ✅ | `backend/middleware/logging.py` | Request-logging + correlation ID |
| 18 | ✅ | `src/components/shared/ErrorBoundary.jsx` | React error boundary til graceful fejlhåndtering |

---

## Noter
- `USE_BACKEND = false` i `src/api/index.js` holder prototype-data isoleret
- Skift til `true` kun når **alle** endpoints er klar med rigtig DB-logik
- Alle backend-routers returnerer `503` indtil FASE 2
- Docker Compose: `docker compose up` starter hele stacken lokalt
