export interface Team {
  id: string
  name: string
}

export interface Player {
  id: string
  name: string
  team_id: string | null
}

export type RoomStatus = "waiting" | "playing" | "finished"

export interface BuzzHistoryEntry {
  id: string
  name: string
  result: "pending" | "correct" | "wrong"
}

export interface RoomState {
  code: string
  players: Player[]
  current_buzzer: Player | null
  status: RoomStatus
  round: number
  scores: Record<string, number>
  blocked_players: string[]
  buzz_history: Record<string, BuzzHistoryEntry[]>
  teams: Team[]
  team_scores: Record<string, number>
  settings: Partial<RoomSettings>
}

export interface RoomSettings {
  max_rounds: number | null
  block_on_wrong: boolean
  block_duration: number
  penalty_on_wrong: boolean
  lock_on_start: boolean
  teams: string[] | null
}

export interface RoomCreateResponse {
  room_code: string
  host_id: string
  success: boolean
  settings: RoomSettings
}

export interface PlayerJoinResponse {
  player_id: string
  name: string
  room_code: string
}
