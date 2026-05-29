/**
 * src/auth/useAuth.ts — Mock auth-hook
 *
 * Mock-implementering der bruger sessionStorage i stedet for rigtig MSAL.
 * Giver `useAuth()` samme API som den rigtige hook vil have.
 *
 * Replace mock with real useMsal() from @azure/msal-react when Entra ID is ready.
 *
 * Skift:
 *   1. Installer: npm install @azure/msal-browser @azure/msal-react
 *   2. Omskriv useAuth() til at bruge useMsal() + useIsAuthenticated()
 *   3. Wrap app i <MsalProvider instance={msalInstance}> i main.tsx
 *   4. Sæt VITE_CLIENT_ID og VITE_TENANT_ID i .env.local
 */

import { useState, useEffect, useCallback } from 'react';
import type { User } from '../types';
import { HovedSaede } from '../types';

// ── Mock-bruger (bruges indtil Entra ID er koblet til) ────────────────────────
const MOCK_USER: User = {
  id:          'u-1',
  firstName:   'Linda',
  lastName:    'Thomsen',
  email:       'linda@socialsundhed.org',
  role:        'raadgiver',
  hovedsaede:  HovedSaede.Aarhus,
};

const SESSION_KEY = 'sos_mock_user';

// ── Return-type for useAuth ───────────────────────────────────────────────────
export interface AuthState {
  /** Den indloggede bruger — null hvis ikke autentificeret */
  user: User | null;

  /** Er brugeren autentificeret? */
  isAuthenticated: boolean;

  /** Log ind med mock-bruger (erstattes af MSAL loginPopup/loginRedirect) */
  login: () => void;

  /** Log ud og ryd sessionStorage */
  logout: () => void;
}

/**
 * useAuth — mock-auth-hook
 *
 * Returnerer auth-state baseret på sessionStorage.
 * Udskiftes med `useMsal()` + `useIsAuthenticated()` fra @azure/msal-react
 * når Entra ID-integrationen er klar.
 */
export function useAuth(): AuthState {
  const [user, setUser] = useState<User | null>(() => {
    try {
      const stored = sessionStorage.getItem(SESSION_KEY);
      return stored ? (JSON.parse(stored) as User) : null;
    } catch {
      return null;
    }
  });

  // Synkroniser state hvis sessionStorage ændres i andre tabs
  useEffect(() => {
    const handleStorage = (evt: StorageEvent): void => {
      if (evt.key !== SESSION_KEY) return;
      if (evt.newValue === null) {
        setUser(null);
      } else {
        try {
          setUser(JSON.parse(evt.newValue) as User);
        } catch {
          setUser(null);
        }
      }
    };
    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, []);

  const login = useCallback((): void => {
    // Replace mock with real useMsal() from @azure/msal-react when Entra ID is ready
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(MOCK_USER));
    setUser(MOCK_USER);
  }, []);

  const logout = useCallback((): void => {
    sessionStorage.removeItem(SESSION_KEY);
    setUser(null);
    window.location.reload();
  }, []);

  return {
    user,
    isAuthenticated: user !== null,
    login,
    logout,
  };
}
