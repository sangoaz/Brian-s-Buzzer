from unittest.mock import patch

from app.services.room_service import (
    rooms,
    create_room,
    join_room,
    get_room_state,
    buzz,
    reset_buzzer,
)


class TestCreateRoom:
    def test_create_room(self):
        room_code = create_room()

        assert room_code in rooms
        assert rooms[room_code]["players"] == {}
        assert rooms[room_code]["current_buzzer"] is None

    def test_create_room_generates_new_code_if_code_already_exists(self):
        rooms["ABCD"] = {
            "players": {},
            "current_buzzer": None,
        }

        with patch(
            "app.services.room_service.generate_room_code",
            side_effect=["ABCD", "WXYZ"],
        ):
            room_code = create_room()

        assert room_code == "WXYZ"
        assert "ABCD" in rooms
        assert "WXYZ" in rooms


class TestJoinRoom:
    def test_join_existing_room(self):
        room_code = create_room()

        player = join_room(room_code, "Kevin")

        assert player is not None
        assert player["name"] == "Kevin"
        assert player["id"] in rooms[room_code]["players"]

    def test_join_unknown_room_returns_none(self):
        player = join_room("ABCD", "Kevin")

        assert player is None


class TestGetRoomState:
    def test_get_room_state(self):
        room_code = create_room()
        player = join_room(room_code, "Kevin")

        state = get_room_state(room_code)

        assert state == {
            "room_code": room_code,
            "players": [player],
            "current_buzzer": None,
        }

    def test_get_unknown_room_state_returns_none(self):
        state = get_room_state("ABCD")

        assert state is None


class TestBuzz:
    def test_buzz_sets_current_buzzer(self):
        room_code = create_room()
        player = join_room(room_code, "Kevin")

        result = buzz(room_code, player["id"])

        assert result == player
        assert rooms[room_code]["current_buzzer"] == player

    def test_buzz_unknown_room_returns_none(self):
        result = buzz("ABCD", "fake-player-id")

        assert result is None

    def test_buzz_unknown_player_returns_none(self):
        room_code = create_room()

        result = buzz(room_code, "fake-player-id")

        assert result is None

    def test_buzz_does_not_replace_first_buzzer(self):
        room_code = create_room()
        first_player = join_room(room_code, "Kevin")
        second_player = join_room(room_code, "Alex")

        first_result = buzz(room_code, first_player["id"])
        second_result = buzz(room_code, second_player["id"])

        assert first_result == first_player
        assert second_result == first_player
        assert rooms[room_code]["current_buzzer"] == first_player


class TestResetBuzzer:
    def test_reset_buzzer(self):
        room_code = create_room()
        player = join_room(room_code, "Kevin")
        buzz(room_code, player["id"])

        state = reset_buzzer(room_code)

        assert state["current_buzzer"] is None
        assert rooms[room_code]["current_buzzer"] is None

    def test_reset_unknown_room_returns_none(self):
        state = reset_buzzer("ABCD")

        assert state is None
