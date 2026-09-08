"use client"

import { useEffect } from "react"

export default function ServiceWorkerRegistration() {
  useEffect(() => {
    if (!("serviceWorker" in navigator)) return

    navigator.serviceWorker.register("/sw.js").catch(() => {
      // L'app fonctionne normalement même si l'enregistrement échoue
      // (navigateur non compatible, contexte non sécurisé en dev, etc.)
    })
  }, [])

  return null
}
