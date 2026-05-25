"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"

import { getPlayerSession } from "../../../utils/storage"
import { useRoomSocket } from "../../../hooks/useRoomSocket"

import RoomHeader from "../../../components/RoomHeader"
import CurrentBuzzer from "../../../components/CurrentBuzzer"
import BuzzerButton from "../../../components/BuzzerButton"

export default function PlayerRoomPage() {
  const { roomCode } = useParams()
  const router = useRouter()

  const [playerId, setPlayerId] = useState(null)
  const [playerName, setPlayerName] = useState("")

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

  const currentBuzzer = roomState?.current_buzzer
  const hasBuzzed = Boolean(currentBuzzer)
  const players = roomState?.players ?? []

  return (
    <main className="min-h-screen flex items-center justify-center bg-zinc-950 text-white px-6">
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

        <CurrentBuzzer currentBuzzer={currentBuzzer} />

        <BuzzerButton
          onBuzz={handleBuzz}
          disabled={!connected || hasBuzzed}
        />

        <p className="mt-8 text-sm text-zinc-500">
          {connected ? "Connecté au salon" : "Connexion..."}
        </p>
      </div>
    </main>
  )
}