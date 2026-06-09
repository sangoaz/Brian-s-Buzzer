from pydantic import BaseModel


class RoomCreateResponse(BaseModel):
    room_code: str
    host_id: str
    success: bool
    settings: dict


class PlayerJoinRequest(BaseModel):
    name: str


class PlayerJoinResponse(BaseModel):
    player_id: str
    name: str
    room_code: str


class RoomStateResponse(BaseModel):
    room_code: str
    players: list[dict]
    current_buzzer: dict | None


class RoomSettings(BaseModel):
    max_rounds: int | None = None
    block_on_wrong: bool = False
    block_duration: int = 5
    penalty_on_wrong: bool = False
    lock_on_start: bool = False
