# Deployment readiness — Brobygger Portal (.NET + Blazor)

_Opdateret: august 2026. Afløser de dele af `AZURE_SETUP.md` der stadig refererer den gamle React/FastAPI-arkitektur._

## Arkitektur nu
- **Backend:** ASP.NET Core Web API (.NET 10) + EF Core + PostgreSQL. Ligger i `backend-dotnet/`.
- **Frontend:** Blazor WebAssembly. Ligger i `frontend-blazor/`. (Den gamle React/Vite-frontend i repo-roden er udfaset.)
- **Realtid:** SSE i backend (ingen Azure SignalR).
- Backendens `infra/main.bicep` er allerede opdateret til .NET (`DOTNETCORE|10.0`). **Docs/CI/SWA-delene er delvist stadig sat op til den gamle React-frontend** — se punkterne nedenfor.

> **Gylden regel:** ingen rigtige borgerdata før auth-laget (Entra) er live. Alle 🔴-punkter skal være løst først.

---

## 🔴 Blokerende før go-live

### 1. Frontend Entra/MSAL — ✅ kodeklar, mangler tenant-config + smoke-test
Frontenden er nu wiret til MSAL (guarded): når `AzureAd:ClientId` i `frontend-blazor/wwwroot/appsettings.json` er sat (ikke `TODO...`), bruges **ægte Microsoft-login** — ellers dev-token som før (lokalt).
Implementeret: `AddMsalAuthentication`, `ApiAuthHandler` (vedhæfter Entra-token på API-kald), `/authentication`-callback, `AuthorizeRouteView` + `RedirectToLogin`. Backend skifter tilsvarende automatisk til Entra-validering når `AzureAd` er sat; roller læses fra `roles`-claim.
**Skal gøres ved deploy:**
- Udfyld `frontend-blazor/wwwroot/appsettings.json`: `AzureAd:Authority` (tenant), `ClientId`, `ApiScope`, samt `ApiBaseUrl` = prod-API-URL.
- **Smoke-test mod den rigtige tenant** (login, token, rolle-gated skærme) — MSAL-stien er ikke testet mod en tenant endnu.
- Overvej at gøre login obligatorisk (tilføj `[Authorize]` på siderne) — pt. vises UI'et, og API'et beskytter data.

### 2. Data Protection-nøgler skal persisteres (ellers datatab)
Backend krypterer helbredsnoter (art. 9) og kontonumre med ASP.NET Data Protection. Nøglerne ligger som standard **flygtigt på App Service** → krypteret data bliver **ulæseligt ved genstart/skalering**.
- Koden har nu en **prod-guard**: appen nægter at starte i Production hvis `DataProtection:BlobUri` mangler (så data aldrig korrumperes stille).
- **Skal gøres ved deploy** (kræver netadgang til nuget.org — kunne ikke tilføjes i dette miljø):
  1. Tilføj pakker til `backend-dotnet.csproj`:
     `Azure.Extensions.AspNetCore.DataProtection.Blob` + `Azure.Extensions.AspNetCore.DataProtection.Keys`.
  2. Fjern kommentaren i `Program.cs` og aktivér persisteringen:
     ```csharp
     var dp = builder.Services.AddDataProtection().SetApplicationName("BrobyggerPortal");
     var cred = new Azure.Identity.DefaultAzureCredential();
     dp.PersistKeysToAzureBlobStorage(new Uri(builder.Configuration["DataProtection:BlobUri"]!), cred);
     dp.ProtectKeysWithAzureKeyVault(new Uri(builder.Configuration["DataProtection:KeyVaultKeyId"]!), cred);
     ```
  3. Provisionér en Storage-konto + container (`dpkeys`) og en Key Vault-nøgle (`dp-key`) — se Bicep-tilføjelser nedenfor. App Service' managed identity skal have **Storage Blob Data Contributor** på containeren og **Key Vault Crypto User** på nøglen.

