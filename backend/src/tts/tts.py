from abc import ABC, abstractmethod


class TTS(ABC):
    @abstractmethod
    def set_callback(self, callback):
        pass

    @abstractmethod
    def text_to_speech(self, text: str):
        pass

    @abstractmethod
    async def text_to_speech_realtime(self, text: str):
        pass
