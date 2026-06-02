"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { QRCodeSVG } from "qrcode.react"

import { useRoomSocket } from "../../../../hooks/useRoomSocket"

import RoomHeader from "../../../../components/RoomHeader"
import CurrentBuzzer from "../../../../components/CurrentBuzzer"
import ResetButton from "../../../../components/ResetButton"
import PlayerList from "../../../../components/PlayerList"

export default function HostRoomPage() {
  const { roomCode } = useParams()
  const router = useRouter()

  const [hostId, setHostId] = useState(null)

  useEffect(() => {
    const storedHostId = localStorage.getItem("hostId")
    const storedRoomCode = localStorage.getItem("hostRoomCode")

    if (!storedHostId || storedRoomCode !== roomCode) {
      router.push("/create")
      return
    }

    setHostId(storedHostId)
  }, [roomCode, router])

  const {
    roomState,
    connected,
    error,
    sendAction,
  } = useRoomSocket({
    roomCode,
    playerId: hostId,
  })

  const currentBuzzer = roomState?.current_buzzer
  const players = roomState?.players ?? []
  const scores = roomState?.scores ?? {}

  const status = roomState?.status ?? "waiting"

  const isWaiting = status === "waiting"
  const isPlaying = status === "playing"
  const isFinished = status === "finished"

  const sortedPlayers = [...players].sort(
    (a, b) => (scores[b.id] ?? 0) - (scores[a.id] ?? 0)
  )

  const hasCurrentBuzzer = Boolean(currentBuzzer)

  function handleStartGame() {
    sendAction("start_game")
  }

  function handleReset() {
    sendAction("reset")
  }

  function handleEndGame() {
    const confirmed = window.confirm("Terminer la partie et afficher le classement final ?")
    if (!confirmed) return
    sendAction("end_game")
  }

  function handleValidateAnswer() {
    sendAction("validate_answer")
  }

  function handleRejectAnswer() {
    sendAction("reject_answer")
  }

  async function handleKickPlayer(playerId) {
    const player = players.find((p) => p.id === playerId)
    const confirmed = window.confirm(
      `Voulez-vous déconnecter ${player?.name ?? "ce joueur"} ?`
    )

    if (!confirmed) return

    await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/rooms/${roomCode}/players/${playerId}?host_id=${hostId}`,
      {
        method: "DELETE",
      }
    )
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-white px-6 py-10">
      <div className="max-w-4xl mx-auto text-center">
        <RoomHeader
          roomCode={roomCode}
          playerCount={players.length}
        />

        <p className="text-sm text-zinc-500 mb-4">
          {connected
            ? "Écran hôte connecté"
            : "Connexion..."}
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

            <p className="text-zinc-400 mt-2 mb-6">
              Les joueurs peuvent rejoindre le salon.
            </p>

            <div className="flex justify-center mb-6">
              <QRCodeSVG
                value={`${process.env.NEXT_PUBLIC_APP_URL}/join?code=${roomCode}`}
                size={180}
                bgColor="#18181b"
                fgColor="#ffffff"
              />
            </div>

            <button
              onClick={handleStartGame}
              disabled={!connected || players.length === 0}
              className="
                w-full
                bg-red-600
                hover:bg-red-700
                disabled:opacity-50
                disabled:cursor-not-allowed
                transition
                rounded-2xl
                py-4
                font-bold
                text-lg
              "
            >
              Lancer la partie
            </button>
          </div>
        )}

        {isPlaying && (
          <div className="rounded-3xl bg-zinc-900 border border-red-600/40 p-4 mb-6">
            <p className="text-sm uppercase tracking-widest text-red-400 font-bold">
              Partie en cours
            </p>

            <p className="text-zinc-400 mt-2 mb-4">
              Manche {roomState?.round ?? 1}
            </p>

            <button
              onClick={handleEndGame}
              className="w-full bg-zinc-700 hover:bg-zinc-600 transition rounded-2xl py-3 font-bold text-sm"
            >
              Terminer la partie
            </button>
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
                    index === 0 ? "bg-yellow-500/20 border border-yellow-500/40" : "bg-zinc-800"
                  }`}
                >
                  <span className="font-bold">
                    {index === 0 && "🏆 "}
                    {index === 1 && "🥈 "}
                    {index === 2 && "🥉 "}
                    {index > 2 && `${index + 1}. `}
                    {player.name}
                  </span>
                  <span className="text-yellow-400 font-black text-xl">
                    {scores[player.id] ?? 0}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <CurrentBuzzer
          currentBuzzer={currentBuzzer}
          large
        />

        {hasCurrentBuzzer && (
          <div className="flex gap-4 mb-8">
            <button
              onClick={handleValidateAnswer}
              className="
                flex-1
                bg-green-600
                hover:bg-green-700
                transition
                rounded-2xl
                py-4
                font-black
                text-lg
              "
            >
              ✅ Bonne réponse
            </button>

            <button
              onClick={handleRejectAnswer}
              className="
                flex-1
                bg-zinc-800
                hover:bg-zinc-700
                transition
                rounded-2xl
                py-4
                font-black
                text-lg
              "
            >
              ❌ Mauvaise réponse
            </button>
          </div>
        )}

        <ResetButton
          onReset={handleReset}
          disabled={!isPlaying}
        />

        <div className="rounded-3xl bg-zinc-900 border border-zinc-800 p-6 mb-6 text-left">
          <h2 className="text-2xl font-black mb-4">
            Scores
          </h2>

          {players.length === 0 ? (
            <p className="text-zinc-500">
              Aucun joueur connecté.
            </p>
          ) : (
            <ul className="space-y-3">
              {players.map((player) => (
                <li
                  key={player.id}
                  className="
                    flex
                    items-center
                    justify-between
                    bg-zinc-800
                    rounded-xl
                    px-4
                    py-3
                  "
                >
                  <span className="font-bold">
                    {player.name}
                  </span>

                  <span className="text-red-400 font-black text-xl">
                    {scores[player.id] ?? 0}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <PlayerList
          players={players}
          onKickPlayer={handleKickPlayer}
        />
      </div>
    </main>
  )
}