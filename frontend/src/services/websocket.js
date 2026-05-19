const WS_BASE_URL = "ws://127.0.0.1:8000"

export function createRoomSocket({ roomCode, playerId }) {
  return new WebSocket(`${WS_BASE_URL}/ws/${roomCode}/${playerId}`)
}