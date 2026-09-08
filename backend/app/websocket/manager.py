import asyncio

from fastapi import WebSocket


# Délai max accordé à l'envoi vers un client avant de le considérer mort.
# Une connexion "zombie" (téléphone verrouillé, réseau qui bascule) peut
# rester ouverte côté serveur sans jamais lever d'erreur : sans ce timeout,
# un `await` bloqué sur cette connexion retardait la diffusion à TOUS les
# autres joueurs de la room (la boucle était séquentielle).
SEND_TIMEOUT_SECONDS = 2.0


class ConnectionManager:
    def __init__(self, send_timeout: float = SEND_TIMEOUT_SECONDS):
        self.active_connections: dict[str, dict[str, WebSocket]] = {}
        self.send_timeout = send_timeout

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

    async def _send(self, player_id: str, websocket: WebSocket, message: dict):
        """Envoie le message à un client. Renvoie le player_id si l'envoi a
        échoué ou a dépassé le timeout, sinon None."""
        try:
            await asyncio.wait_for(
                websocket.send_json(message),
                timeout=self.send_timeout,
            )
            return None
        except (RuntimeError, asyncio.TimeoutError):
            return player_id

    async def broadcast(
        self,
        room_code: str,
        message: dict,
    ):
        room = self.active_connections.get(room_code)

        if not room:
            return

        # Envoi concurrent : une connexion lente ou morte ne doit pas
        # retarder la réception du message par les autres joueurs.
        results = await asyncio.gather(
            *(
                self._send(player_id, websocket, message)
                for player_id, websocket in room.items()
            )
        )

        disconnected_players = [player_id for player_id in results if player_id]

        for player_id in disconnected_players:
            self.disconnect(room_code, player_id)


manager = ConnectionManager()