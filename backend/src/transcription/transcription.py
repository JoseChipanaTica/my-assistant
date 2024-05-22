from abc import ABC, abstractmethod


class Transcription(ABC):
    @abstractmethod
    def get_transcription_from_file(self, file_path):
        pass
