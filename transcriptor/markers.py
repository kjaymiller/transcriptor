from transcriptor.speakers import Speaker
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class Marker:
    speaker: Speaker= None
    start_time: float=0.0
    end_time: float=0.0

def gen_markers(segments: List):
    for segment in segments:
        yield Marker(**segment)

