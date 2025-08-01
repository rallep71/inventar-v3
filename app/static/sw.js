// app/static/sw.js
const CACHE_NAME = 'inventar-v3-cache-v1';
const urlsToCache = [
  '/',
  '/auth/login',
  '/static/src/css/app.css',
  '/static/src/js/modules/app.js',
  '/static/src/js/modules/toast.js',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.css',
  'https://unpkg.com/htmx.org@1.9.10'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  if (!event.request.url.startsWith(self.location.origin)) return;
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then(response => {
        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then(cache => {
          if (response.status === 200) {
            cache.put(event.request, responseToCache);
          }
        });
        return response;
      })
      .catch(() => {
        return caches.match(event.request);
      })
  );
});
