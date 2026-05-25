const API_BASE_URL = "http://127.0.0.1:8000"

export async function createRoom() {
  const response = await fetch(`${API_BASE_URL}/rooms`, {
    method: "POST",
  })

  if (!response.ok) {
    throw new Error("Erreur lors de la création du salon")
  }

  return response.json()
}

export async function joinRoom(roomCode, name) {
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