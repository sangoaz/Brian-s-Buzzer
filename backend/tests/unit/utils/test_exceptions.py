import pytest
from fastapi import HTTPException

from app.constants import errors
from app.utils.exceptions import raise_service_error


class TestRaiseServiceError:
    @pytest.mark.parametrize(
        "error_code, expected_status",
        [
            (errors.ROOM_NOT_FOUND, 404),
            (errors.PLAYER_NOT_FOUND, 404),
            (errors.INVALID_PLAYER_NAME, 400),
            (errors.PLAYER_NAME_ALREADY_EXISTS, 409),
            (errors.BUZZER_ALREADY_LOCKED, 409),
        ],
    )
    def test_raise_service_error_known_errors(
        self,
        error_code,
        expected_status,
    ):
        with pytest.raises(HTTPException) as exc:
            raise_service_error(error_code)

        assert exc.value.status_code == expected_status
        assert exc.value.detail == error_code

    def test_raise_service_error_unknown_error(self):
        with pytest.raises(HTTPException) as exc:
            raise_service_error("UNKNOWN_ERROR")

        assert exc.value.status_code == 400
        assert exc.value.detail == "UNKNOWN_ERROR"
