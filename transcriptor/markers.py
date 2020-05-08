from transcriptor.speakers import Speaker
from dataclasses import dataclass

@dataclass
class Marker:
    speaker: Speaker= None
    start_time: float=0.0
    end_time: float=0.0
