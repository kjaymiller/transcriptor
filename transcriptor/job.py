from transcriptor.speakers import Speaker
from transcriptor.markers import Marker

import typing

class Job:
    def __init__(
            self,
            name: str,
            base_text: str,
            markers: typing.List,
            transcription: typing.Dict,
            transcription_itesm: typing.List,
            speakers: typing.List,
            ):

        self.name = name
        self.base_text = base_text
        self.markers = markers
        self.transcription = transcription
        self.speakers = speakers
        self.transcription_items = transcription_items

    def text_at_marker(self, marker_index: int) -> str:
        for text in transcription_items:
            pass
