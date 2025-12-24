// Simple Service Worker for Noltrion
const CACHE_NAME = 'noltrion-v2'; // Increment version to force update
const urlsToCache = [
    '/static/css/styles.css',
    '/static/js/app.js',
    '/static/vendors/bootstrap/css/bootstrap.min.css',
    '/static/vendors/fontawesome/css/all.min.css'
    // Removed '/' to avoid caching the dynamic dashboard/attendance page
];

// Install event
self.addEventListener('install', function (event) {
    self.skipWaiting(); // Force activation
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function (cache) {
                return cache.addAll(urlsToCache);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cache => {
                    if (cache !== CACHE_NAME) {
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
    return self.clients.claim();
});

// Fetch event
self.addEventListener('fetch', function (event) {
    // Network-first for HTML, Cache-first for static assets
    if (event.request.headers.get('accept').includes('text/html')) {
        event.respondWith(
            fetch(event.request)
                .catch(() => caches.match(event.request))
        );
    } else {
        event.respondWith(
            caches.match(event.request)
                .then(function (response) {
                    return response || fetch(event.request);
                })
        );
    }
});