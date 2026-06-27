const CACHE = 'apiario-v4'
const FILES = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png', './apple-touch-icon.png']

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)))
  self.skipWaiting()
})
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ))
  self.clients.claim()
})
self.addEventListener('fetch', e => {
  // Network first: scarica sempre la versione aggiornata, fallback alla cache se offline
  e.respondWith(
    fetch(e.request)
      .then(res => {
        const copy = res.clone()
        caches.open(CACHE).then(c => c.put(e.request, copy))
        return res
      })
      .catch(() => caches.match(e.request))
  )
})
