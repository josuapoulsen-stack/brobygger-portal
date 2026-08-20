// ═══════════════════════════════════════════════════════════════════════════════
// main.bicep — Brobygger Portal, Azure infrastructure
//
// Deploy med:
//   az group create --name brobygger-rg --location northeurope
//   az deployment group create \
//     --resource-group brobygger-rg \
//     --template-file infra/main.bicep \
//     --parameters @infra/parameters.json
//
// Ressourcer der oprettes:
//   • Azure Static Web Apps  (Blazor WASM-frontend)
//   • Azure App Service      (.NET 10 Web API-backend)
//   • Azure Database for PostgreSQL Flexible Server
//   • Realtids-beskeder via SSE i .NET-backend (ingen separat tjeneste)
// ═══════════════════════════════════════════════════════════════════════════════

@description('Miljø: dev, staging eller prod')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Azure-region — skal være EU af GDPR-hensyn')
param location string = 'northeurope'

@description('Applikationsnavn — bruges som præfiks på alle ressourcer')
param appName string = 'brobygger'

@description('PostgreSQL administrator-brugernavn')
param dbAdminUsername string = 'bbadmin'

@description('PostgreSQL administrator-adgangskode')
@secure()
param dbAdminPassword string  // Sættes i parameters.json eller Key Vault

@description('GitHub repository (org/repo) til Static Web Apps CI/CD')
param githubRepo string = 'josuapoulsen-stack/brobygger-portal'

@description('GitHub branch der deployes')
param githubBranch string = 'master'

// ── Navngivning ───────────────────────────────────────────────────────────────
var prefix = '${appName}-${environment}'
var tags = {
  application: 'Brobygger Portal'
  environment: environment
  owner:       'SoS'
  gdpr:        'EU-data-only'
}

// ─────────────────────────────────────────────────────────────────────────────
// 1. Azure Static Web Apps — Blazor WASM-frontend
// ─────────────────────────────────────────────────────────────────────────────
resource staticWebApp 'Microsoft.Web/staticSites@2022-09-01' = {
  name: '${prefix}-web'
  location: location  // Static Web Apps har begrænsede regioner — se Azure docs
  tags: tags
  sku: {
    name: 'Free'   // Gratis tier er tilstrækkeligt til prototype/MVP
    tier: 'Free'
  }
  properties: {
    repositoryUrl:  'https://github.com/${githubRepo}'
    branch:         githubBranch
    buildProperties: {
      appLocation:    'frontend-blazor'   // Blazor WASM-projektet
      outputLocation: 'wwwroot'           // Blazor publish-output
      apiLocation:    ''                  // Ingen Azure Functions (separat App Service)
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 2. App Service Plan + App Service — .NET 10 Web API-backend
// ─────────────────────────────────────────────────────────────────────────────
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: '${prefix}-plan'
  location: location
  tags: tags
  sku: {
    name: environment == 'prod' ? 'B2' : 'B1'  // B1: ~160 kr/md, B2: ~320 kr/md
    tier: 'Basic'
  }
  kind: 'linux'
  properties: {
    reserved: true  // Linux
  }
}

resource appService 'Microsoft.Web/sites@2022-09-01' = {
  name: '${prefix}-api'
  location: location
  tags: tags
  kind: 'app,linux'
  // Managed identity → adgang til Key Vault + Storage (Data Protection-nøgler)
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${appServiceIdentity.id}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly:    true
    siteConfig: {
      linuxFxVersion: 'DOTNETCORE|10.0'
      appSettings: [
        { name: 'ASPNETCORE_ENVIRONMENT', value: environment == 'prod' ? 'Production' : 'Development' }
        {
          // .NET læser ConnectionStrings:Postgres — dobbelt-underscore = sektions-separator
          name:  'ConnectionStrings__Postgres'
          value: 'Host=${database.properties.fullyQualifiedDomainName};Database=brobygger;Username=${dbAdminUsername};Password=${dbAdminPassword};Ssl Mode=Require'
        }
        // Realtids-beskeder: SSE i egen backend (Azure SignalR udgår, se IMPLEMENTERINGSPLAN 3.2)
        // Entra ID — udfyld fra app-registreringen (se AZURE_SETUP.md)
        { name: 'AzureAd__TenantId', value: 'TODO_TENANT_ID' }
        { name: 'AzureAd__ClientId', value: 'TODO_CLIENT_ID' }
        { name: 'AzureAd__Audience', value: 'TODO_CLIENT_ID' }
        // Monitoring
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsights.properties.ConnectionString }
        // Data Protection-nøgler (KRITISK) — udfyld når storage-konto + KV-nøgle er oprettet, se DEPLOYMENT_READINESS.md
        { name: 'DataProtection__BlobUri', value: 'TODO_https://<konto>.blob.core.windows.net/dpkeys/keys.xml' }
        { name: 'DataProtection__KeyVaultKeyId', value: 'TODO_https://${prefix}-kv.vault.azure.net/keys/dp-key' }
      ]
      cors: {
        allowedOrigins: [
          'https://${staticWebApp.properties.defaultHostname}'
          'http://localhost:5173'  // Vite dev-server
        ]
      }
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 3. Azure Database for PostgreSQL Flexible Server
// ─────────────────────────────────────────────────────────────────────────────
resource database 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: '${prefix}-db'
  location: location
  tags: tags
  sku: {
    name: environment == 'prod' ? 'Standard_D2ds_v4' : 'Standard_B1ms'
    tier: environment == 'prod' ? 'GeneralPurpose' : 'Burstable'
    // B1ms: ~280 kr/md (dev), D2ds: ~900 kr/md (prod)
  }
  properties: {
    administratorLogin:         dbAdminUsername
    administratorLoginPassword: dbAdminPassword
    version:                    '16'
    storage: {
      storageSizeGB: environment == 'prod' ? 64 : 32
    }
    backup: {
      backupRetentionDays:  environment == 'prod' ? 14 : 7
      geoRedundantBackup:   'Disabled'  // Aktiver i prod hvis kritiske data
    }
    highAvailability: {
      mode: 'Disabled'  // Aktiver i prod: 'ZoneRedundant' (fordobler pris)
    }
  }
}

// Database firewall: tillad kun App Service
resource dbFirewallAzureServices 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-03-01-preview' = {
  parent: database
  name:   'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress:   '0.0.0.0'
  }
}

