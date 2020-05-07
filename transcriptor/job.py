from transcriptor.speakers import Speaker
from transcriptor.markers import Marker

import typing

class Job:
    def __init__(
            self,
            name: str,
            markers: typing.List=[],
            _transcript: text = '',
            speakers: typing.List=[],
            ):

        self.name = name
        self.markers = markers
        self._transcript = _transcript
        self.speakers = speakers

