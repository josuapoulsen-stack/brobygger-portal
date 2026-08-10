# Brobygger Portal — backend (.NET)

ASP.NET Core Web API på **.NET 10 (LTS)** med **Entity Framework Core** (PostgreSQL) og
**Microsoft.Identity.Web** til Entra ID-login. Afløser gradvist Python/FastAPI-backend'en i
`../backend/` — den beholdes som reference indtil paritet.

> **Sprogskifte (juli 2026):** Backend er skiftet fra Python/FastAPI til C#/.NET for tættere
> Microsoft-økosystem-integration (Azure, Entra, Graph) og lettere overlevering til
> Microsoft-orienterede udviklere. Frontend forbliver React.

## Hvad er bygget

- Datamodel + `DbContext` for alle ressourcer: **Mennesker, Brobyggere, Aftaler,
  Henvendelser, UCLA, Kontaktpersoner, Opkald, Stamdata, Skabeloner, Udlæg-konto**
- Fulde CRUD-controllers (kapacitetstjek, telefon-normalisering, soft-delete, rolle-gating)
- **Auth:** Entra ID (Microsoft.Identity.Web) når konfigureret; ellers HS256 **dev-token**
  (`POST /v1/auth/dev-token`) til testfasen — umulig i produktion
- **Microsoft Graph:** send mail + opret Outlook-kalenderaftaler (`Services/GraphService.cs`,
  `/v1/graph/*`, `/v1/aftaler/{id}/kalender`) — aktiveres via `Graph:Enabled`
- **Dev:** auto-migrate + fiktivt seed ved opstart (`DbSeeder`)
- JSON i snake_case (matcher `../api/openapi.yaml`)

**Mangler endnu:** art. 9-kryptering af helbredsnoter + kontonr., SSE-beskeder,
opdateret CI/CD til .NET, brugertests.

## Forudsætninger

- **.NET 10 SDK** — https://dotnet.microsoft.com/download (endnu ikke installeret på maskinen)
- **PostgreSQL** (lokal eller Azure)
- EF-værktøj: `dotnet tool install --global dotnet-ef`

## Kør lokalt

```bash
cd backend-dotnet
dotnet restore                     # henter pakker (justér evt. versioner til nyeste)

# hemmeligheder uden for git:
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:Postgres" "Host=localhost;Port=5432;Database=brobygger;Username=bbadmin;Password=DIT_PASSWORD"

# databaseskema via EF-migrations:
dotnet ef migrations add Init
dotnet ef database update

dotnet run                         # API på https://localhost:xxxx, Swagger på /swagger
```

## Entra ID

Udfyld `AzureAd` i `appsettings.json` (eller user-secrets) med `TenantId` + `ClientId` fra
app-registreringen (se `../AZURE_SETUP.md`). Uden dette afviser API'et alle kald med 401 —
det er meningen. Et dev-token-flow til testfasen (svarende til Python-backend'ens
`/v1/auth/dev-token`) tilføjes som næste skridt.

## På Azure

App Service (Linux, .NET 10) + Azure Database for PostgreSQL. Connection string og Entra-config
sættes som App Settings / Key Vault-referencer. `infra/main.bicep` skal opdateres fra
`PYTHON|3.12` til .NET-runtime, når vi deployer.

## Status: verificeret strukturelt

Koden er skrevet men **ikke bygget** (.NET SDK mangler på maskinen). Kør `dotnet build` for at
verificere — meld fejl tilbage, så retter jeg. Pakkeversioner i `.csproj` er startbud; `dotnet
restore` kan foreslå nyere.
