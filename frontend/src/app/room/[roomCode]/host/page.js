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

  const { roomState, connected, sendAction } = useRoomSocket({
    roomCode,
    playerId: hostId,
  })

  function handleReset() {
    sendAction("reset")
  }

  const currentBuzzer = roomState?.current_buzzer
  const players = roomState?.players || []

  return (
    <main className="min-h-screen bg-zinc-950 text-white px-6 py-10">
      <div className="max-w-4xl mx-auto text-center">
        <RoomHeader roomCode={roomCode} subtitle="Code du salon" />

        <p className="text-sm text-zinc-500 mb-10">
          {connected ? "Écran hôte connecté" : "Connexion..."}
        </p>

        <CurrentBuzzer currentBuzzer={currentBuzzer} large />

        <ResetButton onReset={handleReset} />

        <PlayerList players={players} />
      </div>
    </main>
  )
}