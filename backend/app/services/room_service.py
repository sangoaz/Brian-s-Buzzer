import random
import string
import uuid

# Stockage des salons en mémoire dans un dictionnaire Python
rooms = {}


# Génère un code aléatoire de 4 Caractères
def generate_room_code(length: int = 4) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


# Créée le salon dans rooms
def create_room() -> str:
    # Génère un code de salon
    room_code = generate_room_code()

    # Vérifie que le code salon n'existe pas déjà, si il en trouve un, en génère un autre
    while room_code in rooms:
        room_code = generate_room_code()

    rooms[room_code] = {
        "players": {},
        "current_buzzer": None,
    }

    return room_code


# Rejoindre un salon
def join_room(room_code: str, player_name: str) -> dict | None:
    room = rooms.get(room_code)

    if not room:
        return None

    cleaned_player_name = clean_player_name(player_name)
    normalized_player_name = normalize_player_name(player_name)

    if not normalized_player_name:
        return None

    if not is_player_name_available(room, normalized_player_name):
        return None

    player_id = str(uuid.uuid4())

    player = {
        "id": player_id,
        "name": cleaned_player_name,
    }

    room["players"][player_id] = player

    return player


# Lire l'état du salon
def get_room_state(room_code: str) -> dict | None:
    room = rooms.get(room_code)

    if not room:
        return None

    return {
        "room_code": room_code,
        "players": list(room["players"].values()),
        "current_buzzer": room["current_buzzer"],
    }


# Buzzer
def buzz(room_code: str, player_id: str) -> dict | None:
    # Vérifie que le salon existe
    room = rooms.get(room_code)

    if not room:
        return None

    # Vérifie que le joueur existe
    player = room["players"].get(player_id)

    if not player:
        return None

    # Si quelqu'un a déjà buzzé, on ne remplace pas le joueur
    if room["current_buzzer"] is not None:
        return room["current_buzzer"]

    # Dans le cas où personne n'a encore buzzé
    room["current_buzzer"] = player

    return player


# Reset du buzzer
def reset_buzzer(room_code: str) -> dict | None:
    room = rooms.get(room_code)

    if not room:
        return None

    room["current_buzzer"] = None

    return get_room_state(room_code)


# Vérifier si un pseudo existe déjà dans le salon
def is_player_name_available(room: dict, normalized_player_name: str) -> bool:
    for player in room["players"].values():
        existing_player_name = player.get("name")
        normalized_existing_player_name = normalize_player_name(existing_player_name)

        if normalized_existing_player_name == normalized_player_name:
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
