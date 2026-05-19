from pydantic import BaseModel

class RoomCreateResponse(BaseModel):
    room_code: str


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
    