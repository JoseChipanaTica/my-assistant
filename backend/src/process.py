import uuid

from openai import OpenAI
from src.llm.llm import llm_response
from src.transcription.dg_transcription import DeepGramTranscription
from src.tts.openai_tts import OpenAITTS
from src.utils import creating_audio, creating_video, getting_frames


def process_video(video: bytes):

    video_uuid = uuid.uuid4()

    video_path = creating_video(video, video_uuid)
    audio_path = creating_audio(video_path, video_uuid)
    frames = getting_frames(video_path)

    dg_transcription = DeepGramTranscription()
    tts = OpenAITTS()
    transcript = dg_transcription.get_transcription_from_file(audio_path)

    if (transcript):
        response = llm_response(frames, transcript)
        return tts.text_to_speech(response)

    return ''


def tts(text: str):
    client = OpenAI()

    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )

    return response.content
