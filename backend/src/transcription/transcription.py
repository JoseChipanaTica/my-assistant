from abc import ABC, abstractmethod


class Transcription(ABC):
    @abstractmethod
    def set_callback(self):
        pass

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def get_realtime_transcription(self, audio_bytes):
        pass