### 3. Entra app-registrering (opdateret til Blazor SPA + API)
1. **App registration** for API'et: Expose an API → tilføj scope (fx `access_as_user`). App roles: `Admin`, `Raadgiver`, `Oekonomi` (bemærk: koden bruger `Oekonomi`, ikke `Brobygger` til økonomi-adgang — se `[Authorize(Roles=...)]`).
2. **SPA-platform** (Blazor WASM) med redirect URIs: `https://<swa-hostname>/authentication/login-callback` og `http://localhost:5173/authentication/login-callback`.
3. Sæt i App Service: `AzureAd__TenantId`, `AzureAd__ClientId`, `AzureAd__Audience` (= API'ets client/app-id-uri).
4. Tildel brugere roller under **Enterprise applications → Users and groups**.

---

## 🟠 Vigtigt før produktion

- **Bicep — managed identity ikke koblet på App Service.** Identiteten oprettes men `appService`-ressourcen mangler `identity`-blok. Tilføj:
  ```bicep
  identity: { type: 'UserAssigned', userAssignedIdentities: { '${appServiceIdentity.id}': {} } }
  ```
- **Bicep — Storage til DP-nøgler mangler.** Tilføj en `Microsoft.Storage/storageAccounts` + blob-container `dpkeys`, en Key Vault-nøgle `dp-key`, og rolle-tildelinger (Storage Blob Data Contributor + Key Vault Crypto User) til app-identiteten. Sæt `DataProtection__BlobUri` og `DataProtection__KeyVaultKeyId` i App Service-appSettings.
- **Key Vault-referencer.** DB-password og evt. secrets bør injiceres som `@Microsoft.KeyVault(SecretUri=...)`-referencer i App Service frem for klartekst i appSettings.
- **Static Web App / CI er sat op til Vite/React.** `infra/main.bicep` (`outputLocation: 'dist'`) og `.github/workflows/azure-static-web-apps.yml` skal opdateres til **Blazor WASM**: `app_location: frontend-blazor`, `output_location: wwwroot`, .NET-build i stedet for Node. Frontendens `BaseAddress` skal pege på prod-API-URL'en (ikke `localhost:5080`).
- **App Insights ikke wiret i backend.** Tilføj `Microsoft.ApplicationInsights.AspNetCore` + `builder.Services.AddApplicationInsightsTelemetry()` og sæt `APPLICATIONINSIGHTS_CONNECTION_STRING` (findes allerede som Bicep-output).
- **CORS i prod.** `Cors:Origins` skal indeholde den rigtige SWA-URL (ikke kun localhost).
- **Dev-hemmeligheder må ikke med i prod.** `appsettings.Development.json` (`Dev:JwtSecret`) bruges kun i Development. Bekræft at `ASPNETCORE_ENVIRONMENT=Production` er sat på App Service (det er det i Bicep for `environment=prod`).
- **Sikkerhedsaudit (juni 2026).** Verificér at de udestående fund (VAPID-nøgle, PAT-i-URL) er lukket før rigtige data — se `SECURITY_CHECKLIST.md`.
- **DB-migrationer i prod.** Appen auto-migrerer kun i Development. Beslut strategi for prod: kør `dotnet ef database update` i deploy-pipelinen (anbefalet) eller aktivér `Migrate()` bevidst ved opstart.

---

## 🟡 Nice-to-have
- Automatiserede tests (matching, dublet-genkendelse, aftale-livscyklus, scope-filter).
- Prod-robusthed: `geoRedundantBackup: 'Enabled'` + `highAvailability: 'ZoneRedundant'` i Bicep.
- Outlook/Graph-integration (GraphService findes, men er ikke wiret).
- Brobygger-slim-visning (kun egne aftaler) — kræver Entra-roller live.

---

## Config-matrix (App Service appSettings i prod)
| Nøgle | Værdi |
|---|---|
| `ASPNETCORE_ENVIRONMENT` | `Production` |
| `ConnectionStrings__Postgres` | Key Vault-reference eller fuld streng m. `Ssl Mode=Require` |
| `AzureAd__TenantId` / `AzureAd__ClientId` / `AzureAd__Audience` | fra app-registreringen |
| `DataProtection__BlobUri` | `https://<konto>.blob.core.windows.net/dpkeys/keys.xml` |
| `DataProtection__KeyVaultKeyId` | `https://<kv>.vault.azure.net/keys/dp-key` |
| `Cors__Origins__0` | `https://<swa-hostname>` |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | fra App Insights |

---

## Deploy-rækkefølge (kort)
1. `az group create` + udfyld `infra/parameters.json` (DB-password).
2. Ret Bicep-punkterne ovenfor (managed identity, DP-storage, KV-key, Blazor-SWA).
3. `az deployment group create ...` → notér outputs.
4. Entra app-registrering (🔴 pkt. 3) → sæt AzureAd-settings.
5. Tilføj DP-pakker + wiring i backend (🔴 pkt. 2), byg og deploy backend til App Service.
6. Wire MSAL i Blazor (🔴 pkt. 1), sæt prod-API-URL, deploy via opdateret SWA-CI.
7. Kør DB-migrationer mod prod-DB.
8. Inviter koordinator, tildel rolle, verificér login → **først derefter** rigtige data.
