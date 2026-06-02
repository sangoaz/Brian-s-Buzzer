"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"

import { getPlayerSession } from "../../../utils/storage"
import { useRoomSocket } from "../../../hooks/useRoomSocket"

import RoomHeader from "../../../components/RoomHeader"
import CurrentBuzzer from "../../../components/CurrentBuzzer"
import BuzzerButton from "../../../components/BuzzerButton"
import PlayerList from "../../../components/PlayerList"

export default function PlayerRoomPage() {
  const { roomCode } = useParams()
  const router = useRouter()

  const [playerId, setPlayerId] = useState(null)
  const [playerName, setPlayerName] = useState("")
  const [leaving, setLeaving] = useState(false)

  useEffect(() => {
    const {
      playerId: storedPlayerId,
      playerName: storedPlayerName,
    } = getPlayerSession()

    if (!storedPlayerId || !storedPlayerName) {
      router.push("/join")
      return
    }

    setPlayerId(storedPlayerId)
    setPlayerName(storedPlayerName)
  }, [router])

  const {
    roomState,
    connected,
    error,
    kicked,
    sendAction,
  } = useRoomSocket({
    roomCode,
    playerId,
  })

  useEffect(() => {
    if (!kicked) return

    router.push("/join")
  }, [kicked, router])

  function handleBuzz() {
    sendAction("buzz")
  }

  async function handleLeaveRoom() {
    if (!playerId) return

    try {
      setLeaving(true)

      await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/rooms/${roomCode}/players/${playerId}/leave`,
        {
          method: "DELETE",
        }
      )

      router.push("/join")
    } finally {
      setLeaving(false)
    }
  }

  const currentBuzzer = roomState?.current_buzzer
  const hasBuzzed = Boolean(currentBuzzer)
  const iAmTheBuzzer = currentBuzzer?.id === playerId
  const players = roomState?.players ?? []
  const scores = roomState?.scores ?? {}
  const status = roomState?.status ?? "waiting"
  const isWaiting = status === "waiting"
  const isPlaying = status === "playing"
  const isFinished = status === "finished"

  const sortedPlayers = [...players].sort(
    (a, b) => (scores[b.id] ?? 0) - (scores[a.id] ?? 0)
  )

  return (
    <main className="min-h-screen flex items-center justify-center bg-zinc-950 text-white px-6 py-10">
      <div className="w-full max-w-md text-center">
        <RoomHeader
          roomCode={roomCode}
          playerCount={players.length}
        />

        <p className="text-zinc-500 mb-6">
          Joueur :{" "}
          <span className="text-white font-bold">
            {playerName}
          </span>
        </p>

        {error && (
          <p className="text-red-400 text-sm mb-6">
            {error}
          </p>
        )}

        {isWaiting && (
          <div className="rounded-3xl bg-zinc-900 border border-zinc-800 p-6 mb-6">
            <p className="text-sm uppercase tracking-widest text-zinc-500 mb-2">
              État de la partie
            </p>

            <h2 className="text-2xl font-black">
              En attente de début
            </h2>

            <p className="text-zinc-400 mt-2">
              Attends que l’hôte lance la partie.
            </p>
          </div>
        )}

        {isPlaying && (
          <div className="rounded-3xl bg-zinc-900 border border-red-600/40 p-4 mb-6">
            <p className="text-sm uppercase tracking-widest text-red-400 font-bold">
              Partie en cours
            </p>
          </div>
        )}

        {isFinished && (
          <div className="rounded-3xl bg-zinc-900 border border-yellow-500/40 p-6 mb-6">
            <p className="text-sm uppercase tracking-widest text-yellow-400 font-bold mb-2">
              Partie terminée
            </p>

            <h2 className="text-3xl font-black mb-6">Classement final</h2>

            <ul className="space-y-3 text-left">
              {sortedPlayers.map((player, index) => (
                <li
                  key={player.id}
                  className={`flex items-center justify-between rounded-xl px-4 py-3 ${
                    player.id === playerId
                      ? "border border-yellow-500/40 bg-yellow-500/10"
                      : index === 0
                      ? "bg-yellow-500/20"
                      : "bg-zinc-800"
                  }`}
                >
                  <span className="font-bold">
                    {index === 0 && "🏆 "}
                    {index === 1 && "🥈 "}
                    {index === 2 && "🥉 "}
                    {index > 2 && `${index + 1}. `}
                    {player.name}
                    {player.id === playerId && (
                      <span className="ml-2 text-xs text-zinc-400">(toi)</span>
                    )}
                  </span>
                  <span className="text-yellow-400 font-black text-xl">
                    {scores[player.id] ?? 0}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {!isFinished && <CurrentBuzzer currentBuzzer={currentBuzzer} />}

        {!isFinished && (
          <BuzzerButton
            onBuzz={handleBuzz}
            disabled={!connected || hasBuzzed || !isPlaying}
            iAmTheBuzzer={iAmTheBuzzer}
          />
        )}

        {isWaiting && (
          <p className="mt-3 text-sm text-zinc-500">
            Le buzzer sera activé lorsque l’hôte lancera la partie.
          </p>
        )}

        <div className="rounded-3xl bg-zinc-900 border border-zinc-800 p-6 mt-6 text-left">
          <h2 className="text-2xl font-black mb-4">Joueurs</h2>

          {players.length === 0 ? (
            <p className="text-zinc-500">Aucun joueur pour le moment.</p>
          ) : (
            <ul className="space-y-3">
              {players.map((player) => (
                <li
                  key={player.id}
                  className={`flex items-center justify-between rounded-xl px-4 py-3 ${
                    player.id === playerId
                      ? "bg-zinc-700 border border-zinc-500"
                      : "bg-zinc-800"
                  }`}
                >
                  <span className="font-bold">
                    {player.name}
                    {player.id === playerId && (
                      <span className="ml-2 text-xs text-zinc-400">(toi)</span>
                    )}
                  </span>

                  <span className="text-red-400 font-black text-xl">
                    {scores[player.id] ?? 0}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <p className="mt-8 text-sm text-zinc-500">
          {connected ? "Connecté au salon" : "Connexion..."}
        </p>

        <button
          onClick={handleLeaveRoom}
          disabled={leaving}
          className="
            mt-6
            text-sm
            text-zinc-500
            hover:text-red-400
            transition
            disabled:opacity-50
          "
        >
          {leaving ? "Déconnexion..." : "Quitter le salon"}
        </button>
      </div>
    </main>
  )
}