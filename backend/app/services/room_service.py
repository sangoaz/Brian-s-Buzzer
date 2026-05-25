import random
import string
import uuid

from app.constants import errors

# Stockage des salons en mémoire dans un dictionnaire Python
rooms = {}


# Génère un code aléatoire de 4 Caractères
def generate_room_code(length: int = 4) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


# Créée le salon dans rooms
def create_room() -> dict:
    # Génère un code de salon
    room_code = generate_room_code()

    # Vérifie que le code salon n'existe pas déjà, si il en trouve un, en génère un autre
    while room_code in rooms:
        room_code = generate_room_code()

    rooms[room_code] = {
        "players": {},
        "current_buzzer": None,
    }

    return {
        "success": True,
        "room_code": room_code,
    }


# Rejoindre un salon
def join_room(room_code: str, player_name: str) -> dict:
    room = rooms.get(room_code)

    if not room:
        return {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }

    cleaned_player_name = clean_player_name(player_name)
    normalized_player_name = normalize_player_name(player_name)

    if not normalized_player_name:
        return {
            "success": False,
            "error": errors.INVALID_PLAYER_NAME,
        }

    if not is_player_name_available(room, normalized_player_name):
        return {
            "success": False,
            "error": errors.PLAYER_NAME_ALREADY_EXISTS,
        }

    player_id = str(uuid.uuid4())

    player = {
        "id": player_id,
        "name": cleaned_player_name,
    }

    room["players"][player_id] = player

    return {"success": True, "player": player}


# Lire l'état du salon
def get_room_state(room_code: str):
    room = rooms.get(room_code)

    if not room:
        return {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }

    return {
        "success": True,
        "room": get_public_room(room),
    }


# Buzzer
def buzz(room_code: str, player_id: str) -> dict:
    # Vérifie que le salon existe
    room = rooms.get(room_code)

    if not room:
        return {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }

    # Vérifie que le joueur existe
    player = room["players"].get(player_id)

    if not player:
        return {
            "success": False,
            "error": errors.PLAYER_NOT_FOUND,
        }

    # Si quelqu'un a déjà buzzé, on ne remplace pas le joueur
    if room["current_buzzer"] is not None:
        return {
            "success": False,
            "error": errors.BUZZER_ALREADY_LOCKED,
        }

    # Dans le cas où personne n'a encore buzzé
    room["current_buzzer"] = player

    return {"success": True, "player": player}


# Reset du buzzer
def reset_buzzer(room_code: str) -> dict:
    room = rooms.get(room_code)

    if not room:
        return {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }

    room["current_buzzer"] = None

    return get_room_state(room_code)


# Vérifier si un pseudo existe déjà dans le salon
def is_player_name_available(room, player_name: str) -> bool:
    for player in room["players"].values():
        if player["name"].lower() == player_name.lower():
            return False

    return True


# Nettoyer le pseudo pour l'affichage
def clean_player_name(player_name: str) -> str:
    words = player_name.split()
    return " ".join(words)


# Normaliser le pseudo pour les comparaisons
def normalize_player_name(player_name: str) -> str:
    cleaned_name = clean_player_name(player_name)
    return cleaned_name.lower()


# Déconnecter le joueur
def remove_player(room_code: str, player_id: str) -> dict:
    room = rooms.get(room_code)

    if not room:
        return {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }

    room["players"].pop(player_id, None)

    if room.get("current_buzzer") == player_id:
        room["current_buzzer"] = None

    return {
        "success": True,
        "room": get_public_room(room),
    }


# =========================
# Helpers
# =========================


# Transforme une room interne en room envoyable au frontend
def get_public_room(room: dict) -> dict:
    return {
        **room,
        "players": list(room["players"].values()),
    }
