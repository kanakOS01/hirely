import logging
import assemblyai as aai
from assemblyai.streaming.v3 import (
    BeginEvent,
    StreamingClient,
    StreamingClientOptions,
    StreamingError,
    StreamingEvents,
    StreamingParameters,
    StreamingSessionParameters,
    TerminationEvent,
    TurnEvent,
)
from typing import Callable, Optional, Type


class VoiceTranscriber:
    def __init__(self, api_key: str, on_transcript: Optional[Callable[[str, bool], None]] = None):
        self.api_key = api_key
        self.on_transcript = on_transcript  # Callback for receiving transcripts
        self.client = StreamingClient(
            StreamingClientOptions(
                api_key=self.api_key,
                api_host="streaming.assemblyai.com",
            )
        )
        self._register_events()

    def _register_events(self):
        self.client.on(StreamingEvents.Begin, self._on_begin)
        self.client.on(StreamingEvents.Turn, self._on_turn)
        self.client.on(StreamingEvents.Termination, self._on_terminated)
        self.client.on(StreamingEvents.Error, self._on_error)

    def _on_begin(self, client: Type[StreamingClient], event: BeginEvent):
        print(f"Session started: {event.id}")

    def _on_turn(self, client: Type[StreamingClient], event: TurnEvent):
        print(f"{event.transcript} ({event.end_of_turn})")
        if self.on_transcript:
            self.on_transcript(event.transcript, event.end_of_turn)

        if event.end_of_turn and not event.turn_is_formatted:
            client.set_params(StreamingSessionParameters(format_turns=True))

    def _on_terminated(self, client: Type[StreamingClient], event: TerminationEvent):
        print(f"Session terminated: {event.audio_duration_seconds} seconds of audio processed")

    def _on_error(self, client: Type[StreamingClient], error: StreamingError):
        print(f"Error occurred: {error}")

    def run(self):
        self.client.connect(
            StreamingParameters(
                sample_rate=16000,
                format_turns=True,
            )
        )
        try:
            self.client.stream(
                aai.extras.MicrophoneStream(sample_rate=16000)
            )
        finally:
            self.client.disconnect(terminate=True)
