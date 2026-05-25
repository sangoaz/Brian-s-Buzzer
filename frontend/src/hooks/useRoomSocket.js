"use client"

import { useEffect, useState } from "react"
import { createRoomSocket } from "../services/websocket"
import { ERROR_MESSAGES } from "../app/constants/errors"
import {
  ROOM_STATE,
  BUZZ,
  RESET,
  PLAYER_LEFT,
  PLAYER_KICKED,
  ERROR,
} from "../app/constants/events"


export function useRoomSocket({ roomCode, playerId }) {
  const [socket, setSocket] = useState(null)
  const [roomState, setRoomState] = useState(null)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState("")
  const [kicked, setKicked] = useState(false)

  useEffect(() => {
    if (!roomCode || !playerId) return

    const ws = createRoomSocket({
      roomCode,
      playerId,
    })

    ws.onopen = () => {
      setConnected(true)
      setError("")
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
    message.type === PLAYER_LEFT
  ) {
    setRoomState(message.room)
    setError("")
    return
  }
}

    setSocket(ws)

    return () => {
      ws.close()
    }
  }, [roomCode, playerId])

  function sendAction(action) {
    if (!socket || socket.readyState !== WebSocket.OPEN) return

    socket.send(
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