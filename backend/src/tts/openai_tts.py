from openai import OpenAI

from .tts import TTS


class OpenAITTS(TTS):

    def __init__(self) -> None:
        self.client = OpenAI()

    def text_to_speech(self, text: str):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
        )

        return response.content
