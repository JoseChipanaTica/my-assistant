import json
from collections import defaultdict
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from langchain_openai import ChatOpenAI
from src.agent.agent import Agent
from src.assistant import MyAssistant
from src.stt.dg_stt import DGSTT
from src.tts.dg_tts import DGTTS
from websockets.exceptions import ConnectionClosedError

load_dotenv()

app = FastAPI()

websocket_clients = []


class ConnectionManager:
    def __init__(self):
        self.active_connections: defaultdict[str,
                                             List[WebSocket]] = defaultdict(list)

    async def connect(self, room: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[room].append(websocket)

    def disconnect(self, room: str, websocket: WebSocket):
        self.active_connections[room].remove(websocket)
        if not self.active_connections[room]:
            del self.active_connections[room]

    async def broadcast(self, room: str, audio: bytes):
        for connection in self.active_connections[room]:
            await connection.send_bytes(audio)


manager = ConnectionManager()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.websocket("/ws/{room}")
async def ws_audio(websocket: WebSocket, room: str):
    await manager.connect(room, websocket)

    stt_client = DGSTT()

    model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    agent = Agent(model)

    tts_client = DGTTS()

    process = MyAssistant(stt_client, agent, tts_client)

    await process.start()

    async def callback(speech: bytes):
        await manager.broadcast(room, speech)

    process.set_callback(callback)

    try:
        while True:
            data = await websocket.receive_json()
            if (data['type'] == 'audio'):
                audio = data['audio']
                await process.add_audio(audio)
            else:
                frame = data['frame']
                await process.add_frame(frame)

    except ConnectionClosedError as e:
        websocket_clients.remove(websocket)
