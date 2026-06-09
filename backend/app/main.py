from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager

from app.routes.rooms import router as rooms_router
from app.routes.websocket import router as websocket_router
from app.services.room_service import cleanup_inactive_rooms, restore_rooms


async def run_cleanup_task():
    while True:
        await asyncio.sleep(60)
        cleanup_inactive_rooms()


@asynccontextmanager
async def lifespan(app: FastAPI):
    restore_rooms()
    asyncio.create_task(run_cleanup_task())
    yield


app = FastAPI(title="Brian's Buzzer", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://brian-s-buzzer.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rooms_router)
app.include_router(websocket_router)


@app.get("/")
def root():
    return {"message": "Brian's Buzzer API is running"}
