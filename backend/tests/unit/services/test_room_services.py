from unittest.mock import patch

from app.constants import errors
from app.services.room_service import (
    rooms,
    create_room,
    join_room,
    get_room_state,
    buzz,
    reset_buzzer,
    clean_player_name,
    normalize_player_name,
    is_player_name_available,
)


class TestCreateRoom:
    def test_create_room(self):
        result = create_room()
        room_code = result["room_code"]

        assert result["success"] is True
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
            result = create_room()

        assert result == {
            "success": True,
            "room_code": "WXYZ",
        }
        assert "ABCD" in rooms
        assert "WXYZ" in rooms


class TestJoinRoom:
    def test_join_existing_room(self):
        room_code = create_room()["room_code"]

        result = join_room(room_code, "Kevin")
        player = result["player"]

        assert result["success"] == True
        assert player["name"] == "Kevin"
        assert player["id"] in rooms[room_code]["players"]

    def test_join_unknown_room_returns_none(self):
        result = join_room("ABCD", "Kevin")

        assert result == {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }


class TestGetRoomState:
    def test_get_room_state(self):
        room_code = create_room()["room_code"]
        player = join_room(room_code, "Kevin")["player"]

        result = get_room_state(room_code)

        assert result == {
            "success": True,
            "room": {
                "room_code": room_code,
                "players": [player],
                "current_buzzer": None,
            },
        }

    def test_get_unknown_room_state_returns_none(self):
        result = get_room_state("ABCD")

        assert result == {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }


class TestBuzz:
    def test_buzz_sets_current_buzzer(self):
        room_code = create_room()["room_code"]
        player = join_room(room_code, "Kevin")["player"]

        result = buzz(room_code, player["id"])

        assert result == {
            "success": True,
            "player": player,
        }
        assert rooms[room_code]["current_buzzer"] == player

    def test_buzz_unknown_room_returns_none(self):
        result = buzz("ABCD", "fake-player-id")

        assert result == {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }

    def test_buzz_unknown_player_returns_none(self):
        room_code = create_room()["room_code"]

        result = buzz(room_code, "fake-player-id")

        assert result == {
            "success": False,
            "error": errors.PLAYER_NOT_FOUND,
        }

    def test_buzz_does_not_replace_first_buzzer(self):
        room_code = create_room()["room_code"]
        first_player = join_room(room_code, "Kevin")["player"]
        second_player = join_room(room_code, "Alex")["player"]

        first_result = buzz(room_code, first_player["id"])
        second_result = buzz(room_code, second_player["id"])

        assert first_result == {
            "success": True,
            "player": first_player,
        }
        assert second_result == {
            "success": False,
            "error": errors.BUZZER_ALREADY_LOCKED,
        }
        assert rooms[room_code]["current_buzzer"] == first_player


class TestResetBuzzer:
    def test_reset_buzzer(self):
        room_code = create_room()["room_code"]
        player = join_room(room_code, "Kevin")["player"]
        buzz(room_code, player["id"])

        result = reset_buzzer(room_code)

        assert result["success"] is True
        assert result["room"]["current_buzzer"] is None
        assert rooms[room_code]["current_buzzer"] is None

    def test_reset_unknown_room_returns_error(self):
        result = reset_buzzer("ABCD")

        assert result == {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }


class TestPlayerNameValidation:
    def test_join_room_cleans_player_name(self):
        room_code = create_room()["room_code"]

        result = join_room(room_code, "   Kevin    Fruchon   ")

        assert result["success"] is True
        assert result["player"]["name"] == "Kevin Fruchon"

    def test_join_room_rejects_empty_player_name(self):
        room_code = create_room()["room_code"]

        result = join_room(room_code, "   ")

        assert result == {
            "success": False,
            "error": errors.INVALID_PLAYER_NAME,
        }

    def test_join_room_rejects_duplicate_player_name(self):
        room_code = create_room()["room_code"]
        first_result = join_room(room_code, "Kevin")

        second_result = join_room(room_code, "Kevin")

        assert first_result["success"] is True
        assert second_result == {
            "success": False,
            "error": errors.PLAYER_NAME_ALREADY_EXISTS,
        }

    def test_join_room_rejects_duplicate_player_name_with_different_case(self):
        room_code = create_room()["room_code"]
        first_result = join_room(room_code, "Kevin")

        second_result = join_room(room_code, "kevin")

        assert first_result["success"] is True
        assert second_result == {
            "success": False,
            "error": errors.PLAYER_NAME_ALREADY_EXISTS,
        }

    def test_join_room_rejects_duplicate_player_name_with_extra_spaces(self):
        room_code = create_room()["room_code"]
        first_result = join_room(room_code, "Kevin Fruchon")

        second_result = join_room(room_code, "   kevin    fruchon   ")

        assert first_result["success"] is True
        assert second_result == {
            "success": False,
            "error": errors.PLAYER_NAME_ALREADY_EXISTS,
        }

    def test_clean_player_name_removes_extra_spaces(self):
        result = clean_player_name("   Kevin    Fruchon   ")

        assert result == "Kevin Fruchon"

    def test_normalize_player_name_removes_spaces_and_lowercases(self):
        result = normalize_player_name("   Kevin    Fruchon   ")

        assert result == "kevin fruchon"

    def test_is_player_name_available_returns_true_when_name_is_available(self):
        room = {
            "players": {
                "player-1": {
                    "id": "player-1",
                    "name": "Kevin",
                }
            }
        }

        result = is_player_name_available(room, "alex")

        assert result is True

    def test_is_player_name_available_returns_false_when_name_already_exists(self):
        room = {
            "players": {
                "player-1": {
                    "id": "player-1",
                    "name": "Kevin",
                }
            }
        }

        result = is_player_name_available(room, "kevin")

        assert result is False