// Opret database
resource brobyggerDb 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-03-01-preview' = {
  parent: database
  name:   'brobygger'
  properties: {
    charset:   'UTF8'
    collation: 'da_DK.utf8'
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 4. Realtids-beskeder: SSE i egen FastAPI-backend — ingen separat Azure-tjeneste
//    (Azure SignalR udgik juni 2026, se IMPLEMENTERINGSPLAN.md 3.2)
// ─────────────────────────────────────────────────────────────────────────────

// ─────────────────────────────────────────────────────────────────────────────
// 5. Azure Key Vault — hemmeligheder (DB-adgangskode, VAPID, JWT-secret)
// ─────────────────────────────────────────────────────────────────────────────
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name:     '${prefix}-kv'
  location: location
  tags:     tags
  properties: {
    sku:         { family: 'A', name: 'standard' }
    tenantId:    tenant().tenantId
    // App Service får adgang via managed identity (nedenfor)
    accessPolicies: []
    enableRbacAuthorization:      true    // brug RBAC frem for access policies
    enableSoftDelete:             true
    softDeleteRetentionInDays:    90
    enablePurgeProtection:        true
  }
}

// Gem DB-adgangskode i Key Vault (erstatter hardkodet i appSettings)
resource kvSecretDb 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name:   'db-admin-password'
  properties: { value: dbAdminPassword }
}

resource kvSecretJwt 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name:   'jwt-secret'
  properties: { value: 'TODO_GENERATE_32CHAR_SECRET' }
}

resource kvSecretVapid 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name:   'vapid-private-key'
  properties: { value: 'TODO_SET_VAPID_PRIVATE_KEY' }
}

// App Service Managed Identity → Key Vault Reader
resource appServiceIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name:     '${prefix}-api-identity'
  location: location
  tags:     tags
}

// Key Vault Secrets User role til App Service
resource kvRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name:  guid(keyVault.id, appServiceIdentity.id, '4633458b-17de-408a-b874-0445c86b69e6')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId:      appServiceIdentity.properties.principalId
    principalType:    'ServicePrincipal'
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 6. Application Insights — monitoring + fejlsporing
// ─────────────────────────────────────────────────────────────────────────────
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name:     '${prefix}-logs'
  location: location
  tags:     tags
  properties: {
    sku:               { name: 'PerGB2018' }
    retentionInDays:   30
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name:     '${prefix}-ai'
  location: location
  tags:     tags
  kind:     'web'
  properties: {
    Application_Type:             'web'
    WorkspaceResourceId:          logAnalytics.id
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery:     'Enabled'
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Outputs — bruges af GitHub Actions og msal-config.js
// ─────────────────────────────────────────────────────────────────────────────
output staticWebAppUrl          string = 'https://${staticWebApp.properties.defaultHostname}'
output apiUrl                   string = 'https://${appService.properties.defaultHostName}'
output dbHostname               string = database.properties.fullyQualifiedDomainName
output keyVaultName             string = keyVault.name
output appInsightsConnectionStr string = appInsights.properties.ConnectionString

// Månedlig estimeret pris (dev-miljø, DKK ca.):
//   Static Web Apps:  0 kr  (Free tier)
//   App Service B1:  160 kr
//   PostgreSQL B1ms: 280 kr
//   Realtid (SSE):     0 kr  (kører i App Service, ingen separat tjeneste)
//   Key Vault:         ~5 kr  (10.000 operations/md gratis)
//   App Insights:      ~0 kr  (5 GB/md gratis)
//   ─────────────────────────────
//   Total dev:       ~445 kr/md
//
//   Prod (med HA + B2): ~1.800-2.200 kr/md
