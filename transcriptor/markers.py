from transcriptor.speakers import Speaker
from dataclasses import dataclass

import typing

@dataclass
class Marker:
    """Content should only exist when there are no segments"""
    speaker: typing.Optional[Speaker]= None
    start_time: float=0.0
    end_time: float=0.0
    content: typing.Optional[str] = None
