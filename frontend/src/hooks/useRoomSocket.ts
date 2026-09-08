"use client"

import { useEffect, useRef, useState } from "react"
import { createRoomSocket } from "../services/websocket"
import { ERROR_MESSAGES } from "../app/constants/errors"
import {
  ROOM_STATE,
  BUZZ,
  RESET,
  PLAYER_LEFT,
  PLAYER_KICKED,
  GAME_STARTED,
  ERROR,
  ANSWER_REJECTED,
  ANSWER_VALIDATED,
  GAME_FINISHED,
  GAME_RESTARTED,
  ROOM_CLOSED,
  PONG,
} from "../app/constants/events"
import type { RoomState } from "../types/room"

const PING_INTERVAL_MS = 15000
// Si aucun pong ne revient dans ce délai après un ping, la connexion est
// considérée comme "zombie" (téléphone verrouillé, bascule wifi/4G) et on
// force une reconnexion plutôt que d'attendre indéfiniment. Valeurs
// resserrées pour un buzzer temps réel : un joueur déconnecté doit
// retrouver un socket fonctionnel vite, pas au bout de 40s.
const PONG_TIMEOUT_MS = 4000

interface UseRoomSocketOptions {
  roomCode: string | null | undefined
  playerId: string | null | undefined
}

interface IncomingMessage {
  type: string
  room?: RoomState
  error?: string
  player_id?: string
}

export interface AnswerResult {
  playerId: string
  result: "correct" | "wrong"
  token: number
}

export function useRoomSocket({ roomCode, playerId }: UseRoomSocketOptions) {
  const socketRef = useRef<WebSocket | null>(null)
  const pongTimeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [roomState, setRoomState] = useState<RoomState | null>(null)
  // Miroir synchrone de roomState, lu depuis onmessage : ce handler est
  // défini une fois par connexion (l'effet ne redépend pas de roomState),
  // donc lire roomState directement y donnerait une valeur périmée. Le ref
  // est toujours à jour, y compris entre deux rendus.
  const roomStateRef = useRef<RoomState | null>(null)
  const [lastAnswerResult, setLastAnswerResult] = useState<AnswerResult | null>(null)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState("")
  const [kicked, setKicked] = useState(false)
  const [retryCount, setRetryCount] = useState(0)     // déclenche le useEffect
  const [retryAttempt, setRetryAttempt] = useState(0) // calcule le délai
  const [roomClosed, setRoomClosed] = useState(false)
  const shouldReconnect = useRef(true)

  useEffect(() => {
    if (!roomCode || !playerId) return

    const ws = createRoomSocket({
      roomCode,
      playerId,
    })

    socketRef.current = ws
    setSocket(ws)

    ws.onopen = () => {
      setConnected(true)
      setRetryAttempt(0)
      setError("")
    }

    const interval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "ping" }))

        clearTimeout(pongTimeoutRef.current)
        pongTimeoutRef.current = setTimeout(() => {
          // Pas de pong reçu à temps : la socket est probablement morte
          // sans que le navigateur l'ait détecté. On force la fermeture
          // pour déclencher la reconnexion automatique existante.
          ws.close()
        }, PONG_TIMEOUT_MS)
      }
    }, PING_INTERVAL_MS)

    ws.onclose = () => {
      clearTimeout(pongTimeoutRef.current)
      setConnected(false)
      if (!shouldReconnect.current) return
      setRetryAttempt(n => n + 1)  // ← délai de plus en plus long
      setTimeout(() => {
        setRetryCount(n => n + 1)  // ← déclenche la reconnexion
      }, Math.min(1000 * 2 ** retryAttempt, 30000))
    }

    ws.onmessage = (event: MessageEvent) => {
      const message: IncomingMessage = JSON.parse(event.data)

      if (message.type === PONG) {
        clearTimeout(pongTimeoutRef.current)
        return
      }

      if (message.type === ERROR) {
        setError(
          (message.error && ERROR_MESSAGES[message.error]) ||
          "Une erreur est survenue."
        )
        return
      }

      if (message.type === PLAYER_KICKED) {
        roomStateRef.current = message.room ?? null
        setRoomState(message.room ?? null)
        setError("")

        if (message.player_id === playerId) {
          setKicked(true)
        }

        return
      }

      if (message.type === ROOM_CLOSED) {
        shouldReconnect.current = false
        setRoomClosed(true)
        return
      }

      if (message.type === ANSWER_VALIDATED || message.type === ANSWER_REJECTED) {
        // Le buzzer courant (avant que cet événement ne le remette à zéro)
        // est le joueur concerné par la validation/le rejet : on capture
        // son id avant d'écraser roomState avec le nouvel état.
        const buzzerId = roomStateRef.current?.current_buzzer?.id
        if (buzzerId) {
          setLastAnswerResult({
            playerId: buzzerId,
            result: message.type === ANSWER_VALIDATED ? "correct" : "wrong",
            token: Date.now(),
          })
        }

        roomStateRef.current = message.room ?? null
        setRoomState(message.room ?? null)
        setError("")
        return
      }

      if (
        message.type === ROOM_STATE ||
        message.type === BUZZ ||
        message.type === RESET ||
        message.type === PLAYER_LEFT ||
        message.type === GAME_STARTED ||
        message.type === GAME_FINISHED ||
        message.type === GAME_RESTARTED
      ) {
        roomStateRef.current = message.room ?? null
        setRoomState(message.room ?? null)
        setError("")
        return
      }
    }

    return () => {
      clearInterval(interval)
      clearTimeout(pongTimeoutRef.current)
      ws.onclose = null
      ws.close()
      socketRef.current = null
    }
  }, [roomCode, playerId, retryCount])

  function sendAction(action: string) {
    const currentSocket = socketRef.current

    if (!currentSocket || currentSocket.readyState !== WebSocket.OPEN) {
      return
    }

    currentSocket.send(
      JSON.stringify({
        action,
      })
    )
  }

  return {
    socket,
    roomState,
    lastAnswerResult,
    connected,
    error,
    kicked,
    roomClosed,
    sendAction,
  }
}
