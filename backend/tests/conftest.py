import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.room_service import rooms


@pytest.fixture(autouse=True)
def clear_rooms():
    rooms.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def room_code():
    from app.services.room_service import create_room

    return create_room()


@pytest.fixture
def player(room_code):
    from app.services.room_service import join_room

    return join_room(room_code, "Kevin")
