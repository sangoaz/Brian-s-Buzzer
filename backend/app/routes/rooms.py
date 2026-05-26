from fastapi import APIRouter, HTTPException
from app.websocket.manager import manager

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
    remove_player,
    kick_player,
)
from app.constants import errors, events
from app.utils.exceptions import raise_service_error

router = APIRouter(prefix="/rooms", tags=["Rooms"])


# Route de création de salon
@router.post("", response_model=RoomCreateResponse, status_code=201)
def create_new_room():
    return create_room()


# Route pour rejoindre un salon
@router.post("/{room_code}/join", response_model=PlayerJoinResponse)
def join_existing_room(room_code: str, payload: PlayerJoinRequest):
    result = join_room(room_code.upper(), payload.name)

    if not result["success"]:
        raise_service_error(result["error"])

    player = result["player"]

    return {
        "player_id": player["id"],
        "name": player["name"],
        "room_code": room_code.upper(),
    }


# Lit l'état du salon
@router.get("/{room_code}", response_model=RoomStateResponse)
def read_room_state(room_code: str):
    result = get_room_state(room_code.upper())

    if not result["success"]:
        raise_service_error(result["error"])

    room_state = result["room"]

    return room_state


# Route pour buzzer
@router.post("/{room_code}/buzz/{player_id}")
def buzz_room(room_code: str, player_id: str):
    result = buzz(room_code.upper(), player_id)

    if not result["success"]:
        raise_service_error(result["error"])

    player = result["player"]

    return {
        "message": f"{player['name']} buzzed first",
        "player": player,
    }


# Route pour reset le buzzer
@router.post("/{room_code}/reset", response_model=RoomStateResponse)
def reset_room_buzzer(room_code: str):
    result = reset_buzzer(room_code.upper())

    if not result["success"]:
        raise_service_error(result["error"])

    room_state = result["room"]

    return room_state


# Route pour kick un joueur
@router.delete("/{room_code}/players/{player_id}")
async def kick_player_from_room(
    room_code: str,
    player_id: str,
    host_id: str,
):
    result = kick_player(
        room_code.upper(),
        host_id,
        player_id,
    )

    if not result["success"]:
        raise HTTPException(status_code=403, detail=result["error"])

    await manager.broadcast(
        room_code.upper(),
        {
            "type": events.PLAYER_KICKED,
            "player_id": player_id,
            "room": result["room"],
        },
    )

    return result


# Déconnection volontaire du joueur
@router.delete("/{room_code}/players/{player_id}/leave")
async def leave_room(room_code: str, player_id: str):
    result = remove_player(room_code.upper(), player_id)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    await manager.broadcast(
        room_code.upper(),
        {
            "type": events.PLAYER_LEFT,
            "player_id": player_id,
            "room": result["room"],
        },
    )

    return result
