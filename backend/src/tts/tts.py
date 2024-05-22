from abc import ABC, abstractmethod


class TTS(ABC):
    @abstractmethod
    def text_to_speech(self, text: str):
        pass
