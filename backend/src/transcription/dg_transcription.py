from deepgram import DeepgramClient, FileSource, PrerecordedOptions
from src.utils import get_bytes_from_file

from .transcription import Transcription


class DeepGramTranscription(Transcription):

    def __init__(self) -> None:

        self.client = DeepgramClient()
        self.options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            language='es'
        )

    def get_transcription_from_file(self, file_path) -> str:

        try:

            buffer_data = get_bytes_from_file(file_path)

            payload: FileSource = {
                "buffer": buffer_data,
            }

            response = self.client.listen.prerecorded.v(
                "1").transcribe_file(payload, self.options)

            transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
            print("DEEPGRAM_TRANSCRIPT", transcript)
            return transcript

        except Exception as e:
            print(f"DEEPGRAM Transcription Exception: {e}")
            return ''
