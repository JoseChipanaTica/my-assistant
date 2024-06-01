from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from openai import AsyncOpenAI
from src.process import RealTimeProcess
from src.transcription.dg_transcription import DeepGramTranscription
from src.tts.deepgram_tts import DeepGramTTS
from src.tts.openai_tts import OpenAITTS
from src.utils import SYSTEM_PROMPT
from websockets.exceptions import ConnectionClosedError

load_dotenv()

app = FastAPI()

websocket_clients = []

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

stt_client = DeepGramTranscription()
llm_client = AsyncOpenAI()
tts_client = DeepGramTTS()
process = RealTimeProcess(stt_client, llm_client, tts_client)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.websocket("/ws/audio")
async def ws_audio(websocket: WebSocket):

    await websocket.accept()
    await process.start()

    process.messages = messages

    websocket_clients.append(websocket)

    async def callback(speech: bytes):
        await websocket.send_bytes(speech)

    process.set_callback(callback)

    try:
        while True:
            data = await websocket.receive_bytes()
            await process.add_audio(data)

    except ConnectionClosedError as e:
        websocket_clients.remove(websocket)


@app.websocket("/ws/video")
async def ws_video(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_bytes()
            await process.add_frame(data)

    except ConnectionClosedError:
        websocket_clients.remove(websocket)
