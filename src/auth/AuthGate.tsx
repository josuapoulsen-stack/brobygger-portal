/**
 * src/auth/AuthGate.tsx — Auth-gate komponent
 *
 * Viser login-skærm til uautoriserede brugere.
 * Wrapper autentificeret indhold og stiller bruger-context til rådighed.
 *
 * Replace mock with real useMsal() from @azure/msal-react when Entra ID is ready.
 */

import React, { createContext, useContext } from 'react';
import { useAuth } from './useAuth';
import type { User } from '../types';

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Context: aktuel bruger
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

interface UserContextValue {
  user: User;
  logout: () => void;
}

const UserContext = createContext<UserContextValue | null>(null);

/**
 * useCurrentUser — hent den indloggede bruger fra context.
 * Kaster en fejl hvis kaldt udenfor en <AuthGate>.
 */
export function useCurrentUser(): UserContextValue {
  const ctx = useContext(UserContext);
  if (!ctx) {
    throw new Error('useCurrentUser skal bruges inde i <AuthGate>');
  }
  return ctx;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Styles (v2 palette: paper + forest green + JetBrains Mono)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const css = {
  overlay: {
    minHeight: '100vh',
    background: '#FAFAF8',
    fontFamily: "'JetBrains Mono', monospace, system-ui, sans-serif",
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '2rem',
  } as React.CSSProperties,

  card: {
    background: '#FFFFFF',
    border: '1.5px solid #E5E3DE',
    borderRadius: '20px',
    padding: '3rem 2.5rem',
    maxWidth: '400px',
    width: '100%',
    boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
    textAlign: 'center' as const,
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    gap: '1.25rem',
  } as React.CSSProperties,

  logo: {
    width: 56,
    height: 56,
    background: '#4A7C59',
    borderRadius: '14px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1.75rem',
    marginBottom: '0.25rem',
  } as React.CSSProperties,

  heading: {
    fontSize: '1.375rem',
    fontWeight: 700,
    color: '#1A1A1A',
    margin: 0,
  } as React.CSSProperties,

  sub: {
    fontSize: '0.8125rem',
    color: '#6B6860',
    lineHeight: 1.6,
    margin: 0,
  } as React.CSSProperties,

  msBtn: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.625rem',
    width: '100%',
    padding: '0.75rem 1.5rem',
    background: '#0078D4',
    color: '#FFFFFF',
    border: 'none',
    borderRadius: '10px',
    fontSize: '0.9375rem',
    fontWeight: 600,
    fontFamily: 'inherit',
    cursor: 'pointer',
    transition: 'background 0.15s',
    marginTop: '0.5rem',
  } as React.CSSProperties,

  divider: {
    width: '100%',
    borderTop: '1px solid #E5E3DE',
    margin: '0.5rem 0',
  } as React.CSSProperties,

  disclaimer: {
    fontSize: '0.6875rem',
    color: '#9E9C97',
    lineHeight: 1.5,
    margin: 0,
  } as React.CSSProperties,
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Microsoft-logo SVG (forenklet)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function MsLogo(): React.ReactElement {
  return (
    <svg width="18" height="18" viewBox="0 0 21 21" aria-hidden="true">
      <rect x="1"  y="1"  width="9" height="9" fill="#F25022" />
      <rect x="11" y="1"  width="9" height="9" fill="#7FBA00" />
      <rect x="1"  y="11" width="9" height="9" fill="#00A4EF" />
      <rect x="11" y="11" width="9" height="9" fill="#FFB900" />
    </svg>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Login-skærm
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

interface LoginCardProps {
  onLogin: () => void;
}

function LoginCard({ onLogin }: LoginCardProps): React.ReactElement {
  return (
    <div style={css.overlay}>
      <div style={css.card}>
        {/* Logo */}
        <div style={css.logo}>🌉</div>

        <h1 style={css.heading}>Brobygger Portal</h1>
        <p style={css.sub}>
          Log ind med din Social & Sundhed Microsoft-konto for at fortsætte.
        </p>

        <hr style={css.divider} />

        <button
          style={css.msBtn}
          onClick={onLogin}
          type="button"
          onMouseEnter={(e) => { (e.currentTarget.style.background = '#006CBE'); }}
          onMouseLeave={(e) => { (e.currentTarget.style.background = '#0078D4'); }}
        >
          <MsLogo />
          Log ind med Microsoft
        </button>

        <p style={css.disclaimer}>
          Kun autoriseret personale hos Social &amp; Sundhed har adgang.
          <br />
          MFA aktiveres automatisk via Microsoft Authenticator.
        </p>
      </div>
    </div>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// AuthGate — hoved-komponent
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

interface AuthGateProps {
  children: React.ReactNode;
}

/**
 * AuthGate — wrapper der kræver autentificering.
 *
 * - Ikke autentificeret → viser <LoginCard>
 * - Autentificeret → renderer children og gør bruger tilgængelig via context
 *
 * Replace mock with real useMsal() from @azure/msal-react when Entra ID is ready.
 */
export function AuthGate({ children }: AuthGateProps): React.ReactElement {
  const { user, isAuthenticated, login, logout } = useAuth();

  if (!isAuthenticated || user === null) {
    return <LoginCard onLogin={login} />;
  }

  return (
    <UserContext.Provider value={{ user, logout }}>
      {children}
    </UserContext.Provider>
  );
}
