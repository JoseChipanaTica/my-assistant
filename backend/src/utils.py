import base64
import os
import subprocess
import time

import cv2
from colorama import Fore, Style  # Import color constants
from moviepy.editor import VideoFileClip

MEDIA_DIR = "files"


def get_bytes_from_file(file_path):
    with open(file_path, "rb") as file:
        buffer_data = file.read()
        return buffer_data


def creating_video(video: bytes, video_uuid: str):
    start_time = time.time()

    video_file_path = os.path.join(MEDIA_DIR, f"{video_uuid}.webm")

    with open(video_file_path, "wb") as video_file:
        video_file.write(video)
        video_file.close()

    # Convert webm to mp4 using ffmpeg
    output_file_path = os.path.join(MEDIA_DIR, f"{video_uuid}.mp4")
    ffmpeg_command = ["ffmpeg", "-i", video_file_path, output_file_path]

    try:
        subprocess.run(ffmpeg_command, check=True)

        execution_time = time.time() - start_time
        print(
            f"{Fore.GREEN}Execution time: {execution_time:.2f} seconds{Style.RESET_ALL}")
        return output_file_path
    except subprocess.CalledProcessError as e:
        execution_time = time.time() - start_time
        print(
            f"{Fore.RED}Execution time (failed): {execution_time:.2f} seconds{Style.RESET_ALL}")
        #  print("Error converting video:", e)
        return ""  # Return empty string i


def creating_audio(video_path: str, video_uuid: str):
    audio_path = os.path.join(MEDIA_DIR, f"{video_uuid}.mp3")
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, bitrate="32k")
    clip.audio.close()
    clip.close()

    return audio_path


def getting_frames(video_path: str):
    video = cv2.VideoCapture(video_path)

    base64Frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

    video.release()

    return base64Frames[0::60]
