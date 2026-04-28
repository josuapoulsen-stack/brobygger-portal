import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

/**
 * vite.config.js — SoS Brobygger Portal
 *
 * Bruges ved FASE 2 (Vite-migration fra single-file HTML).
 * I prototype-tilstand bruges index.html stadig direkte.
 *
 * Build: npm run build → dist/
 * Deploy: GitHub Actions → Azure Static Web Apps
 */
export default defineConfig({
  plugins: [
    react(),

    // ── PWA / Service Worker ──────────────────────────────────────────────
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['logo.png', 'favicon.ico'],
      manifest: {
        name: 'SoS Brobygger Portal',
        short_name: 'Brobygger',
        description: 'Støt op om en bro til livet',
        theme_color: '#4A7C59',
        background_color: '#F9FAFB',
        display: 'standalone',
        start_url: '/',
        icons: [
          { src: 'logo.png', sizes: '192x192', type: 'image/png' },
          { src: 'logo.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' },
        ],
      },
      workbox: {
        // Cache API-svar i 5 minutter
        runtimeCaching: [
          {
            urlPattern: /\/v1\//,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: { maxAgeSeconds: 300 },
            },
          },
        ],
      },
    }),
  ],

  // ── Dev-server ────────────────────────────────────────────────────────────
  server: {
    port: 5173,
    proxy: {
      // Videresend /v1/* til FastAPI under udvikling
      '/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },

  // ── Build ─────────────────────────────────────────────────────────────────
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        // Chunk-splits for bedre caching
        manualChunks: {
          'react-vendor':  ['react', 'react-dom'],
          'msal':          ['@azure/msal-browser', '@azure/msal-react'],
        },
      },
    },
  },

  // ── Env-variabler (VITE_* eksponeres til frontend) ────────────────────────
  // Definerede i .env.local (lokalt) eller GitHub Secrets (CI/CD):
  //   VITE_CLIENT_ID    → Azure Entra ID klient-ID
  //   VITE_TENANT_ID    → Azure Entra ID tenant-ID
  //   VITE_API_URL      → Backend URL (https://brobygger-dev-api.azurewebsites.net)
  //   VITE_ENVIRONMENT  → development | staging | production
  //   VITE_VAPID_PUBLIC_KEY → Web Push public key
});
