
import base64
import os

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from openai import OpenAI
from src.transcription.dg_transcription import DeepGramTranscription
from src.tts.openai_tts import OpenAITTS
from src.utils import MEDIA_DIR
from websockets.exceptions import ConnectionClosedError

SYSTEM_PROMPT = """
                Your primary purpose is to assist users by generating human-like text based on the input you receive. 
                Offer accurate and up-to-date information on a wide range of topics, respond to queries clearly and concisely, and help with tasks such as writing, summarizing, translating, generating ideas, or creating content.
                Engage in meaningful and coherent conversations, maintaining context and providing relevant responses.
                Adhere to ethical guidelines, ensuring responses are respectful, non-discriminatory, and free of harmful content, while respecting user privacy and confidentiality. 
                Provide citations or references when applicable to ensure credibility and allow users to verify information. Strive to stay neutral and unbiased, presenting information factually and impartially. 
                Always aim to be helpful, informative, and respectful in all interactions.
                """


load_dotenv()

app = FastAPI()

if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

websocket_clients = []

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

client = OpenAI()

tts = OpenAITTS()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.websocket("/ws/audio")
async def websocket_audio(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.append(websocket)  # Add client to list

    async def callback(transcript: str):
        print(f"speaker: {transcript}")

        messages.append({"role": "user", "content": transcript})

        if transcript:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages[-20:],
                temperature=0,
            )

            text = response.choices[0].message.content

            print("LLM: ", text)

            messages.append({"role": "assistant", "content": text})

            audio_text = tts.text_to_speech(text)
            await websocket.send_bytes(audio_text)

    transcriptor = DeepGramTranscription(callback)
    await transcriptor.start()

    try:
        while True:
            data = await websocket.receive_bytes()
            await transcriptor.get_realtime_transcription(data)

    except ConnectionClosedError as e:
        websocket_clients.remove(websocket)


@app.websocket("/ws/video")
async def websocket_video(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_bytes()
            base64_bytes = base64.b64encode(data)
            base64_string = base64_bytes.decode('utf-8')
            messages.append({"role": "user", "content": [{"type": "image_url", "image_url": {
                            "url": f'data:image/jpg;base64,{base64_string}', "detail": "low"}}]})

    except ConnectionClosedError:
        websocket_clients.remove(websocket)
