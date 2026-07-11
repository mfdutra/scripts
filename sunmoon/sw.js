const CACHE_NAME = "sunmoon-v14";

const PRECACHE_URLS = [
  "./",
  "./index.html",
  "./app.js",
  "./manifest.json",
  "./vendor/jquery-4.0.0.min.js",
  "./vendor/suncalc-2.0.0.js",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-512-maskable.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      // cache: "reload" bypasses the HTTP cache so a stale copy is never precached
      .then((cache) => cache.addAll(
        PRECACHE_URLS.map((url) => new Request(url, { cache: "reload" }))
      ))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

const respond = async (event) => {
  // ignoreSearch: Android/Chrome may launch the installed PWA with a query
  // string appended (e.g. index.html?homescreen=1), which must still hit the
  // precached shell.
  const cached = await caches.match(event.request, { ignoreSearch: true });

  const network = fetch(event.request).then((response) => {
    if (response.ok) {
      const clone = response.clone();
      event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone))
      );
    }
    return response;
  });

  if (cached) {
    // Stale-while-revalidate: serve the cached copy now, let the network
    // update finish in the background (and swallow offline failures).
    event.waitUntil(network.catch(() => {}));
    return cached;
  }

  try {
    return await network;
  } catch (err) {
    // Offline and not in cache: for page loads, fall back to the app shell
    // instead of letting the browser show its own offline error page.
    if (event.request.mode === "navigate") {
      const shell = await caches.match("./index.html");
      if (shell) return shell;
    }
    throw err;
  }
};

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  event.respondWith(respond(event));
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "GET_VERSION" && event.ports[0]) {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
});
