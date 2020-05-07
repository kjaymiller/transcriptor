from dataclasses import dataclass
import typing

@dataclass
def Marker:
    speaker: typing.type[Speaker]: None
    start_time: float=0.0
    end_time: float=0.0
