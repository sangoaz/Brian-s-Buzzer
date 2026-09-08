// Service worker de Brian's Buzzer.
//
// L'app est temps réel (WebSocket) : on ne cherche pas à rendre le jeu
// jouable hors-ligne, ça n'aurait pas de sens. Le but ici est plus modeste :
// - charger l'app quasi instantanément au retour (cache des fichiers statiques)
// - éviter un écran blanc si le réseau coupe pendant la navigation
//
// Stratégie "network-first" : le réseau est toujours tenté en premier pour ne
// jamais servir une version périmée de l'app ; le cache ne sert que de secours.
// Seules les requêtes GET de même origine sont concernées : les appels à
// l'API backend (autre origine) et le WebSocket ne sont jamais interceptés.

const CACHE_NAME = "brians-buzzer-v1"

self.addEventListener("install", () => {
  self.skipWaiting()
})

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
        )
      )
      .then(() => self.clients.claim())
  )
})

self.addEventListener("fetch", (event) => {
  const { request } = event
  const url = new URL(request.url)

  const isSameOriginGet =
    request.method === "GET" && url.origin === self.location.origin

  if (!isSameOriginGet) {
    return
  }

  event.respondWith(
    fetch(request)
      .then((response) => {
        const responseCopy = response.clone()
        caches.open(CACHE_NAME).then((cache) => cache.put(request, responseCopy))
        return response
      })
      .catch(() => caches.match(request))
  )
})
