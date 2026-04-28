/**
 * src/main.jsx — Vite-indgangspunkt (FASE 2)
 *
 * I FASE 1 bruges index.html direkte (Babel Standalone + CDN).
 * I FASE 2 erstattes Babel CDN-bygget af dette Vite-indgangspunkt.
 *
 * Migrationsplan:
 *   1. Flyt komponenter fra "Brobygger portal.html" til src/components/
 *   2. Erstat <script type="text/babel"> med rigtige .jsx-filer
 *   3. Peg index.html til dette bundle i stedet for Babel CDN
 *   4. Sæt USE_BACKEND = true i src/api/index.js
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import { MsalProvider } from '@azure/msal-react';
import { msalInstance } from './auth/msalInstance';
import App from './App';

// ── Web Push service worker ───────────────────────────────────────────────────
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then(reg => console.log('[SW] Registreret:', reg.scope))
      .catch(err => console.warn('[SW] Fejl:', err));
  });
}

// ── React-app ─────────────────────────────────────────────────────────────────
const container = document.getElementById('root');
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <MsalProvider instance={msalInstance}>
      <App />
    </MsalProvider>
  </React.StrictMode>
);
