from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.rooms import router as rooms_router
from app.routes.websocket import router as websocket_router

app = FastAPI(title="Brian's Buzzer")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://briansbuzzer.vercel.app",
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
