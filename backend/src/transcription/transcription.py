from abc import ABC, abstractmethod


class Transcription(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def get_realtime_transcription(self, audio_bytes):
        pass
