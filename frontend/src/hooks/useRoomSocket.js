"use client"

import { useEffect, useState } from "react"
import { createRoomSocket } from "../services/websocket"

export function useRoomSocket({ roomCode, playerId }) {
  const [socket, setSocket] = useState(null)
  const [roomState, setRoomState] = useState(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    if (!roomCode || !playerId) return

    const ws = createRoomSocket({
      roomCode,
      playerId,
    })

    ws.onopen = () => {
      setConnected(true)
    }

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)

      if (message.room) {
        setRoomState(message.room)
      }
    }

    ws.onclose = () => {
      setConnected(false)
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
    sendAction,
  }
}