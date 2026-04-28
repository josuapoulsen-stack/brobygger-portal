/**
 * public/sw.js — SoS Brobygger Portal Service Worker
 *
 * Håndterer:
 *   1. Web Push-notifikationer (baggrunds-push fra backend)
 *   2. Offline-cache af app-shell (skeleton vises ved ingen net)
 *   3. Baggrunds-sync (sendte beskeder gemmes og synkroniseres når net er tilbage)
 *
 * Registreres fra src/main.jsx ved app-start.
 * Vite PWA-plugin genererer en service worker oveni ved build (workbox).
 * Denne fil supplerer med Push-logik som workbox ikke håndterer.
 */

const CACHE_NAME = 'sos-shell-v1';
const APP_SHELL  = ['/', '/index.html', '/logo.png'];

// ── Installation — cache app-shell ───────────────────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

// ── Aktivering — ryd gamle caches ────────────────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// ── Fetch — network first, cache fallback ────────────────────────────────────
self.addEventListener('fetch', (event) => {
  // API-kald går altid til netværket
  if (event.request.url.includes('/v1/')) return;

  event.respondWith(
    fetch(event.request)
      .catch(() => caches.match(event.request).then(r => r || caches.match('/index.html')))
  );
});

// ── Web Push ──────────────────────────────────────────────────────────────────
self.addEventListener('push', (event) => {
  if (!event.data) return;

  let data;
  try {
    data = event.data.json();
  } catch {
    data = { title: 'SoS Brobygger Portal', body: event.data.text() };
  }

  const { title, body, icon, badge, tag, url } = data;

  event.waitUntil(
    self.registration.showNotification(title || 'SoS Brobygger Portal', {
      body:  body  || '',
      icon:  icon  || '/logo.png',
      badge: badge || '/logo.png',
      tag:   tag   || 'sos-notif',
      data:  { url: url || '/' },
      vibrate: [200, 100, 200],
      requireInteraction: false,
    })
  );
});

// ── Notifikationsklik — åbn eller fokusér app ─────────────────────────────────
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  const targetUrl = event.notification.data?.url || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
      // Find åbent vindue og fokusér
      for (const client of windowClients) {
        if (client.url.includes(self.registration.scope) && 'focus' in client) {
          client.navigate(targetUrl);
          return client.focus();
        }
      }
      // Intet åbent vindue — åbn nyt
      return clients.openWindow(targetUrl);
    })
  );
});

// ── Baggrunds-sync — send beskeder der fejlede ───────────────────────────────
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-messages') {
    event.waitUntil(syncPendingMessages());
  }
});

async function syncPendingMessages() {
  // Hent afventende beskeder fra IndexedDB (TODO: implementér i FASE 2)
  // const pending = await getPendingFromIDB('messages');
  // for (const msg of pending) {
  //   await fetch('/v1/beskeder/threads/' + msg.threadId + '/messages', {
  //     method: 'POST', headers: { ... }, body: JSON.stringify(msg),
  //   });
  // }
  console.log('[SW] sync-messages kørte (placeholder)');
}
