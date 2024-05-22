
import os

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from src.process import process_video
from src.utils import MEDIA_DIR
from websockets.exceptions import ConnectionClosedError

load_dotenv()

app = FastAPI()

if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

websocket_clients = []


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.append(websocket)  # Add client to list

    try:
        while True:
            data = await websocket.receive_bytes()
            transcript = process_video(data)
            await websocket.send_bytes(transcript)

    except ConnectionClosedError:
        websocket_clients.remove(websocket)
