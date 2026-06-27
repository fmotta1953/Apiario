const CACHE = 'apiario-v9'
const STATIC = ['./manifest.json', './icon-192.png', './icon-512.png', './apple-touch-icon.png']

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(STATIC)))
  self.skipWaiting()
})
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ))
  self.clients.claim()
})
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url)
  // index.html: sempre dal network (mai dalla cache), fallback cache solo se offline
  if(url.pathname === '/' || url.pathname.endsWith('/index.html') || url.pathname.endsWith('/Apiario/')) {
    e.respondWith(
      fetch(e.request, {cache: 'no-store'})
        .then(res => res)
        .catch(() => caches.match('./index.html'))
    )
    return
  }
  // Tutto il resto: network first, fallback cache
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
