const CACHE = "dna-gigante-v1";
const SHELL = ["/app"];

self.addEventListener("install", e =>
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)))
);

self.addEventListener("fetch", e => {
  if (e.request.url.includes("/api/")) return; // never cache API calls
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
});
