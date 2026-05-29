/**
 * src/App.tsx — App-shell placeholder (TypeScript)
 *
 * Vise-placeholder mens komponenterne migreres fra "Brobygger portal.html".
 * Erstatter src/App.jsx i Vite-bygget.
 *
 * FASE 2: Erstat dette med AuthGate + rolle-routing (brobygger/rådgiver/admin).
 */

import React from 'react';
import { AuthGate } from './auth/AuthGate';

// ── v2-stiltokens ─────────────────────────────────────────────────────────────
const styles = {
  page: {
    minHeight: '100vh',
    background: '#FAFAF8',           // paper bg
    fontFamily: "'JetBrains Mono', monospace, system-ui, sans-serif",
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '2rem',
  } as React.CSSProperties,

  card: {
    background: '#FFFFFF',
    border: '1.5px solid #E5E3DE',
    borderRadius: '16px',
    padding: '3rem 2.5rem',
    maxWidth: '520px',
    width: '100%',
    boxShadow: '0 2px 16px rgba(0,0,0,0.06)',
    textAlign: 'center' as const,
  } as React.CSSProperties,

  badge: {
    display: 'inline-block',
    background: '#4A7C59',
    color: '#fff',
    fontSize: '11px',
    fontWeight: 600,
    letterSpacing: '0.08em',
    padding: '4px 10px',
    borderRadius: '999px',
    marginBottom: '1.5rem',
    textTransform: 'uppercase' as const,
  } as React.CSSProperties,

  heading: {
    fontSize: '1.75rem',
    fontWeight: 700,
    color: '#1A1A1A',
    marginBottom: '0.75rem',
    lineHeight: 1.2,
  } as React.CSSProperties,

  sub: {
    fontSize: '0.875rem',
    color: '#6B6860',
    lineHeight: 1.6,
    marginBottom: '2rem',
  } as React.CSSProperties,

  statusList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
    textAlign: 'left' as const,
    borderTop: '1px solid #E5E3DE',
    paddingTop: '1.5rem',
  } as React.CSSProperties,

  statusItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.625rem',
    fontSize: '0.8125rem',
    color: '#3D3C3A',
    padding: '0.375rem 0',
  } as React.CSSProperties,

  dot: (done: boolean): React.CSSProperties => ({
    width: 8,
    height: 8,
    borderRadius: '50%',
    flexShrink: 0,
    background: done ? '#4A7C59' : '#D4A853',
  }),
};

// ── Statusoversigt over migreringen ──────────────────────────────────────────
const STATUS_ITEMS: Array<{ label: string; done: boolean }> = [
  { label: 'Vite + React + TypeScript setup', done: true },
  { label: 'TypeScript datamodel (src/types)', done: true },
  { label: 'Auth-stub (useAuth + AuthGate)', done: true },
  { label: 'MSAL-konfiguration klar til swap', done: true },
  { label: 'Komponent-migration fra HTML', done: false },
  { label: 'Azure Static Web Apps CI/CD', done: false },
  { label: 'Entra ID kobling (echte MSAL)', done: false },
];

// ── Placeholder-komponent ─────────────────────────────────────────────────────
function AppPlaceholder(): React.ReactElement {
  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <span style={styles.badge}>v2 — Vite build</span>

        <h1 style={styles.heading}>Brobygger Portal</h1>
        <p style={styles.sub}>
          Vite-bygget er klar. Komponenterne migreres løbende fra prototypen
          (<code>Brobygger portal.html</code>) til denne TypeScript-kodebase.
        </p>

        <ul style={styles.statusList}>
          {STATUS_ITEMS.map(({ label, done }) => (
            <li key={label} style={styles.statusItem}>
              <span style={styles.dot(done)} />
              {label}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

// ── App-root ──────────────────────────────────────────────────────────────────
export default function App(): React.ReactElement {
  return (
    <AuthGate>
      <AppPlaceholder />
    </AuthGate>
  );
}
