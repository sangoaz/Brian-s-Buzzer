import pytest
from starlette.websockets import WebSocketDisconnect


class TestWebSocketConnection:
    def test_websocket_connect_broadcasts_room_state(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        join_response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Kevin"},
        )
        player_id = join_response.json()["player_id"]

        with client.websocket_connect(f"/ws/{room_code}/{player_id}") as websocket:
            data = websocket.receive_json()

            assert data["type"] == "room_state"
            assert data["room"]["room_code"] == room_code
            assert data["room"]["current_buzzer"] is None
            assert data["room"]["players"] == [
                {
                    "id": player_id,
                    "name": "Kevin",
                }
            ]

    def test_websocket_connect_accepts_lowercase_room_code(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        join_response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Kevin"},
        )
        player_id = join_response.json()["player_id"]

        with client.websocket_connect(
            f"/ws/{room_code.lower()}/{player_id}"
        ) as websocket:
            data = websocket.receive_json()

            assert data["type"] == "room_state"
            assert data["room"]["room_code"] == room_code


class TestWebSocketActions:
    def test_websocket_buzz_action(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        join_response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Kevin"},
        )
        player_id = join_response.json()["player_id"]

        with client.websocket_connect(f"/ws/{room_code}/{player_id}") as websocket:
            websocket.receive_json()

            websocket.send_json({"action": "buzz"})
            data = websocket.receive_json()

            assert data["type"] == "buzz"
            assert data["player"] == {
                "id": player_id,
                "name": "Kevin",
            }
            assert data["room"]["current_buzzer"] == {
                "id": player_id,
                "name": "Kevin",
            }

    def test_websocket_reset_action(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        join_response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Kevin"},
        )
        player_id = join_response.json()["player_id"]

        with client.websocket_connect(f"/ws/{room_code}/{player_id}") as websocket:
            websocket.receive_json()

            websocket.send_json({"action": "buzz"})
            websocket.receive_json()

            websocket.send_json({"action": "reset"})
            data = websocket.receive_json()

            assert data["type"] == "reset"
            assert data["room"]["current_buzzer"] is None

    def test_websocket_unknown_action_returns_error(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        join_response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Kevin"},
        )
        player_id = join_response.json()["player_id"]

        with client.websocket_connect(f"/ws/{room_code}/{player_id}") as websocket:
            websocket.receive_json()

            websocket.send_json({"action": "unknown"})
            data = websocket.receive_json()

            assert data == {
                "type": "error",
                "message": "Unknown action",
            }


class TestWebSocketDisconnect:
    def test_websocket_disconnect_does_not_crash(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        join_response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Kevin"},
        )
        player_id = join_response.json()["player_id"]

        with client.websocket_connect(f"/ws/{room_code}/{player_id}") as websocket:
            websocket.receive_json()

        # Le simple fait de sortir du `with` déclenche la déconnexion.
        assert True
