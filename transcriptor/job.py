from dataclasses import dataclass
from transcriptor.speakers import Speaker
from transcriptor.markers import Marker

import typing

@dataclass
class Job:
    base_text: str
    name: str
    markers: typing.List
    _transcript: typing.Dict
    speakers: typing.List
