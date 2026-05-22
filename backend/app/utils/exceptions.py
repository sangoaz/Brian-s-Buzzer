from fastapi import HTTPException

from app.constants import errors


# Helper errors
def raise_service_error(error_code: str):
    if error_code == errors.ROOM_NOT_FOUND:
        raise HTTPException(status_code=404, detail=error_code)

    if error_code == errors.PLAYER_NOT_FOUND:
        raise HTTPException(status_code=404, detail=error_code)

    if error_code == errors.INVALID_PLAYER_NAME:
        raise HTTPException(status_code=400, detail=error_code)

    if error_code == errors.PLAYER_NAME_ALREADY_EXISTS:
        raise HTTPException(status_code=409, detail=error_code)

    if error_code == errors.BUZZER_ALREADY_LOCKED:
        raise HTTPException(status_code=409, detail=error_code)

    raise HTTPException(status_code=400, detail=error_code)
