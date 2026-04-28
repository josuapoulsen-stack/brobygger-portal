/**
 * msal-config.js — Microsoft Entra ID (Azure AD B2C External Identities)
 *
 * UDFYLD disse tre værdier når Azure-adgang er klar:
 *
 *   CLIENT_ID  → Azure Portal → App registrations → din app → "Application (client) ID"
 *   TENANT_ID  → Azure Portal → App registrations → din app → "Directory (tenant) ID"
 *   REDIRECT   → Skal matche præcist det du har sat under "Redirect URIs" i Azure
 *
 * Trin for at finde disse værdier — se AZURE_SETUP.md
 */

const MSAL_CONFIG = {
  // ─── UDFYLD HER ────────────────────────────────────────────────────────────
  CLIENT_ID:    "TODO_CLIENT_ID",       // fx "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  TENANT_ID:    "TODO_TENANT_ID",       // fx "12345678-abcd-ef01-2345-6789abcdef01"
  REDIRECT_URI: "https://josuapoulsen-stack.github.io/brobygger-portal/",
  // ───────────────────────────────────────────────────────────────────────────

  // Roller defineret i Azure AD — skal matche app-rollerne i Azure Portal
  ROLES: {
    BROBYGGER: "Brobygger",
    RAADGIVER: "Raadgiver",
    ADMIN:     "Admin",
  },

  // Token-levetid (dage) — konfigurerbart i Azure Conditional Access
  SESSION_DAYS: 30,
};

// ── MSAL PublicClientApplication config ──────────────────────────────────────
export const msalConfig = {
  auth: {
    clientId:    MSAL_CONFIG.CLIENT_ID,
    authority:   `https://login.microsoftonline.com/${MSAL_CONFIG.TENANT_ID}`,
    redirectUri: MSAL_CONFIG.REDIRECT_URI,
  },
  cache: {
    cacheLocation:     "localStorage",  // Husker session på enheden
    storeAuthStateInCookie: false,
  },
};

// ── Login-scopes ──────────────────────────────────────────────────────────────
export const loginRequest = {
  scopes: ["openid", "profile", "email"],
};

// ── Token-request (til API-kald) ──────────────────────────────────────────────
export const tokenRequest = {
  scopes: [`api://${MSAL_CONFIG.CLIENT_ID}/access_as_user`],
};

// ── Hjælpefunktion: map Azure-rolle til app-rolle ─────────────────────────────
export function getRoleFromClaims(idTokenClaims) {
  const roles = idTokenClaims?.roles || [];
  if (roles.includes(MSAL_CONFIG.ROLES.ADMIN))     return "admin";
  if (roles.includes(MSAL_CONFIG.ROLES.RAADGIVER)) return "raadgiver";
  if (roles.includes(MSAL_CONFIG.ROLES.BROBYGGER)) return "brobygger";
  return "brobygger"; // Fallback: ny bruger der endnu ikke har fået rolle
}

// ── Er konfigurationen udfyldt? ───────────────────────────────────────────────
export const IS_CONFIGURED =
  MSAL_CONFIG.CLIENT_ID !== "TODO_CLIENT_ID" &&
  MSAL_CONFIG.TENANT_ID !== "TODO_TENANT_ID";
