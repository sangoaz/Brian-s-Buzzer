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

    host_id = str(uuid.uuid4())

    rooms[room_code] = {
        "code": room_code,
        "host_id": host_id,
        "players": {},
        "current_buzzer": None,
        "status": "waiting",
        "round": 1,
        "scores": {},
    }

    return {
        "success": True,
        "room_code": room_code,
        "host_id": host_id,
        "status": "waiting",
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
    room["scores"][player_id] = 0

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


# Commencer la partie
def start_game(room_code: str, requester_id: str) -> dict:
    room = rooms.get(room_code)

    if not room:
        return {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }

    if not can_manage_room(room, requester_id):
        return {
            "success": False,
            "error": errors.NOT_HOST_ACTION,
        }

    room["status"] = "playing"
    room["current_buzzer"] = None

    return {
        "success": True,
        "room": get_public_room(room),
    }


# Finir la parte
def end_game(room_code: str, requester_id: str) -> dict:
    room = rooms.get(room_code)

    if not room:
        return {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }

    if not can_manage_room(room, requester_id):
        return {
            "success": False,
            "error": errors.NOT_HOST_ACTION,
        }

    room["status"] = "finished"
    room["current_buzzer"] = None

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

    if room.get("status", "waiting") != "playing":
        return {
            "success": False,
            "error": errors.GAME_NOT_STARTED,
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
def reset_buzzer(room_code: str, requester_id: str) -> dict:
    room = rooms.get(room_code)

    if not room:
        return {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }

    if not can_manage_room(room, requester_id):
        return {
            "success": False,
            "error": errors.NOT_HOST_ACTION,
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

    if player_id not in room["players"]:
        return {
            "success": False,
            "error": errors.PLAYER_NOT_FOUND,
        }

    room["scores"].pop(player_id, None)
    room["players"].pop(player_id)

    current_buzzer = room.get("current_buzzer")

    if current_buzzer and current_buzzer["id"] == player_id:
        room["current_buzzer"] = None

    return {
        "success": True,
        "room": get_public_room(room),
    }


# Fonction permettant à l'host de kick un joueur
def kick_player(room_code: str, requester_id: str, player_id: str) -> dict:
    room = rooms.get(room_code)

    if not room:
        return {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }

    if not can_manage_room(room, requester_id):
        return {
            "success": False,
            "error": errors.NOT_HOST_ACTION,
        }

    if player_id not in room["players"]:
        return {
            "success": False,
            "error": errors.PLAYER_NOT_FOUND,
        }

    room["scores"].pop(player_id, None)
    room["players"].pop(player_id, None)

    current_buzzer = room.get("current_buzzer")

    if current_buzzer and current_buzzer["id"] == player_id:
        room["current_buzzer"] = None

    return {
        "success": True,
        "room": get_public_room(room),
    }


# Fonction permettant à l'host de valider une réponse
def validate_answer(room_code: str, requester_id: str) -> dict:
    room = rooms.get(room_code)

    if not room:
        return {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }

    if not can_manage_room(room, requester_id):
        return {
            "success": False,
            "error": errors.NOT_HOST_ACTION,
        }

    current_buzzer = room.get("current_buzzer")

    if not current_buzzer:
        return {
            "success": False,
            "error": errors.NO_CURRENT_BUZZER,
        }

    player_id = current_buzzer["id"]

    room["scores"][player_id] = room["scores"].get(player_id, 0) + 1
    room["current_buzzer"] = None
    room["round"] = room.get("round", 1) + 1

    return {
        "success": True,
        "room": get_public_room(room),
    }


# Fonction permettant à l'host de refuser une réponse
def reject_answer(room_code: str, requester_id: str) -> dict:
    room = rooms.get(room_code)

    if not room:
        return {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }

    if not can_manage_room(room, requester_id):
        return {
            "success": False,
            "error": errors.NOT_HOST_ACTION,
        }

    if not room.get("current_buzzer"):
        return {
            "success": False,
            "error": errors.NO_CURRENT_BUZZER,
        }

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
        "code": room["code"],
        "players": list(room["players"].values()),
        "current_buzzer": room["current_buzzer"],
        "status": room.get("status", "waiting"),
        "round": room.get("round", 1),
        "scores": room.get("scores", {}),
    }


# Vérifier que celui qui demande une action de gestion est bien l’hôte du salon
def can_manage_room(room: dict, requester_id: str) -> bool:
    return room.get("host_id") == requester_id


# Un client peut se connecter à la room si et seulement si c'est un host ou un joueur de la room
def can_connect_to_room(room_code: str, connection_id: str) -> dict:
    room = rooms.get(room_code)

    if not room:
        return {
            "success": False,
            "error": errors.ROOM_NOT_FOUND,
        }

    is_host = room.get("host_id") == connection_id
    is_player = connection_id in room["players"]

    if not is_host and not is_player:
        return {
            "success": False,
            "error": errors.UNAUTHORIZED_CONNECTION,
        }

    return {
        "success": True,
        "room": room,
    }
