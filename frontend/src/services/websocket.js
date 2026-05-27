const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL

export function createRoomSocket({ roomCode, playerId }) {
  return new WebSocket(`${WS_BASE_URL}/ws/${roomCode}/${playerId}`)
}