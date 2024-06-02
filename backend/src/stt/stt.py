from abc import ABC, abstractmethod


class STT(ABC):
    @abstractmethod
    def set_callback(self, callback):
        pass

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    def get_transcription(self, audio_bytes):
        pass

    @abstractmethod
    async def get_realtime_transcription(self, audio_bytes):
        pass
