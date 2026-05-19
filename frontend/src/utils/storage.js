export function savePlayerSession({ playerId, playerName, roomCode }) {
  localStorage.setItem("player_id", playerId)
  localStorage.setItem("player_name", playerName)
  localStorage.setItem("room_code", roomCode)
}

export function getPlayerSession() {
  return {
    playerId: localStorage.getItem("player_id"),
    playerName: localStorage.getItem("player_name"),
    roomCode: localStorage.getItem("room_code"),
  }
}

export function clearPlayerSession() {
  localStorage.removeItem("player_id")
  localStorage.removeItem("player_name")
  localStorage.removeItem("room_code")
}