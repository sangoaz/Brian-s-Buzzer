"use client"

import { useEffect, useRef, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { QRCodeSVG } from "qrcode.react"
import YouTube from "react-youtube"

import { useRoomSocket } from "../../../../hooks/useRoomSocket"

import RoomHeader from "../../../../components/RoomHeader"
import CurrentBuzzer from "../../../../components/CurrentBuzzer"
import ResetButton from "../../../../components/ResetButton"
import PlayerList from "../../../../components/PlayerList"

export default function HostRoomPage() {
  const { roomCode } = useParams()
  const router = useRouter()

  const [hostId, setHostId] = useState(null)
  const [historyOpen, setHistoryOpen] = useState(false)
  const [youtubeUrl, setYoutubeUrl] = useState("")
  const playerRef = useRef(null)

  function extractVideoId(url) {
    const patterns = [
      /[?&]v=([^&]+)/,
      /youtu\.be\/([^?+]+)/,
      /youtube\.com\/embed\/([^?]+)/,
    ]
    for (const pattern of patterns) {
      const match = url.match(pattern)
      if (match) return match[1]
    }
    return null
  }

  const videoId = extractVideoId(youtubeUrl)

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
  const buzzHistory = roomState?.buzz_history ?? {}

  const status = roomState?.status ?? "waiting"

  const isWaiting = status === "waiting"
  const isPlaying = status === "playing"
  const isFinished = status === "finished"

  const sortedPlayers = [...players].sort(
    (a, b) => (scores[b.id] ?? 0) - (scores[a.id] ?? 0)
  )

  const hasCurrentBuzzer = Boolean(currentBuzzer)

  useEffect(() => {
    if (currentBuzzer && playerRef.current) {
      playerRef.current.pauseVideo()
    }
  }, [currentBuzzer])

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

  function handleRestartGame() {
    const confirmed = window.confirm("Lancer une nouvelle partie ? Les scores seront remis à zéro.")
    if (!confirmed) return
    sendAction("restart_game")
  }

  function handleValidateAnswer() {
    sendAction("validate_answer")
    if (playerRef.current) playerRef.current.playVideo()
  }

  function handleRejectAnswer() {
    sendAction("reject_answer")
    if (playerRef.current) playerRef.current.playVideo()
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

            <div className="mb-6">
              <input
                type="text"
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                placeholder="Lien YouTube (optionnel)"
                className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500"
              />
            </div>

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

            <button
              onClick={handleRestartGame}
              className="w-full mt-6 bg-red-600 hover:bg-red-700 transition rounded-2xl py-4 font-bold text-lg"
            >
              Nouvelle partie
            </button>
          </div>
        )}

        {videoId && !isFinished && (
          <div className="rounded-3xl overflow-hidden mb-6">
            <YouTube
              videoId={videoId}
              onReady={(e) => { playerRef.current = e.target }}
              opts={{ width: "100%", playerVars: { autoplay: 0 } }}
            />
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

        {(isPlaying || isFinished) && Object.keys(buzzHistory).length > 0 && (
          <div className="rounded-3xl bg-zinc-900 border border-zinc-800 mb-6 text-left overflow-hidden">
            <button
              onClick={() => setHistoryOpen(v => !v)}
              className="w-full flex items-center justify-between p-6 hover:bg-zinc-800 transition"
            >
              <h2 className="text-2xl font-black">Historique des buzzers</h2>
              <span className="text-zinc-400 text-xl">{historyOpen ? "▲" : "▼"}</span>
            </button>

            {historyOpen && (
              <ul className="space-y-3 px-6 pb-6">
                {Object.entries(buzzHistory)
                  .sort(([a], [b]) => Number(b) - Number(a))
                  .map(([round, buzzers]) => (
                    <li key={round}>
                      <p className="text-xs uppercase tracking-widest text-zinc-500 mb-1">
                        Manche {round}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {buzzers.map((buzzer, index) => (
                          <span
                            key={index}
                            className="bg-zinc-800 rounded-lg px-3 py-1 text-sm font-bold"
                          >
                            {index + 1}. {buzzer.name}
                          </span>
                        ))}
                      </div>
                    </li>
                  ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </main>
  )
}