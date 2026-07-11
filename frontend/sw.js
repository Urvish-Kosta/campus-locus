/* sw.js — minimal service worker.
 *
 * Two jobs:
 *   1. Cache the app shell so the portal page loads quickly on a return
 *      visit (useful on constrained guest networks).
 *   2. Provide the registration context that lets the page raise
 *      "event starting soon" notifications via showNotification().
 *
 * This is intentionally simple. Full server-pushed Web Push (VAPID +
 * a push service) is listed as a future enhancement in the roadmap; the
 * current build triggers notifications from client-side polling.
 */

const CACHE = "campus-locus-v1";
const SHELL = [
  "/",
  "/index.html",
  "/assets/styles.css",
  "/assets/app.js",
  "/assets/map.js",
  "/manifest.webmanifest",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  // Never cache API calls — they must always be fresh.
  if (new URL(request.url).pathname.startsWith("/api/")) return;

  event.respondWith(
    caches.match(request).then((cached) => cached || fetch(request))
  );
});

// If a notification is tapped, focus/open the portal.
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(clients.openWindow("/"));
});
