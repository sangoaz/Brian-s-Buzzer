"use client"

import { useRouter, useSearchParams } from "next/navigation"
import { useState, useEffect } from "react"
import { joinRoom } from "../../services/api"
import { savePlayerSession } from "../../utils/storage"
import { ERROR_MESSAGES } from "../constants/errors"

export default function JoinPage() {
  const router = useRouter()

  const [roomCode, setRoomCode] = useState("")
  const [name, setName] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const searchParams = useSearchParams()

  useEffect(() => {
    const code = searchParams.get("code")
    if (code) setRoomCode(code.toUpperCase())
  }, [searchParams])

  async function handleJoinRoom(event) {
    event.preventDefault()

    if (!roomCode.trim() || !name.trim()) {
      setError("Entre un pseudo et un code de salon")
      return
    }

    try {
      setLoading(true)
      setError("")

      const data = await joinRoom(roomCode.trim().toUpperCase(), name.trim())

        savePlayerSession({
        playerId: data.player_id,
        playerName: data.name,
        roomCode: data.room_code,
        })

      router.push(`/room/${data.room_code}`)
    } catch (err) {
      setError(ERROR_MESSAGES[err.message] || "Impossible de rejoindre le salon.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-zinc-950 text-white px-6">
      <form onSubmit={handleJoinRoom} className="w-full max-w-md">
        <h1 className="text-4xl font-black mb-4 text-center">
          Rejoindre une partie
        </h1>

        <div className="flex flex-col gap-4 mt-8">
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Ton pseudo"
            className="bg-zinc-900 border border-zinc-700 rounded-2xl px-4 py-4 outline-none"
          />

          <input
            value={roomCode}
            onChange={(event) => setRoomCode(event.target.value)}
            placeholder="Code du salon"
            className="bg-zinc-900 border border-zinc-700 rounded-2xl px-4 py-4 uppercase outline-none"
          />
        </div>

        {error && <p className="text-red-400 mt-4 text-center">{error}</p>}

        <button
          disabled={loading}
          className="w-full mt-6 bg-red-600 hover:bg-red-700 disabled:opacity-50 transition rounded-2xl py-4 font-bold text-lg"
        >
          {loading ? "Connexion..." : "Rejoindre"}
        </button>
      </form>
    </main>
  )
}