"use client"

import { Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useState, useEffect } from "react"
import { joinRoom } from "../../services/api"
import { savePlayerSession, getPlayerSession, clearPlayerSession } from "../../utils/storage"
import { ERROR_MESSAGES } from "../constants/errors"

function JoinForm() {
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

  const [sessionValid, setSessionValid] = useState(true)
  const { playerId, playerName: savedName, roomCode: savedRoomCode } = getPlayerSession()
  const hasExistingSession = Boolean(playerId && savedName && savedRoomCode)

  useEffect(() => {
    if (!hasExistingSession) return

    fetch(`${process.env.NEXT_PUBLIC_API_URL}/rooms/${savedRoomCode}`)
      .then(res => {
        if (!res.ok) {
          clearPlayerSession()
          setSessionValid(false)
        }
      })
      .catch(() => {
        clearPlayerSession()
        setSessionValid(false)
      })
  }, [])

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
      <div className="w-full max-w-md">
      {hasExistingSession && sessionValid && (
        <div className="rounded-3xl bg-zinc-900 border border-zinc-800 p-6 mb-6 text-center">
          <p className="text-zinc-400 text-sm mb-1">Partie en cours</p>
          <p className="font-black text-lg mb-4">{savedName} · {savedRoomCode}</p>
          <button
            onClick={() => router.push(`/room/${savedRoomCode}`)}
            className="w-full bg-red-600 hover:bg-red-700 transition rounded-2xl py-3 font-bold"
          >
            Reprendre ma partie
          </button>
        </div>
      )}
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
      </div>
    </main>
  )
}

export default function JoinPage() {
  return (
    <Suspense>
      <JoinForm />
    </Suspense>
  )
}