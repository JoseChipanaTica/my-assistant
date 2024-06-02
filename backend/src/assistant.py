import base64
from typing import List

from langchain_core.messages.base import BaseMessage
from langchain_core.messages.human import HumanMessage
from src.agent.agent import Agent
from src.stt.stt import STT
from src.tts.tts import TTS


class MyAssistant:

    def __init__(self, stt_client: STT, agent: Agent, tts_client: TTS):
        self.stt_client = stt_client
        self.tts_client = tts_client
        self.agent = agent
        self.messages: List[BaseMessage] = []
        self.callback = None

    def set_callback(self, callback):
        self.callback = callback

    async def add_frame(self, frame_bytes: str):
        self.messages.append(HumanMessage([{"type": "image_url", "image_url": {
            "url": f'data:image/jpg;base64,{frame_bytes}', "detail": "low"}}]))

    async def add_audio(self, audio_bytes: str):
        byte_data = base64.b64decode(audio_bytes)
        await self.stt_client.get_realtime_transcription(byte_data)

    async def run(self, transcript: str):
        if transcript:
            print("transcript:", transcript)
            result: dict = await self.agent.ainvoke(transcript, self.messages)
            self.messages = result.get('chat_history')
            text = result.get('output')
            print("text:", text)
            speech = self.tts_client.text_to_speech(text)
            await self.callback(speech)

    async def start(self):
        await self.stt_client.start()
        await self.agent.start()
        self.stt_client.set_callback(self.run)
