from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.constants import events, errors
from app.services.room_service import (
    buzz,
    get_room_state,
    reset_buzzer,
    remove_player,
    can_connect_to_room,
    start_game,
)
from app.websocket.manager import manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/{room_code}/{player_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_code: str,
    player_id: str,
):
    room_code = room_code.upper()

    connection_result = can_connect_to_room(room_code, player_id)

    if not connection_result["success"]:
        await websocket.accept()
        await websocket.send_json(
            {
                "type": events.ERROR,
                "error": connection_result["error"],
            }
        )
        await websocket.close()
        return

    # Connexion autorisée : accepte la connexion et stocke le websocket
    await manager.connect(room_code, player_id, websocket)

    room_result = get_room_state(room_code)

    if not room_result["success"]:
        await websocket.send_json(
            {
                "type": events.ERROR,
                "error": room_result["error"],
            }
        )
        await websocket.close()
        return

    room_state = room_result["room"]

    await manager.broadcast(
        room_code,
        {
            "type": events.ROOM_STATE,
            "room": room_state,
        },
    )

    try:
        while True:
            data = await websocket.receive_json()

            action = data.get("action")

            if action == "buzz":
                buzz_result = buzz(room_code, player_id)

                if not buzz_result["success"]:
                    await websocket.send_json(
                        {
                            "type": events.ERROR,
                            "error": buzz_result["error"],
                        }
                    )
                    continue

                player = buzz_result["player"]

                room_result = get_room_state(room_code)
                room_state = room_result["room"]

                await manager.broadcast(
                    room_code,
                    {
                        "type": events.BUZZ,
                        "player": player,
                        "room": room_state,
                    },
                )

            elif action == "start_game":
                start_result = start_game(room_code, player_id)

                if not start_result["success"]:
                    await websocket.send_json(
                        {
                            "type": events.ERROR,
                            "error": start_result["error"],
                        }
                    )
                    continue

                await manager.broadcast(
                    room_code,
                    {
                        "type": events.GAME_STARTED,
                        "room": start_result["room"],
                    },
                )

            elif action == "reset":
                reset_result = reset_buzzer(room_code, player_id)

                if not reset_result["success"]:
                    await websocket.send_json(
                        {
                            "type": events.ERROR,
                            "error": reset_result["error"],
                        }
                    )
                    continue

                room_state = reset_result["room"]

                await manager.broadcast(
                    room_code,
                    {
                        "type": events.RESET,
                        "room": room_state,
                    },
                )

            else:
                await websocket.send_json(
                    {
                        "type": events.ERROR,
                        "error": errors.UNKNOWN_ACTION,
                    }
                )

    except WebSocketDisconnect:
        manager.disconnect(room_code, player_id)

        remove_result = remove_player(room_code, player_id)

        if remove_result["success"]:
            await manager.broadcast(
                room_code,
                {
                    "type": events.PLAYER_LEFT,
                    "player_id": player_id,
                    "room": remove_result["room"],
                },
            )
