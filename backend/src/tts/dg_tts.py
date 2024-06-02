import os

import aiohttp
import requests

from .tts import TTS


class DGTTS(TTS):

    def __init__(self):
        self.client = None
        self.callback = None
        self.DEEPGRAM_URL = f"{os.getenv('DEEPGRAM_URL')}?model=aura-asteria-en"
        self.DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

    def set_callback(self, callback):
        self.callback = callback

    def text_to_speech(self, text: str):

        payload = {
            "text": text
        }

        headers = {
            "Authorization": f"Token {self.DEEPGRAM_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            self.DEEPGRAM_URL, headers=headers, json=payload)
        return response.content

    async def text_to_speech_realtime(self, text: str):

        payload = {
            "text": text
        }

        headers = {
            "Authorization": f"Token {self.DEEPGRAM_API_KEY}",
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.DEEPGRAM_URL, headers=headers, json=payload) as response:
                async for chunk in response.content.iter_chunked(1024):
                    if chunk:
                        await self.callback(chunk)
