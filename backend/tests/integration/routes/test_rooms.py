from app.services.room_service import rooms


class TestCreateRoomRoute:
    def test_create_room_returns_201_and_room_code(self, client):
        response = client.post("/rooms")

        assert response.status_code == 201

        data = response.json()

        assert "room_code" in data
        assert data["room_code"] in rooms


class TestJoinRoomRoute:
    def test_join_existing_room(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Kevin"},
        )

        assert response.status_code == 200

        data = response.json()

        assert "player_id" in data
        assert data["name"] == "Kevin"
        assert data["room_code"] == room_code

    def test_join_existing_room_with_lowercase_code(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        response = client.post(
            f"/rooms/{room_code.lower()}/join",
            json={"name": "Kevin"},
        )

        assert response.status_code == 200
        assert response.json()["room_code"] == room_code

    def test_join_unknown_room_returns_404(self, client):
        response = client.post(
            "/rooms/ABCD/join",
            json={"name": "Kevin"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Room not found"


class TestReadRoomStateRoute:
    def test_read_existing_room_state(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        join_response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Kevin"},
        )
        player_id = join_response.json()["player_id"]

        response = client.get(f"/rooms/{room_code}")

        assert response.status_code == 200

        data = response.json()

        assert data["room_code"] == room_code
        assert data["current_buzzer"] is None
        assert data["players"] == [
            {
                "id": player_id,
                "name": "Kevin",
            }
        ]

    def test_read_existing_room_state_with_lowercase_code(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        response = client.get(f"/rooms/{room_code.lower()}")

        assert response.status_code == 200
        assert response.json()["room_code"] == room_code

    def test_read_unknown_room_returns_404(self, client):
        response = client.get("/rooms/ABCD")

        assert response.status_code == 404
        assert response.json()["detail"] == "Room not found"


class TestBuzzRoomRoute:
    def test_buzz_existing_room_with_existing_player(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        join_response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Kevin"},
        )
        player_id = join_response.json()["player_id"]

        response = client.post(f"/rooms/{room_code}/buzz/{player_id}")

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Kevin buzzed first"
        assert data["player"] == {
            "id": player_id,
            "name": "Kevin",
        }

    def test_buzz_existing_room_with_lowercase_code(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        join_response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Kevin"},
        )
        player_id = join_response.json()["player_id"]

        response = client.post(f"/rooms/{room_code.lower()}/buzz/{player_id}")

        assert response.status_code == 200
        assert response.json()["player"]["id"] == player_id

    def test_buzz_unknown_room_returns_404(self, client):
        response = client.post("/rooms/ABCD/buzz/fake-player-id")

        assert response.status_code == 404
        assert response.json()["detail"] == "Room or player not found"

    def test_buzz_unknown_player_returns_404(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        response = client.post(f"/rooms/{room_code}/buzz/fake-player-id")

        assert response.status_code == 404
        assert response.json()["detail"] == "Room or player not found"


class TestResetRoomBuzzerRoute:
    def test_reset_existing_room_buzzer(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        join_response = client.post(
            f"/rooms/{room_code}/join",
            json={"name": "Kevin"},
        )
        player_id = join_response.json()["player_id"]

        client.post(f"/rooms/{room_code}/buzz/{player_id}")

        response = client.post(f"/rooms/{room_code}/reset")

        assert response.status_code == 200

        data = response.json()

        assert data["room_code"] == room_code
        assert data["current_buzzer"] is None
        assert data["players"] == [
            {
                "id": player_id,
                "name": "Kevin",
            }
        ]

    def test_reset_existing_room_with_lowercase_code(self, client):
        create_response = client.post("/rooms")
        room_code = create_response.json()["room_code"]

        response = client.post(f"/rooms/{room_code.lower()}/reset")

        assert response.status_code == 200
        assert response.json()["room_code"] == room_code

    def test_reset_unknown_room_returns_404(self, client):
        response = client.post("/rooms/ABCD/reset")

        assert response.status_code == 404
        assert response.json()["detail"] == "Room not found"
