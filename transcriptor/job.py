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
            speakers: typing.List,
            ):

        self.name = name
        self.base_text = base_text
        self.markers = markers
        self.transcription = transcription
        self.speakers = speakers

    def text_at_marker(self, marker:Marker) -> str:
        pass
