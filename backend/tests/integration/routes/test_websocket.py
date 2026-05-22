import pytest
from starlette.websockets import WebSocketDisconnect


from app.constants import errors


class TestWebSocketDisconnect:
    def test_websocket_disconnect_broadcasts_disconnect_message(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        first_join_response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Kevin"},
        )
        first_player_id = first_join_response.json()["player_id"]

        second_join_response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Alex"},
        )
        second_player_id = second_join_response.json()["player_id"]

        with client.websocket_connect(
            f"/ws/{room_code}/{first_player_id}"
        ) as first_websocket:

            first_websocket.receive_json()

            with client.websocket_connect(
                f"/ws/{room_code}/{second_player_id}"
            ) as second_websocket:

                # message reçu à l'arrivée du second joueur
                first_websocket.receive_json()
                second_websocket.receive_json()

            # ignorer éventuel room_state restant
            message = first_websocket.receive_json()

            while message["type"] != "disconnect":
                message = first_websocket.receive_json()

            assert message["type"] == "disconnect"
            assert message["player_id"] == second_player_id
            assert message["room"]["room_code"] == room_code

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
    def test_websocket_disconnect_broadcasts_disconnect_message(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        first_join_response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Kevin"},
        )
        first_player_id = first_join_response.json()["player_id"]

        second_join_response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Alex"},
        )
        second_player_id = second_join_response.json()["player_id"]

        with client.websocket_connect(
            f"/ws/{room_code}/{first_player_id}"
        ) as first_websocket:
            first_websocket.receive_json()

            with client.websocket_connect(
                f"/ws/{room_code}/{second_player_id}"
            ) as second_websocket:
                first_websocket.receive_json()
                second_websocket.receive_json()

            data = first_websocket.receive_json()

            assert data["type"] == "player_left"
            assert data["player_id"] == second_player_id
            assert data["room"]["room_code"] == room_code


class TestWebSocketErrors:
    def test_websocket_connect_unknown_room_returns_error(self, client):
        with client.websocket_connect("/ws/ABCD/fake-player-id") as websocket:
            data = websocket.receive_json()

            assert data == {
                "type": "error",
                "error": errors.ROOM_NOT_FOUND,
            }

    def test_websocket_buzz_when_buzzer_already_locked_returns_error(self, client):
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

            websocket.send_json({"action": "buzz"})
            data = websocket.receive_json()

            assert data == {
                "type": "error",
                "error": errors.BUZZER_ALREADY_LOCKED,
            }
