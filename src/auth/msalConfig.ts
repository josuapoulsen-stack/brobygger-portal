/**
 * src/auth/msalConfig.ts — MSAL-konfiguration (placeholder)
 *
 * Placeholder-konfiguration klar til swap med Azure Entra ID.
 * Erstat REPLACE_WITH_* værdier med rigtige Azure App Registration-værdier.
 *
 * I Vite-miljø bruges VITE_CLIENT_ID og VITE_TENANT_ID env-variabler
 * (defineres i .env.local eller GitHub Secrets).
 */

/** MSAL-konfigurationsstruktur (spejler @azure/msal-browser Configuration) */
export interface MsalConfigShape {
  auth: {
    clientId: string;
    authority: string;
    redirectUri: string;
  };
  cache: {
    cacheLocation: 'sessionStorage' | 'localStorage';
    storeAuthStateInCookie: boolean;
  };
}

// Placeholder — swap clientId/tenantId when Azure app registration is created
export const msalConfig: MsalConfigShape = {
  auth: {
    clientId:    import.meta.env.VITE_CLIENT_ID  ?? 'REPLACE_WITH_AZURE_APP_CLIENT_ID',
    authority:   `https://login.microsoftonline.com/${import.meta.env.VITE_TENANT_ID ?? 'REPLACE_WITH_TENANT_ID'}`,
    redirectUri: typeof window !== 'undefined' ? window.location.origin : '/',
  },
  cache: {
    cacheLocation:        'sessionStorage',
    storeAuthStateInCookie: false,
  },
};

/** Login-scope til Microsoft Graph */
export const loginRequest = {
  scopes: ['openid', 'profile', 'email', 'User.Read'],
} as const;

/** API-scope til backend (udfyldes når Azure API-registrering er klar) */
export const apiTokenRequest = {
  scopes: [`api://${msalConfig.auth.clientId}/access_as_user`],
} as const;

/**
 * Udtræk brugerrolle fra MSAL-token-claims.
 * Entra ID grupperer roller i `idTokenClaims.roles[]`.
 */
export function getRoleFromClaims(
  claims: Record<string, unknown> | null | undefined
): 'admin' | 'raadgiver' | 'brobygger' | null {
  const roles = (claims?.roles as string[] | undefined) ?? [];
  if (roles.includes('Admin'))      return 'admin';
  if (roles.includes('Raadgiver'))  return 'raadgiver';
  if (roles.includes('Brobygger'))  return 'brobygger';
  return null;
}
