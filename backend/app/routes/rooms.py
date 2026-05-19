from fastapi import APIRouter, HTTPException

from app.schemas.room import (
    PlayerJoinRequest,
    PlayerJoinResponse,
    RoomCreateResponse,
    RoomStateResponse,
)
from app.services.room_service import (
    create_room,
    join_room,
    get_room_state,
    buzz,
    reset_buzzer,
)

router = APIRouter(prefix="/rooms", tags=["Rooms"])

# Route de création de salon
@router.post("", response_model=RoomCreateResponse, status_code=201)
def create_new_room():
    room_code = create_room()
    return {"room_code": room_code}


# Route pour rejoindre un salon
@router.post("/{room_code}/join", response_model=PlayerJoinResponse)
def join_existing_room(room_code: str, payload: PlayerJoinRequest):
    player = join_room(room_code.upper(), payload.name)

    if not player:
        raise HTTPException(status_code=404, detail="Room not found")

    return {
        "player_id": player["id"],
        "name": player["name"],
        "room_code": room_code.upper(),
    }

# Lit l'état du salon
@router.get("/{room_code}", response_model=RoomStateResponse)
def read_room_state(room_code: str):
    room_state = get_room_state(room_code.upper())

    if not room_state:
        raise HTTPException(status_code=404, detail="Room not found")

    return room_state

# Route pour buzzer
@router.post("/{room_code}/buzz/{player_id}")
def buzz_room(room_code: str, player_id: str):
    player = buzz(room_code.upper(), player_id)

    if not player:
        raise HTTPException(status_code=404, detail="Room or player not found")

    return {
        "message": f"{player['name']} buzzed first",
        "player": player,
    }

# Route pour reser le buzzer
@router.post("/{room_code}/reset", response_model=RoomStateResponse)
def reset_room_buzzer(room_code: str):
    room_state = reset_buzzer(room_code.upper())

    if not room_state:
        raise HTTPException(status_code=404, detail="Room not found")

    return room_state