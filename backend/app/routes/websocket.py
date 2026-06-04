from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.constants import events, errors
from app.services.room_service import (
    buzz,
    get_room_state,
    next_round,
    remove_player,
    can_connect_to_room,
    start_game,
    validate_answer,
    reject_answer,
    end_game,
    restart_game,
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

            elif action == "end_game":
                end_result = end_game(room_code, player_id)

                if not end_result["success"]:
                    await websocket.send_json(
                        {
                            "type": events.ERROR,
                            "error": end_result["error"],
                        }
                    )
                    continue

                await manager.broadcast(
                    room_code,
                    {
                        "type": events.GAME_FINISHED,
                        "room": end_result["room"],
                    },
                )

            elif action == "restart_game":
                end_result = restart_game(room_code, player_id)

                if not end_result["success"]:
                    await websocket.send_json(
                        {
                            "type": events.ERROR,
                            "error": end_result["error"],
                        }
                    )
                    continue

                await manager.broadcast(
                    room_code,
                    {
                        "type": events.GAME_RESTARTED,
                        "room": end_result["room"],
                    },
                )

            elif action == "validate_answer":
                validate_result = validate_answer(room_code, player_id)

                if not validate_result["success"]:
                    await websocket.send_json(
                        {
                            "type": events.ERROR,
                            "error": validate_result["error"],
                        }
                    )
                    continue

                await manager.broadcast(
                    room_code,
                    {
                        "type": events.ANSWER_VALIDATED,
                        "room": validate_result["room"],
                    },
                )

            elif action == "reject_answer":
                reject_result = reject_answer(room_code, player_id)

                if not reject_result["success"]:
                    await websocket.send_json(
                        {
                            "type": events.ERROR,
                            "error": reject_result["error"],
                        }
                    )
                    continue

                await manager.broadcast(
                    room_code,
                    {
                        "type": events.ANSWER_REJECTED,
                        "room": reject_result["room"],
                    },
                )

            elif action == "reset":
                reset_result = next_round(room_code, player_id)

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

            # Garde une activité sur le websocket
            elif action == "ping":
                await websocket.send_json({"type": "pong"})

            else:
                await websocket.send_json(
                    {
                        "type": events.ERROR,
                        "error": errors.UNKNOWN_ACTION,
                    }
                )

    except WebSocketDisconnect:
        manager.disconnect(room_code, player_id)
