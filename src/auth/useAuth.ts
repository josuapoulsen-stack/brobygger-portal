/**
 * src/auth/useAuth.ts — Mock auth-hook med demo-personas
 *
 * Mock-implementering der bruger sessionStorage i stedet for rigtig MSAL.
 * Giver `useAuth()` samme API som den rigtige hook vil have.
 *
 * Demo-personas:
 *   - Admin:      Sarah Andersen (admin@socialsundhed.org)
 *   - Rådgiver:   Linda Thomsen  (linda@socialsundhed.org)
 *   - Brobygger:  Maja Holmberg  (maja@socialsundhed.org)
 *
 * Skift til rigtig MSAL:
 *   1. Installer: npm install @azure/msal-browser @azure/msal-react
 *   2. Omskriv useAuth() til at bruge useMsal() + useIsAuthenticated()
 *   3. Wrap app i <MsalProvider instance={msalInstance}> i main.tsx
 *   4. Sæt VITE_CLIENT_ID og VITE_TENANT_ID i .env.local
 */

import { useState, useEffect, useCallback } from 'react';
import type { User } from '../types';
import { HovedSaede } from '../types';

// ── Demo-personas (bruges indtil Entra ID er koblet til) ─────────────────────
export const DEMO_PERSONAS: Record<string, User> = {
  admin: {
    id:         'u-admin',
    firstName:  'Sarah',
    lastName:   'Andersen',
    email:      'sarah@socialsundhed.org',
    role:       'admin',
    hovedsaede: HovedSaede.Aarhus,
  },
  raadgiver: {
    id:         'u-1',
    firstName:  'Linda',
    lastName:   'Thomsen',
    email:      'linda@socialsundhed.org',
    role:       'raadgiver',
    hovedsaede: HovedSaede.Aarhus,
  },
  brobygger: {
    id:         'u-2',
    firstName:  'Maja',
    lastName:   'Holmberg',
    email:      'maja@socialsundhed.org',
    role:       'brobygger',
    hovedsaede: HovedSaede.Aarhus,
  },
};

const SESSION_KEY = 'sos_mock_user';

// ── Return-type for useAuth ───────────────────────────────────────────────────
export interface AuthState {
  /** Den indloggede bruger — null hvis ikke autentificeret */
  user: User | null;

  /** Er brugeren autentificeret? */
  isAuthenticated: boolean;

  /** Log ind med den valgte demo-persona (erstattes af MSAL loginPopup/loginRedirect) */
  login: (rolle?: keyof typeof DEMO_PERSONAS) => void;

  /** Log ud og ryd sessionStorage */
  logout: () => void;

  /** Skift til en anden demo-persona uden at logge ud (praktisk til rollestests) */
  switchPersona: (rolle: keyof typeof DEMO_PERSONAS) => void;

  /** Liste af tilgængelige demo-personas */
  personas: typeof DEMO_PERSONAS;
}

/**
 * useAuth — mock-auth-hook med demo-personas
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

  const _setPersona = useCallback((persona: User): void => {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(persona));
    setUser(persona);
  }, []);

  const login = useCallback((rolle: keyof typeof DEMO_PERSONAS = 'raadgiver'): void => {
    // Replace mock with real useMsal() from @azure/msal-react when Entra ID is ready
    const persona = DEMO_PERSONAS[rolle] ?? DEMO_PERSONAS.raadgiver;
    _setPersona(persona);
  }, [_setPersona]);

  const switchPersona = useCallback((rolle: keyof typeof DEMO_PERSONAS): void => {
    const persona = DEMO_PERSONAS[rolle];
    if (persona) _setPersona(persona);
  }, [_setPersona]);

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
    switchPersona,
    personas: DEMO_PERSONAS,
  };
}
