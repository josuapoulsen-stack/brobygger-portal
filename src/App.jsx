/**
 * src/App.jsx — App-shell (FASE 2)
 *
 * Håndterer:
 *   • Auth-gate: uautoriserede brugere sendes til login
 *   • Rolle-routing: brobygger → BrobyggerApp, rådgiver/admin → AdminApp
 *   • Token-refresh (MSAL håndterer automatisk)
 *
 * FASE 1: Denne fil bruges IKKE — app kører via index.html + Babel CDN.
 */

import React from 'react';
import { useIsAuthenticated, useMsal, AuthenticatedTemplate, UnauthenticatedTemplate } from '@azure/msal-react';
import { loginRequest, getRoleFromClaims } from './auth/msalInstance';

// TODO (FASE 2): Importer rigtige app-komponenter når de er migreret fra HTML
// import BrobyggerApp from './components/BrobyggerApp';
// import AdminApp from './components/AdminApp';
// import LoginScreen from './components/LoginScreen';

export default function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  const account = accounts[0] ?? null;
  const role    = getRoleFromClaims(account);

  const handleLogin = () => {
    instance.loginPopup(loginRequest).catch(console.error);
  };

  const handleLogout = () => {
    instance.logoutPopup({ postLogoutRedirectUri: window.location.origin });
  };

  return (
    <>
      {/* ── Ikke logget ind ──────────────────────────────────────────── */}
      <UnauthenticatedTemplate>
        <LoginPlaceholder onLogin={handleLogin} />
      </UnauthenticatedTemplate>

      {/* ── Logget ind ───────────────────────────────────────────────── */}
      <AuthenticatedTemplate>
        {role === 'brobygger' && (
          // TODO: <BrobyggerApp user={account} onLogout={handleLogout} />
          <AppPlaceholder role="Brobygger" name={account?.name} onLogout={handleLogout} />
        )}
        {(role === 'raadgiver' || role === 'admin') && (
          // TODO: <AdminApp user={account} role={role} onLogout={handleLogout} />
          <AppPlaceholder role={role === 'admin' ? 'Admin' : 'Rådgiver'} name={account?.name} onLogout={handleLogout} />
        )}
        {!role && (
          <div style={{ padding: 32, textAlign: 'center' }}>
            <p>Din konto har ikke en gyldig rolle. Kontakt din koordinator.</p>
            <button onClick={handleLogout}>Log ud</button>
          </div>
        )}
      </AuthenticatedTemplate>
    </>
  );
}

// ── Placeholders (erstattes af rigtige komponenter i FASE 2) ──────────────────
function LoginPlaceholder({ onLogin }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', gap: 16 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700 }}>SoS Brobygger Portal</h1>
      <button
        onClick={onLogin}
        style={{ padding: '12px 24px', background: '#0078D4', color: '#fff', border: 'none', borderRadius: 8, fontSize: 16, cursor: 'pointer' }}
      >
        Log ind med Microsoft
      </button>
    </div>
  );
}

function AppPlaceholder({ role, name, onLogout }) {
  return (
    <div style={{ padding: 32 }}>
      <p>Logget ind som <strong>{name}</strong> ({role})</p>
      <p style={{ color: '#666' }}>App-komponenter migreres hertil i Fase 2.</p>
      <button onClick={onLogout}>Log ud</button>
    </div>
  );
}
