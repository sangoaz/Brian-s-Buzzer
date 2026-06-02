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
} from "../app/constants/events"

export function useRoomSocket({ roomCode, playerId }) {
  const socketRef = useRef(null)

  const [socket, setSocket] = useState(null)
  const [roomState, setRoomState] = useState(null)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState("")
  const [kicked, setKicked] = useState(false)
  const [retryCount, setRetryCount] = useState(0)     // déclenche le useEffect
  const [retryAttempt, setRetryAttempt] = useState(0) // calcule le délai

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

    ws.onclose = () => {
      setConnected(false)
      setRetryAttempt(n => n + 1)  // ← délai de plus en plus long
      setTimeout(() => {
        setRetryCount(n => n + 1)  // ← déclenche la reconnexion
      }, Math.min(1000 * 2 ** retryAttempt, 30000))
    }

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)

      if (message.type === ERROR) {
        setError(
          ERROR_MESSAGES[message.error] ||
          "Une erreur est survenue."
        )
        return
      }

      if (message.type === PLAYER_KICKED) {
        setRoomState(message.room)
        setError("")

        if (message.player_id === playerId) {
          setKicked(true)
        }

        return
      }

      if (
        message.type === ROOM_STATE ||
        message.type === BUZZ ||
        message.type === RESET ||
        message.type === PLAYER_LEFT ||
        message.type === GAME_STARTED ||
        message.type === ANSWER_VALIDATED ||
        message.type === ANSWER_REJECTED ||
        message.type === GAME_FINISHED
      ) {
        setRoomState(message.room)
        setError("")
        return
      }
    }

    return () => {
      ws.close()
      socketRef.current = null
    }
  }, [roomCode, playerId, retryCount])

  function sendAction(action) {
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
    connected,
    error,
    kicked,
    sendAction,
  }
}