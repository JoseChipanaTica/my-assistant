import time
from typing import List

from src.image_description import image_description
from src.transcription.transcription import Transcription
from src.tts.tts import TTS


class RealTimeProcess:

    def __init__(self, stt_client: Transcription, llm_client, tts_client: TTS):
        self.stt_client = stt_client
        self.tts_client = tts_client
        self.llm_client = llm_client
        self.messages = []
        self.ws_callback = None

    def set_callback(self, callback):
        self.ws_callback = callback

    def set_messages(self, messages: List):
        self.messages = messages

    async def add_frame(self, frame_bytes):
        description = image_description(frame_bytes)
        self.messages.append(description)

    async def add_audio(self, audio_bytes):
        await self.stt_client.get_realtime_transcription(audio_bytes)

    async def callback(self, transcript: str):
        if transcript:
            print("transcript:", transcript)
            self.messages.append({"role": "user", "content": transcript})
            text = await self.llm()

            if text:
                print("text:", text)
                self.messages.append({"role": "assistant", "content": "text"})
                speech = self.tts_client.text_to_speech(text)
                await self.ws_callback(speech)

    async def start(self):
        await self.stt_client.start()
        self.stt_client.set_callback(self.callback)

    async def llm(self):
        response = await self.llm_client.chat.completions.create(
            model="gpt-4o",
            messages=self.messages[-20:],
            temperature=0,
        )

        text = response.choices[0].message.content

        return text
