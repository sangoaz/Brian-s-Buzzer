"use client"

import { useMemo } from "react"
import { useParams } from "next/navigation"

import { useRoomSocket } from "../../../../hooks/useRoomSocket"

import RoomHeader from "../../../../components/RoomHeader"
import CurrentBuzzer from "../../../../components/CurrentBuzzer"
import ResetButton from "../../../../components/ResetButton"
import PlayerList from "../../../../components/PlayerList"

export default function HostRoomPage() {
  const { roomCode } = useParams()

  const hostId = useMemo(() => {
    return `host-${crypto.randomUUID()}`
  }, [])

  const { roomState, connected, error, sendAction } = useRoomSocket({
    roomCode,
    playerId: hostId,
  })

  const currentBuzzer = roomState?.current_buzzer
  const players = roomState?.players ?? []

  function handleReset() {
    sendAction("reset")
  }

  async function handleKickPlayer(playerId) {
    await fetch(`http://127.0.0.1:8000/rooms/${roomCode}/players/${playerId}`, {
      method: "DELETE",
    })
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-white px-6 py-10">
      <div className="max-w-4xl mx-auto text-center">
        <RoomHeader
          roomCode={roomCode}
          playerCount={players.length}
        />

        <p className="text-sm text-zinc-500 mb-4">
          {connected ? "Écran hôte connecté" : "Connexion..."}
        </p>

        {error && (
          <p className="text-red-400 text-sm mb-6">
            {error}
          </p>
        )}

        <CurrentBuzzer currentBuzzer={currentBuzzer} large />

        <ResetButton onReset={handleReset} />

        <PlayerList
          players={players}
          onKickPlayer={handleKickPlayer}
        />
      </div>
    </main>
  )
}