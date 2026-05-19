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
    # cherche le salon
    room = rooms.get(room_code)

    # Si le salon n'existe pas
    if not room:
        return None

    # Créée un identifiant unique pour le joueur
    player_id = str(uuid.uuid4())

    # Création du joueur
    player = {
        "id": player_id,
        "name": player_name,
    }

    # Ajoute le joueur au salon
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