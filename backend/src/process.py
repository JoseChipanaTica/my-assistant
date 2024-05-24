import asyncio
import time
import uuid

from colorama import Fore, Style
from src.llm.llm import llm_response
from src.transcription.dg_transcription import DeepGramTranscription
from src.tts.openai_tts import OpenAITTS
from src.utils import creating_audio, creating_video, getting_frames


class VideoProcessing:
    def __init__(self, video: bytes) -> None:
        self.stt_client = DeepGramTranscription()
        self.tts_client = OpenAITTS()
        self.video = video
        self.video_id = uuid.uuid4()
        self.video_path = None

    async def process_video(self):
        start_time = time.time()

        self.video_path = creating_video(self.video, self.video_id)

        transcript, frames = await asyncio.gather(self.get_video_transcription(), self.get_video_frames())

        if transcript:
            response = llm_response(frames, transcript)

            execution_time = time.time() - start_time
            print(
                f"{Fore.GREEN}Execution time: {execution_time:.2f} seconds{Style.RESET_ALL}")

            return self.tts_client.text_to_speech(response)
        return None

    async def get_video_transcription(self):
        try:
            audio_bytes = await creating_audio(self.video_path, self.video_id)
            print("Creating The Transcription")
            transcription = self.stt_client.get_transcription(audio_bytes)
            return transcription
        except Exception as e:
            print(f'Error Extracting the audio: {e}')
            return None

    async def get_video_frames(self):
        try:
            video_path = await creating_video(self.video, self.video_id)
            frames = getting_frames(video_path)
            return frames
        except Exception as e:
            print(f'Error Extracting the video: {e}')
            return None
