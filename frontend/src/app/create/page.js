"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import { createRoom } from "../../services/api"

const ROUNDS_OPTIONS = [5, 10, 15, 20]
const BLOCK_DURATION_OPTIONS = [3, 5, 10]

export default function CreatePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const [maxRoundsEnabled, setMaxRoundsEnabled] = useState(false)
  const [maxRounds, setMaxRounds] = useState(10)

  const [blockOnWrong, setBlockOnWrong] = useState(false)
  const [blockDuration, setBlockDuration] = useState(5)

  const [penaltyOnWrong, setPenaltyOnWrong] = useState(false)
  const [lockOnStart, setLockOnStart] = useState(false)

  async function handleCreateRoom() {
    try {
      setLoading(true)
      setError("")

      const settings = {
        max_rounds: maxRoundsEnabled ? maxRounds : null,
        block_on_wrong: blockOnWrong,
        block_duration: blockDuration,
        penalty_on_wrong: penaltyOnWrong,
        lock_on_start: lockOnStart,
      }

      const data = await createRoom(settings)

      localStorage.setItem("hostId", data.host_id)
      localStorage.setItem("hostRoomCode", data.room_code)

      router.push(`/room/${data.room_code}/host`)
    } catch (err) {
      setError("Impossible de créer le salon")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-zinc-950 text-white px-6 py-10">
      <div className="w-full max-w-md">
        <h1 className="text-4xl font-black mb-2 text-center">
          Créer une partie
        </h1>

        <p className="text-zinc-400 mb-8 text-center">
          Configure les règles avant de lancer le salon.
        </p>

        {/* Nombre de manches */}
        <div className="rounded-3xl bg-zinc-900 border border-zinc-800 p-6 mb-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="font-black text-lg">Nombre de manches</h2>
              <p className="text-zinc-400 text-sm">Illimité par défaut</p>
            </div>

            <button
              onClick={() => setMaxRoundsEnabled(v => !v)}
              className={`w-12 h-6 rounded-full transition ${
                maxRoundsEnabled ? "bg-red-600" : "bg-zinc-700"
              }`}
            >
              <div className={`w-5 h-5 bg-white rounded-full mx-auto transition-transform ${
                maxRoundsEnabled ? "translate-x-3" : "-translate-x-3"
              }`} />
            </button>
          </div>

          {maxRoundsEnabled && (
            <div className="flex gap-2">
              {ROUNDS_OPTIONS.map((option) => (
                <button
                  key={option}
                  onClick={() => setMaxRounds(option)}
                  className={`flex-1 py-2 rounded-xl font-bold text-sm transition ${
                    maxRounds === option
                      ? "bg-red-600 text-white"
                      : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Bloquer le buzzer sur mauvaise réponse */}
        <div className="rounded-3xl bg-zinc-900 border border-zinc-800 p-6 mb-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="font-black text-lg">Bloquer sur mauvaise réponse</h2>
              <p className="text-zinc-400 text-sm">
                Le joueur ne peut plus buzzer pendant {blockDuration}s
              </p>
            </div>

            <button
              onClick={() => setBlockOnWrong(v => !v)}
              className={`w-12 h-6 rounded-full transition ${
                blockOnWrong ? "bg-red-600" : "bg-zinc-700"
              }`}
            >
              <div className={`w-5 h-5 bg-white rounded-full mx-auto transition-transform ${
                blockOnWrong ? "translate-x-3" : "-translate-x-3"
              }`} />
            </button>
          </div>

          {blockOnWrong && (
            <div className="flex gap-2">
              {BLOCK_DURATION_OPTIONS.map((option) => (
                <button
                  key={option}
                  onClick={() => setBlockDuration(option)}
                  className={`flex-1 py-2 rounded-xl font-bold text-sm transition ${
                    blockDuration === option
                      ? "bg-red-600 text-white"
                      : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
                  }`}
                >
                  {option}s
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Pénalité sur mauvaise réponse */}
        <div className="rounded-3xl bg-zinc-900 border border-zinc-800 p-6 mb-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-black text-lg">Pénalité sur mauvaise réponse</h2>
              <p className="text-zinc-400 text-sm">Le joueur perd 1 point</p>
            </div>

            <button
              onClick={() => setPenaltyOnWrong(v => !v)}
              className={`w-12 h-6 rounded-full transition ${
                penaltyOnWrong ? "bg-red-600" : "bg-zinc-700"
              }`}
            >
              <div className={`w-5 h-5 bg-white rounded-full mx-auto transition-transform ${
                penaltyOnWrong ? "translate-x-3" : "-translate-x-3"
              }`} />
            </button>
          </div>
        </div>

        {/* Verrouiller à la manche */}
        <div className="rounded-3xl bg-zinc-900 border border-zinc-800 p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-black text-lg">Verrouiller à la manche</h2>
              <p className="text-zinc-400 text-sm">Empêche de rejoindre une partie en cours</p>
            </div>

            <button
              onClick={() => setLockOnStart(v => !v)}
              className={`w-12 h-6 rounded-full transition ${
                lockOnStart ? "bg-red-600" : "bg-zinc-700"
              }`}
            >
              <div className={`w-5 h-5 bg-white rounded-full mx-auto transition-transform ${
                lockOnStart ? "translate-x-3" : "-translate-x-3"
              }`} />
            </button>
          </div>
        </div>

        {error && (
          <p className="text-red-400 mb-4 text-center">{error}</p>
        )}

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
