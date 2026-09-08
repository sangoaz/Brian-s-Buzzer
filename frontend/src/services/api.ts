import type { RoomCreateResponse, RoomSettings, PlayerJoinResponse } from "../types/room"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL

export async function createRoom(settings: RoomSettings): Promise<RoomCreateResponse> {
  const response = await fetch(`${API_BASE_URL}/rooms`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(settings),
  })

  if (!response.ok) {
    throw new Error("Erreur lors de la création du salon")
  }

  return response.json()
}

export async function joinRoom(roomCode: string, name: string): Promise<PlayerJoinResponse> {
  const response = await fetch(`${API_BASE_URL}/rooms/${roomCode}/join`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name }),
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.detail)
  }

  return response.json()
}
