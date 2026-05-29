/**
 * src/main.tsx — Vite-indgangspunkt (TypeScript)
 *
 * Erstatter src/main.jsx.
 * I prototype-tilstand bruges "Brobygger portal.html" direkte (Babel CDN).
 * Dette er Vite-build-indgangspunktet til FASE 2.
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

// ── Web Push service worker ───────────────────────────────────────────────────
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/brobygger-portal/sw.js')
      .then((reg) => console.log('[SW] Registreret:', reg.scope))
      .catch((err) => console.warn('[SW] Fejl:', err));
  });
}

// ── React-app ─────────────────────────────────────────────────────────────────
const container = document.getElementById('root');
if (!container) throw new Error('Root-element #root ikke fundet i DOM');

const root = createRoot(container);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
