# Azure-opsætning — Brobygger Portal

Følg disse trin præcist i rækkefølge. Hele opsætningen tager ca. **2–3 timer** første gang.

---

## Forudsætninger

- [ ] Azure-adgang (Contributor-rolle på subscription eller resource group)
- [ ] Azure CLI installeret: https://learn.microsoft.com/cli/azure/install-azure-cli
- [ ] Bicep CLI: `az bicep install`
- [ ] Node.js 20+: https://nodejs.org
- [ ] Git konfigureret

---

## Trin 1 — Log ind på Azure CLI

```bash
az login
az account show  # Bekræft du er i den rigtige tenant
```

---

## Trin 2 — Opret resource group

```bash
az group create \
  --name brobygger-rg \
  --location northeurope
```

> **Vigtigt:** `northeurope` (Irland) eller `westeurope` (Holland) er de eneste EU-regioner der opfylder GDPR-krav til sundhedsdata.

---

## Trin 3 — Opdater adgangskode i parameters.json

Åbn `infra/parameters.json` og erstat:
```json
"dbAdminPassword": {
  "value": "TODO_CHANGE_THIS_PASSWORD_Min12Tegn!"
}
```
Med en stærk adgangskode (min. 12 tegn, store/små bogstaver, tal, specialtegn).

**Gem ALDRIG denne fil med den rigtige adgangskode i Git.**

---

## Trin 4 — Deploy infrastruktur

```bash
cd brobygger-portal

az deployment group create \
  --resource-group brobygger-rg \
  --template-file infra/main.bicep \
  --parameters @infra/parameters.json
```

Notér output-værdierne (bruges i næste trin):
- `staticWebAppUrl` → fx `https://orange-sea-12345.azurestaticapps.net`
- `apiUrl` → fx `https://brobygger-dev-api.azurewebsites.net`
- `dbHostname` → fx `brobygger-dev-db.postgres.database.azure.com`

---

## Trin 5 — Registrer app i Entra ID

### 5a. Opret App Registration

1. Gå til: https://portal.azure.com → **Microsoft Entra ID** → **App registrations**
2. Klik **New registration**
3. Udfyld:
   - **Name:** `Brobygger Portal`
   - **Supported account types:** `Accounts in any organizational directory and personal Microsoft accounts`
   - **Redirect URI:** Web → `https://orange-sea-12345.azurestaticapps.net` *(din Static Web App URL)*
4. Klik **Register**

### 5b. Notér Client ID og Tenant ID

På oversigts-siden:
- **Application (client) ID** → kopier → indsæt som `CLIENT_ID` i `auth/msal-config.js`
- **Directory (tenant) ID** → kopier → indsæt som `TENANT_ID` i `auth/msal-config.js`

### 5c. Tilføj redirect URIs

Klik **Authentication** i sidemenuen → under **Web** tilføj:
- `http://localhost:5173` (til lokal udvikling)
- `https://orange-sea-12345.azurestaticapps.net` (produktion)

Sæt hak ved:
- ☑ **Access tokens**
- ☑ **ID tokens**

### 5d. Opret app-roller

Klik **App roles** → **Create app role** — opret disse tre:

| Display name | Value      | Allowed member types |
|---|---|---|
| Brobygger    | Brobygger  | Users/Groups         |
| Raadgiver    | Raadgiver  | Users/Groups         |
| Admin        | Admin      | Users/Groups         |

### 5e. Aktiver External Identities (inviter brobyggere)

Gå til: **Microsoft Entra ID** → **External Identities** → **External collaboration settings**

Sæt:
- Guest user access: `Guest users have the same access as members`
- Guest invite settings: `Member users and users assigned to specific admin roles can invite`

---

## Trin 6 — Opdater msal-config.js

Åbn `auth/msal-config.js` og udfyld:
```js
CLIENT_ID:    "a1b2c3d4-...",   // Fra trin 5b
TENANT_ID:    "12345678-...",   // Fra trin 5b
REDIRECT_URI: "https://orange-sea-12345.azurestaticapps.net",
```

---

## Trin 7 — Opsæt GitHub Secrets

Gå til: GitHub repo → **Settings** → **Secrets and variables** → **Actions**

Tilføj disse secrets:

| Navn | Værdi | Hvor finder du den |
|---|---|---|
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Deployment token | Azure Portal → Static Web Apps → din app → Manage deployment token |
| `AZURE_CLIENT_ID` | Client ID | Fra trin 5b |
| `AZURE_TENANT_ID` | Tenant ID | Fra trin 5b |
| `API_URL` | API URL | Output fra trin 4 |

---

## Trin 8 — Første deployment

```bash
git add auth/msal-config.js
git commit -m "feat: configure Azure Entra ID"
git push
```

GitHub Actions kører automatisk og deployer til Azure Static Web Apps.
Følg status under: GitHub repo → **Actions**.

---

## Trin 9 — Inviter første bruger (koordinator)

1. Gå til: **Microsoft Entra ID** → **Users** → **New user** → **Invite external user**
2. Udfyld email og navn
3. Efter invitation: tildel rollen "Raadgiver" under brugerens **Assigned roles**

Brobyggere inviteres på samme måde og tildeles rollen "Brobygger".

---

## Trin 10 — Verificer

Åbn `https://orange-sea-12345.azurestaticapps.net` → klik "Log ind med Microsoft" → login med den inviterede bruger → MFA-opsætning sker automatisk første gang.

---

## Månedlig pris (dev-miljø)

| Ressource | Pris |
|---|---|
| Azure Static Web Apps (Free) | 0 kr |
| App Service B1 | ~160 kr |
| PostgreSQL B1ms | ~280 kr |
| SignalR Free | 0 kr |
| **Total** | **~440 kr/md** |

Prod-miljø med skalering: ~1.800–2.200 kr/md

---

## Hjælp og kontakt

- Azure-dokumentation: https://learn.microsoft.com/azure
- Entra ID External Identities: https://learn.microsoft.com/azure/active-directory/external-identities
- MSAL.js: https://github.com/AzureAD/microsoft-authentication-library-for-js
