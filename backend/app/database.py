import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timezone

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SECRET_KEY")

supabase: Client = create_client(url, key)


def save_room(room_code: str, room_data: dict, last_activity: float):
    timestamp = datetime.fromtimestamp(last_activity, tz=timezone.utc).isoformat()
    supabase.table("rooms").upsert({
        "code": room_code,
        "data": room_data,
        "last_activity": timestamp,
    }).execute()


def load_all_rooms() -> dict:
    response = supabase.table("rooms").select("*").execute()
    return {row["code"]: row["data"] for row in response.data}


def delete_room(room_code: str):
    supabase.table("rooms").delete().eq("code", room_code).execute()