from .alternatives import Alternative
from .speakers import Speaker
from datetime import timedelta
from dataclasses import dataclass
import typing

@dataclass
class Segment:
    alternatives: typing.List[Alternative]
    start_time: typing.Optional[float] = 0.0 
    end_time: typing.Optional[float] = 0.0
    speaker: typing.Optional[Speaker] = None


def gen_segments(segments):
    for segments in segments:
        yield Segment(**kwargs)
