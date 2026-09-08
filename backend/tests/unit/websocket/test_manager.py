import asyncio

import pytest
from unittest.mock import AsyncMock

from app.websocket.manager import ConnectionManager


@pytest.fixture
def manager():
    return ConnectionManager()


@pytest.fixture
def websocket():
    websocket = AsyncMock()
    websocket.accept = AsyncMock()
    websocket.send_json = AsyncMock()
    return websocket


class TestConnectionManagerConnect:
    @pytest.mark.asyncio
    async def test_connect_accepts_websocket_and_stores_connection(
        self,
        manager,
        websocket,
    ):
        await manager.connect("ABCD", "player-1", websocket)

        websocket.accept.assert_awaited_once()
        assert manager.active_connections == {
            "ABCD": {
                "player-1": websocket,
            }
        }

    @pytest.mark.asyncio
    async def test_connect_adds_player_to_existing_room(
        self,
        manager,
        websocket,
    ):
        second_websocket = AsyncMock()
        second_websocket.accept = AsyncMock()

        await manager.connect("ABCD", "player-1", websocket)
        await manager.connect("ABCD", "player-2", second_websocket)

        assert manager.active_connections["ABCD"] == {
            "player-1": websocket,
            "player-2": second_websocket,
        }


class TestConnectionManagerDisconnect:
    def test_disconnect_existing_player(self, manager, websocket):
        manager.active_connections = {
            "ABCD": {
                "player-1": websocket,
                "player-2": AsyncMock(),
            }
        }

        manager.disconnect("ABCD", "player-1")

        assert "player-1" not in manager.active_connections["ABCD"]
        assert "player-2" in manager.active_connections["ABCD"]

    def test_disconnect_unknown_room_does_nothing(self, manager):
        manager.disconnect("ABCD", "player-1")

        assert manager.active_connections == {}

    def test_disconnect_unknown_player_does_nothing(self, manager, websocket):
        manager.active_connections = {
            "ABCD": {
                "player-1": websocket,
            }
        }

        manager.disconnect("ABCD", "fake-player-id")

        assert manager.active_connections == {
            "ABCD": {
                "player-1": websocket,
            }
        }

    def test_disconnect_removes_empty_room(self, manager, websocket):
        manager.active_connections = {
            "ABCD": {
                "player-1": websocket,
            }
        }

        manager.disconnect("ABCD", "player-1")

        assert manager.active_connections == {}


class TestConnectionManagerBroadcast:
    @pytest.mark.asyncio
    async def test_broadcast_sends_message_to_all_players(self, manager):
        websocket_1 = AsyncMock()
        websocket_2 = AsyncMock()

        manager.active_connections = {
            "ABCD": {
                "player-1": websocket_1,
                "player-2": websocket_2,
            }
        }

        message = {"type": "room_state"}

        await manager.broadcast("ABCD", message)

        websocket_1.send_json.assert_awaited_once_with(message)
        websocket_2.send_json.assert_awaited_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_unknown_room_does_nothing(self, manager):
        await manager.broadcast("ABCD", {"type": "room_state"})

        assert manager.active_connections == {}

    @pytest.mark.asyncio
    async def test_broadcast_disconnects_players_with_runtime_error(self, manager):
        working_websocket = AsyncMock()
        broken_websocket = AsyncMock()
        broken_websocket.send_json.side_effect = RuntimeError

        manager.active_connections = {
            "ABCD": {
                "player-1": working_websocket,
                "player-2": broken_websocket,
            }
        }

        message = {"type": "room_state"}

        await manager.broadcast("ABCD", message)

        working_websocket.send_json.assert_awaited_once_with(message)
        broken_websocket.send_json.assert_awaited_once_with(message)

        assert manager.active_connections == {
            "ABCD": {
                "player-1": working_websocket,
            }
        }


class TestConnectionManagerBroadcastConcurrency:
    @pytest.mark.asyncio
    async def test_broadcast_slow_connection_does_not_block_others(self, manager):
        # Reproduit le bug signalé : un téléphone dont la connexion WebSocket
        # est "zombie" (verrouillage écran, bascule wifi/4G) ne doit pas
        # empêcher les autres joueurs de recevoir la mise à jour en temps réel.
        manager.send_timeout = 0.05

        fast_websocket = AsyncMock()

        async def slow_send(message):
            await asyncio.sleep(1)

        slow_websocket = AsyncMock()
        slow_websocket.send_json = AsyncMock(side_effect=slow_send)

        manager.active_connections = {
            "ABCD": {
                "player-fast": fast_websocket,
                "player-slow": slow_websocket,
            }
        }

        message = {"type": "room_state"}

        start = asyncio.get_event_loop().time()
        await manager.broadcast("ABCD", message)
        elapsed = asyncio.get_event_loop().time() - start

        # Le joueur "rapide" a bien reçu le message sans attendre le lent
        fast_websocket.send_json.assert_awaited_once_with(message)
        assert elapsed < 0.5

        # Le joueur "zombie" a été détecté et retiré des connexions actives
        assert manager.active_connections == {
            "ABCD": {
                "player-fast": fast_websocket,
            }
        }

    @pytest.mark.asyncio
    async def test_broadcast_disconnects_players_on_timeout(self, manager):
        manager.send_timeout = 0.05

        stuck_websocket = AsyncMock()

        async def hang_forever(message):
            await asyncio.sleep(10)

        stuck_websocket.send_json = AsyncMock(side_effect=hang_forever)

        manager.active_connections = {
            "ABCD": {
                "player-1": stuck_websocket,
            }
        }

        await manager.broadcast("ABCD", {"type": "room_state"})

        assert manager.active_connections == {}
