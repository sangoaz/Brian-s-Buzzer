from unittest.mock import patch

from app.constants import errors
from app.services.room_service import (
    rooms,
    create_room,
    join_room,
    get_room_state,
    buzz,
    next_round,
    validate_answer,
    reject_answer,
    assign_player_team,
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


class TestNextRound:
    def test_next_round(self):
        room_code = create_room()["room_code"]
        player = join_room(room_code, "Kevin")["player"]
        buzz(room_code, player["id"])

        result = next_round(room_code)

        assert result["success"] is True
        assert result["room"]["current_buzzer"] is None
        assert rooms[room_code]["current_buzzer"] is None

    def test_reset_unknown_room_returns_error(self):
        result = next_round("ABCD")

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


class TestAssignPlayerTeam:
    def test_assign_player_to_team(self):
        with patch("app.services.room_service.save_room"):
            room = create_room({"teams": ["Rouges", "Bleus"]})
            room_code = room["room_code"]
            host_id = room["host_id"]
            player = join_room(room_code, "Kevin")["player"]

            result = assign_player_team(room_code, host_id, player["id"], "0")

            assert result["success"] is True
            assert rooms[room_code]["players"][player["id"]]["team_id"] == "0"
            assert result["room"]["teams"] == [
                {"id": "0", "name": "Rouges"},
                {"id": "1", "name": "Bleus"},
            ]

    def test_unassign_player_with_none(self):
        with patch("app.services.room_service.save_room"):
            room = create_room({"teams": ["Rouges", "Bleus"]})
            room_code = room["room_code"]
            host_id = room["host_id"]
            player = join_room(room_code, "Kevin")["player"]
            assign_player_team(room_code, host_id, player["id"], "0")

            result = assign_player_team(room_code, host_id, player["id"], None)

            assert result["success"] is True
            assert rooms[room_code]["players"][player["id"]]["team_id"] is None

    def test_assign_player_team_requires_host(self):
        with patch("app.services.room_service.save_room"):
            room = create_room({"teams": ["Rouges", "Bleus"]})
            room_code = room["room_code"]
            player = join_room(room_code, "Kevin")["player"]

            result = assign_player_team(room_code, "not-the-host", player["id"], "0")

            assert result == {
                "success": False,
                "error": errors.NOT_HOST_ACTION,
            }

    def test_assign_player_team_unknown_team_id(self):
        with patch("app.services.room_service.save_room"):
            room = create_room({"teams": ["Rouges", "Bleus"]})
            room_code = room["room_code"]
            host_id = room["host_id"]
            player = join_room(room_code, "Kevin")["player"]

            result = assign_player_team(room_code, host_id, player["id"], "99")

            assert result == {
                "success": False,
                "error": errors.TEAM_NOT_FOUND,
            }

    def test_assign_player_team_when_teams_not_enabled(self):
        with patch("app.services.room_service.save_room"):
            room = create_room()  # pas de "teams" dans les settings
            room_code = room["room_code"]
            host_id = room["host_id"]
            player = join_room(room_code, "Kevin")["player"]

            result = assign_player_team(room_code, host_id, player["id"], "0")

            assert result == {
                "success": False,
                "error": errors.TEAMS_NOT_ENABLED,
            }

    def test_assign_player_team_unknown_player(self):
        with patch("app.services.room_service.save_room"):
            room = create_room({"teams": ["Rouges", "Bleus"]})
            room_code = room["room_code"]
            host_id = room["host_id"]

            result = assign_player_team(room_code, host_id, "fake-player-id", "0")

            assert result == {
                "success": False,
                "error": errors.PLAYER_NOT_FOUND,
            }


class TestTeamScores:
    def test_team_scores_sum_individual_scores_of_members(self):
        with patch("app.services.room_service.save_room"):
            room = create_room({"teams": ["Rouges", "Bleus"]})
            room_code = room["room_code"]
            host_id = room["host_id"]

            kevin = join_room(room_code, "Kevin")["player"]
            alex = join_room(room_code, "Alex")["player"]
            sam = join_room(room_code, "Sam")["player"]

            assign_player_team(room_code, host_id, kevin["id"], "0")
            assign_player_team(room_code, host_id, alex["id"], "0")
            assign_player_team(room_code, host_id, sam["id"], "1")

            rooms[room_code]["status"] = "playing"

            # Kevin (équipe Rouges) buzz et a la bonne réponse -> +1 pour Rouges
            buzz(room_code, kevin["id"])
            result = validate_answer(room_code, host_id)

            assert result["room"]["team_scores"] == {"0": 1, "1": 0}

    def test_team_scores_empty_when_teams_not_enabled(self):
        with patch("app.services.room_service.save_room"):
            room = create_room()
            room_code = room["room_code"]

            result = get_room_state(room_code)

            assert result["room"]["teams"] == []
            assert result["room"]["team_scores"] == {}


class TestRejectAnswerTeamBlocking:
    def test_reject_answer_blocks_whole_team_when_teams_enabled(self):
        with patch("app.services.room_service.save_room"):
            room = create_room({
                "teams": ["Rouges", "Bleus"],
                "block_on_wrong": True,
                "block_duration": 5,
            })
            room_code = room["room_code"]
            host_id = room["host_id"]

            kevin = join_room(room_code, "Kevin")["player"]
            alex = join_room(room_code, "Alex")["player"]
            sam = join_room(room_code, "Sam")["player"]

            assign_player_team(room_code, host_id, kevin["id"], "0")  # Rouges
            assign_player_team(room_code, host_id, alex["id"], "0")  # Rouges
            assign_player_team(room_code, host_id, sam["id"], "1")   # Bleus

            rooms[room_code]["status"] = "playing"
            buzz(room_code, kevin["id"])

            result = reject_answer(room_code, host_id)

            blocked = result["room"]["blocked_players"]
            assert kevin["id"] in blocked
            assert alex["id"] in blocked
            assert sam["id"] not in blocked

    def test_reject_answer_blocks_only_player_when_teams_disabled(self):
        with patch("app.services.room_service.save_room"):
            room = create_room({
                "block_on_wrong": True,
                "block_duration": 5,
            })
            room_code = room["room_code"]
            host_id = room["host_id"]

            kevin = join_room(room_code, "Kevin")["player"]
            alex = join_room(room_code, "Alex")["player"]

            rooms[room_code]["status"] = "playing"
            buzz(room_code, kevin["id"])

            result = reject_answer(room_code, host_id)

            blocked = result["room"]["blocked_players"]
            assert kevin["id"] in blocked
            assert alex["id"] not in blocked


class TestPublicRoomSettings:
    # Le front a besoin de max_rounds et block_duration (entre autres) pour
    # rester synchronisé avec la vraie config plutôt que deviner des valeurs
    # par défaut (cf. bug du timer de blocage fixé à 5s côté client).
    def test_get_room_state_exposes_settings(self):
        with patch("app.services.room_service.save_room"):
            room = create_room({
                "max_rounds": 10,
                "block_on_wrong": True,
                "block_duration": 3,
            })
            room_code = room["room_code"]

            state = get_room_state(room_code)

            assert state["room"]["settings"]["max_rounds"] == 10
            assert state["room"]["settings"]["block_duration"] == 3

    def test_get_room_state_settings_defaults_when_room_created_without_settings(self):
        with patch("app.services.room_service.save_room"):
            room = create_room()
            room_code = room["room_code"]

            state = get_room_state(room_code)

            assert state["room"]["settings"] == {"max_rounds": None, "block_on_wrong": False}
