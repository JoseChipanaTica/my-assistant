from typing import List

from deepgram import (DeepgramClient, DeepgramClientOptions, LiveOptions,
                      LiveTranscriptionEvents)

from .transcription import Transcription


class DeepGramTranscription(Transcription):

    def __init__(self):

        config = DeepgramClientOptions(options={"keepalive": "true"})
        self.client = DeepgramClient(config=config)
        self.dg_connection = self.client.listen.asynclive.v("1")
        self.collector: List[str] = []
        self.callback = None

        async def on_message(_self, result, **kwargs):
            sentence: str = result.channel.alternatives[0].transcript
            self.collector.append(sentence.strip())

            if result.speech_final:
                if len(sentence) == 0:
                    return
                await self.callback(' '.join(self.collector).strip())
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

    def set_callback(self, callback):
        self.callback = callback

    async def start(self):
        options = LiveOptions(
            model="nova-2",
            smart_format=True,
            language='en'
        )
        await self.dg_connection.start(options)

    async def get_realtime_transcription(self, audio_bytes):
        await self.dg_connection.send(audio_bytes)
