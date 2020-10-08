from datetime import timedelta
from dataclasses import dataclass
import typing

@dataclass
class Alternative:
    content: str
    confidence: float
    _type: str
    tag: typing.Optional[str] = None
    start_time: typing.Optional[float]
    end_time: typing.Opriontal[float]
    # regional times for loading from text
    regional_start_time: typing.Optional[float]=None 
    regional_end_time: typing.Optional[float]=None

def gen_alternatives(alternatives):
    for alternative in alternatives:
        yield Alternative(**kwargs)

