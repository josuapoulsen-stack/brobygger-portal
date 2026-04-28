/**
 * src/auth/msalInstance.js
 *
 * Opretter MSAL PublicClientApplication til brug i hele appen.
 * Konfiguration hentes fra Vite env-variabler (VITE_CLIENT_ID, VITE_TENANT_ID).
 *
 * Svarer til auth/msal-config.js men i Vite-modulformat.
 */

import { PublicClientApplication, LogLevel } from '@azure/msal-browser';

const clientId  = import.meta.env.VITE_CLIENT_ID  || 'TODO_CLIENT_ID';
const tenantId  = import.meta.env.VITE_TENANT_ID  || 'TODO_TENANT_ID';
const redirectUri = window.location.origin;

export const msalConfig = {
  auth: {
    clientId,
    authority: `https://login.microsoftonline.com/${tenantId}`,
    redirectUri,
    postLogoutRedirectUri: redirectUri,
  },
  cache: {
    cacheLocation: 'localStorage',
    storeAuthStateInCookie: false,
  },
  system: {
    loggerOptions: {
      loggerCallback: (level, message) => {
        if (import.meta.env.DEV) console.log(`[MSAL ${level}]`, message);
      },
      logLevel: import.meta.env.DEV ? LogLevel.Info : LogLevel.Error,
    },
  },
};

export const loginRequest = {
  scopes: ['openid', 'profile', 'email', 'User.Read'],
};

export const tokenRequest = {
  scopes: [`api://${clientId}/access_as_user`],
};

/** Hjælper: udtræk rolle fra token-claims */
export function getRoleFromClaims(account) {
  const roles = account?.idTokenClaims?.roles ?? [];
  if (roles.includes('Admin'))      return 'admin';
  if (roles.includes('Raadgiver'))  return 'raadgiver';
  if (roles.includes('Brobygger'))  return 'brobygger';
  return null;
}

export const msalInstance = new PublicClientApplication(msalConfig);

// Håndtér redirect-respons (bruges ved loginRedirect-flow)
msalInstance.initialize().then(() => {
  msalInstance.handleRedirectPromise().catch(console.error);
});
