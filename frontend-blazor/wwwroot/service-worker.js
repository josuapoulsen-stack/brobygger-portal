// Brobygger Portal — service worker.
// Formål: gør appen installerbar (PWA) og lad den åbne offline.
// Strategi: NETWORK-FIRST — online hentes altid friskt indhold (så opdateringer
// slår igennem med det samme); cachen bruges kun som fallback når man er offline.
// API-kald (anden origin, fx backend på :5080) røres aldrig.

const CACHE = 'brobygger-shell-v2';
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
        caches.keys()
            .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (e) => {
    const req = e.request;
    if (req.method !== 'GET') return;

    const url = new URL(req.url);
    // Kun samme origin — backend-API/SSE går altid direkte til nettet.
    if (url.origin !== self.location.origin) return;

    // Network-first: hent friskt, opdatér cache; ved fejl (offline) brug cache.
    e.respondWith(
        fetch(req)
            .then((res) => {
                if (res && res.status === 200 && res.type === 'basic') {
                    const copy = res.clone();
                    caches.open(CACHE).then((c) => c.put(req, copy));
                }
                return res;
            })
            .catch(() => caches.match(req).then((cached) =>
                cached || (req.mode === 'navigate' ? caches.match('index.html') : Response.error())
            ))
    );
});
