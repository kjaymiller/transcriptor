from dataclasses import dataclass
from transcriptor.speakers import Speaker
from transcriptor.markers import Marker

import typing

@dataclass
class Job:
    self,
    base_text: str,
    name: str,
    markers: typing.List[]=[],
    _transcript: dict = {},
    speakers: typing.List=[],
