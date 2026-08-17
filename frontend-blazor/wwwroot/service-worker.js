// Brobygger Portal — service worker.
// Formål: gør appen installerbar (PWA) og cache app-shellet, så den åbner offline.
// API-kald (anden origin, fx backend på :5080) caches ALDRIG — de skal altid være live.

const CACHE = 'brobygger-shell-v1';
const CORE = [
    './',
    'index.html',
    'app.css',
    'manifest.webmanifest',
    'icons/icon-192.png',
    'icons/icon-512.png',
    'icons/apple-touch-icon.png',
];

self.addEventListener('install', (e) => {
    e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (e) => {
    const req = e.request;
    if (req.method !== 'GET') return;

    const url = new URL(req.url);
    // Kun samme origin caches — backend-API/SSE går altid direkte til nettet.
    if (url.origin !== self.location.origin) return;

    // Navigation (SPA): network-first med offline-fallback til app-shellet.
    if (req.mode === 'navigate') {
        e.respondWith(fetch(req).catch(() => caches.match('index.html')));
        return;
    }

    // Øvrige statiske filer (inkl. _framework): stale-while-revalidate.
    e.respondWith(
        caches.match(req).then((cached) => {
            const net = fetch(req).then((res) => {
                if (res && res.status === 200 && res.type === 'basic') {
                    const copy = res.clone();
                    caches.open(CACHE).then((c) => c.put(req, copy));
                }
                return res;
            }).catch(() => cached);
            return cached || net;
        })
    );
});
