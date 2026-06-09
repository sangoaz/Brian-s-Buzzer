import random
import string
import time
import uuid

from app.database import save_room, load_all_rooms, delete_room
from app.constants import errors

# Stockage des salons en mémoire dans un dictionnaire Python
rooms = {}


# Génère un code aléatoire de 4 Caractères
def generate_room_code(length: int = 4) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


# Créée le salon dans rooms
def create_room(settings: dict = None) -> dict:
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
        "blocked_players": {},
        "settings": settings
        or {
            "max_rounds": None,
            "block_on_wrong": False,
        },
        "buzz_history": {},
        "last_activity": time.time(),
    }

    # Sauvegarde de l'état de la room en base de donnée
    save_room(room_code, rooms[room_code], rooms[room_code]["last_activity"])

    return {
        "success": True,
        "room_code": room_code,
        "host_id": host_id,
        "status": "waiting",
        "settings": rooms[room_code]["settings"],
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

    # Sauvegarde de l'état de la room en base de donnée
    save_room(room_code, room, room["last_activity"])

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
    touch_room(room)

    # Sauvegarde de l'état de la room en base de donnée
    save_room(room_code, room, room["last_activity"])

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
    touch_room(room)
    # Sauvegarde de l'état de la room en base de donnée
    save_room(room_code, room, room["last_activity"])

    return {
        "success": True,
        "room": get_public_room(room),
    }


# Recommencer une partie
def restart_game(room_code: str, requester_id: str) -> dict:
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

    if room["status"] != "finished":
        return {
            "success": False,
            "error": errors.GAME_IN_PROGRESS,
        }

    room["status"] = "waiting"
    room["round"] = 1
    room["scores"] = {player_id: 0 for player_id in room["players"]}
    room["current_buzzer"] = None
    room["blocked_players"] = {}
    room["buzz_history"] = {}

    # Sauvegarde de l'état de la room en base de donnée
    save_room(room_code, room, room["last_activity"])

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

    # Vérifie si le joueur est bloqué suite à une mauvaise réponse
    blocked_players = room.get("blocked_players", {})
    if player_id in blocked_players:
        if time.time() < blocked_players[player_id]:
            return {
                "success": False,
                "error": errors.PLAYER_BLOCKED,
            }
        else:
            # Le blocage a expiré, on nettoie
            del blocked_players[player_id]

    # Dans le cas où personne n'a encore buzzé
    room["current_buzzer"] = player

    # On ajoute le buzz dans un historique pour savoir qui a buzzé et à quelle manche
    round_num = room.get("round", 1)
    if round_num not in room["buzz_history"]:
        room["buzz_history"][round_num] = []
    room["buzz_history"][round_num].append(
        {
            "id": player["id"],
            "name": player["name"],
            "result": "pending",
        }
    )

    touch_room(room)

    # Sauvegarde de l'état de la room en base de donnée
    save_room(room_code, room, room["last_activity"])

    return {"success": True, "player": player}


# Passe à la prochaine manche
def next_round(room_code: str, requester_id: str) -> dict:
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
    room["blocked_players"] = {}
    room["round"] = room.get("round", 1) + 1
    touch_room(room)

    max_rounds = room["settings"].get("max_rounds")
    if max_rounds and room["round"] > max_rounds:
        room["status"] = "finished"

    # Sauvegarde de l'état de la room en base de donnée
    save_room(room_code, room, room["last_activity"])

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

    # Sauvegarde de l'état de la room en base de donnée
    save_room(room_code, room, room["last_activity"])

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

    # Sauvegarde de l'état de la room en base de donnée
    save_room(room_code, room, room["last_activity"])

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
    room["blocked_players"] = {}

    round_num = room.get("round", 1)
    for entry in reversed(room["buzz_history"].get(round_num, [])):
        if entry["id"] == player_id:
            entry["result"] = "correct"
            break
    room["round"] = room.get("round", 1) + 1

    max_rounds = room["settings"].get("max_rounds")
    if max_rounds and room["round"] > max_rounds:
        room["status"] = "finished"

    touch_room(room)

    # Sauvegarde de l'état de la room en base de donnée
    save_room(room_code, room, room["last_activity"])

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

    buzzer_id = room["current_buzzer"]["id"]
    room["current_buzzer"] = None

    # Si la pénalité est activée, le joueur perd un point si mauvaise réponse
    if room["settings"].get("penalty_on_wrong", False):
        current_score = room["scores"].get(buzzer_id, 0)
        room["scores"][buzzer_id] = max(0, current_score - 1)

    # Si block_on_wrong est activé, bloque le joueur pendant X secondes
    if room["settings"].get("block_on_wrong", False):
        block_duration = room["settings"].get("block_duration", 5)
        room["blocked_players"][buzzer_id] = time.time() + block_duration

    round_num = room.get("round", 1)
    for entry in reversed(room["buzz_history"].get(round_num, [])):
        if entry["id"] == buzzer_id:
            entry["result"] = "wrong"
            break

    touch_room(room)

    # Sauvegarde de l'état de la room en base de donnée
    save_room(room_code, room, room["last_activity"])

    return {
        "success": True,
        "room": get_public_room(room),
    }


# =========================
# Helpers
# =========================


# Transforme une room interne en room envoyable au frontend
def get_public_room(room: dict) -> dict:
    now = time.time()
    active_blocked = [
        pid for pid, until in room.get("blocked_players", {}).items() if until > now
    ]

    return {
        "code": room["code"],
        "players": list(room["players"].values()),
        "current_buzzer": room["current_buzzer"],
        "status": room.get("status", "waiting"),
        "round": room.get("round", 1),
        "scores": room.get("scores", {}),
        "blocked_players": active_blocked,
        "buzz_history": room.get("buzz_history", {}),
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


TTL_SECONDS = 30 * 60  # 30 minutes


# Enregistrer la dernière activité
def touch_room(room: dict):
    room["last_activity"] = time.time()


# Supprimer les room inactives
def cleanup_inactive_rooms():
    now = time.time()
    to_delete = [
        code
        for code, room in list(rooms.items())
        if now - room.get("last_activity", now) > TTL_SECONDS
    ]
    for code in to_delete:
        del rooms[code]
        delete_room(code)

# Restaurer une room au démarage du server
def restore_rooms():
    loaded = load_all_rooms()
    for room in loaded.values():
        if "buzz_history" in room:
            room["buzz_history"] = {int(k): v for k, v in room["buzz_history"].items()}
    rooms.update(loaded)