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

    # Dès qu'un joueur se connecte, on envoie l'état actuel du salo à tout le monde
    room_state = get_room_state(room_code)

    await manager.broadcast(
        room_code,
        {
            "type": "room_state",
            "room": room_state
        },
    )

    try:
        # Le websocket reste vivant tant que le client est connecté
        while True:
            # Le server attend un message JSON venant du client ex: "action": "buzz"
            data = await websocket.receive_json()

            action = data.get("action")

            if action == "buzz":
                player = buzz(room_code, player_id)
                room_state = get_room_state(room_code)

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
                room_state = reset_buzzer(room_code)

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

        room_state = get_room_state(room_code)

        await manager.broadcast(
            room_code,
            {
                "type": "disconnect",
                "player_id": player_id,
                "room": room_state,
            },
        )