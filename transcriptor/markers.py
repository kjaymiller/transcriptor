from dataclasses import dataclass
import typing

@dataclass
def Marker:
    speaker: typing.type[Speaker]
    timestamp_start: float
    text: str
