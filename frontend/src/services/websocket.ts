const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL

interface CreateRoomSocketOptions {
  roomCode: string
  playerId: string
}

export function createRoomSocket({ roomCode, playerId }: CreateRoomSocketOptions): WebSocket {
  return new WebSocket(`${WS_BASE_URL}/ws/${roomCode}/${playerId}`)
}
