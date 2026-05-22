from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.room_service import buzz, get_room_state, reset_buzzer
from app.websocket.manager import manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/{room_code}/{player_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_code: str,
    player_id: str,
):
    room_code = room_code.upper()

    # Connexion: Accepte la connection, stocke le websocket dans la bonne room
    await manager.connect(room_code, player_id, websocket)

    # Récupère l'état du salon
    room_result = get_room_state(room_code)

    if not room_result["success"]:
        await websocket.send_json(
            {
                "type": "error",
                "error": room_result["error"],
            }
        )
        return

    room_state = room_result["room"]

    # Dès qu'un joueur se connecte, on envoie l'état actuel du salon à tout le monde
    await manager.broadcast(
        room_code,
        {
            "type": "room_state",
            "room": room_state,
        },
    )

    try:
        # Le websocket reste vivant tant que le client est connecté
        while True:
            # Le server attend un message JSON venant du client ex: "action": "buzz"
            data = await websocket.receive_json()

            action = data.get("action")

            if action == "buzz":
                buzz_result = buzz(room_code, player_id)

                if not buzz_result["success"]:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "error": buzz_result["error"],
                        }
                    )
                    continue

                player = buzz_result["player"]

                room_result = get_room_state(room_code)
                room_state = room_result["room"]

                # Le server renvoie le message à tous les joueurs de la room
                await manager.broadcast(
                    room_code,
                    {
                        "type": "buzz",
                        "player": player,
                        "room": room_state,
                    },
                )

            elif action == "reset":
                reset_result = reset_buzzer(room_code)

                if not reset_result["success"]:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "error": reset_result["error"],
                        }
                    )
                    continue

                room_state = reset_result["room"]

                await manager.broadcast(
                    room_code,
                    {
                        "type": "reset",
                        "room": room_state,
                    },
                )

            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "Unknown action",
                    }
                )

    except WebSocketDisconnect:
        manager.disconnect(room_code, player_id)

        room_result = get_room_state(room_code)

        if room_result["success"]:
            room_state = room_result["room"]

            await manager.broadcast(
                room_code,
                {
                    "type": "disconnect",
                    "player_id": player_id,
                    "room": room_state,
                },
            )
