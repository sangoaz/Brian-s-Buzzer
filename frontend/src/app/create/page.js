"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import { createRoom } from "../../services/api"

export default function CreatePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  async function handleCreateRoom() {
    try {
      setLoading(true)
      setError("")

      const data = await createRoom()

      router.push(`/room/${data.room_code}/host`)
    } catch (err) {
      setError("Impossible de créer le salon")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-zinc-950 text-white px-6">
      <div className="w-full max-w-md text-center">
        <h1 className="text-4xl font-black mb-4">Créer une partie</h1>

        <p className="text-zinc-400 mb-8">
          Crée un salon et affiche l’écran hôte pour gérer le buzzer.
        </p>

        {error && <p className="text-red-400 mb-4">{error}</p>}

        <button
          onClick={handleCreateRoom}
          disabled={loading}
          className="w-full bg-red-600 hover:bg-red-700 disabled:opacity-50 transition rounded-2xl py-4 font-bold text-lg"
        >
          {loading ? "Création..." : "Créer le salon"}
        </button>
      </div>
    </main>
  )
}