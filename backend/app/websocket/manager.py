from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, dict[str, WebSocket]] = {}

    async def connect(
        self,
        room_code: str,
        player_id: str,
        websocket: WebSocket,
    ):
        await websocket.accept()

        if room_code not in self.active_connections:
            self.active_connections[room_code] = {}

        self.active_connections[room_code][player_id] = websocket

    def disconnect(
        self,
        room_code: str,
        player_id: str,
    ):
        room = self.active_connections.get(room_code)

        if not room:
            return

        room.pop(player_id, None)

        if len(room) == 0:
            self.active_connections.pop(room_code, None)

    async def broadcast(
        self,
        room_code: str,
        message: dict,
    ):
        room = self.active_connections.get(room_code)

        if not room:
            return

        disconnected_players = []

        for player_id, websocket in room.items():
            try:
                await websocket.send_json(message)
            except RuntimeError:
                disconnected_players.append(player_id)

        for player_id in disconnected_players:
            self.disconnect(room_code, player_id)


manager = ConnectionManager()