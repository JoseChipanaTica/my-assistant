from typing import List

from deepgram import (DeepgramClient, DeepgramClientOptions, FileSource,
                      LiveOptions, LiveTranscriptionEvents)

from .transcription import Transcription


class DeepGramTranscription(Transcription):

    def __init__(self, callback) -> None:

        config = DeepgramClientOptions(options={"keepalive": "true"})
        self.client = DeepgramClient(config=config)
        self.dg_connection = self.client.listen.asynclive.v("1")

        self.callback = callback

        async def on_message(_self, result, **kwargs):
            sentence: str = result.channel.alternatives[0].transcript
            self.collector.append(sentence.strip())

            if result.speech_final:
                if len(sentence) == 0:
                    return

                await self.callback(' '.join(self.collector))
                self.collector = []

        async def on_metadata(_self, metadata, **kwargs):
            print("")
            # print(f"\n\n{metadata}\n\n")

        async def on_error(_self, error, **kwargs):
            print("Check Error")
            #  print(f"\n\n{error}\n\n")

        self.dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        self.dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        self.dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        self.collector: List[str] = []

    async def start(self):
        options = LiveOptions(
            model="nova-2",
            smart_format=True,
            language='es'
        )
        await self.dg_connection.start(options)
        try:

            payload: FileSource = {
                "buffer": audio_bytes,
            }

            response = self.client.listen.prerecorded.v(
                "1").transcribe_file(payload, self.options)

            transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
            print("DEEPGRAM_TRANSCRIPT", transcript)
            return transcript

        except Exception as e:
            print(f"DEEPGRAM Transcription Exception: {e}")
            return ''

    async def get_realtime_transcription(self, audio_bytes):
        await self.dg_connection.send(audio_bytes)
