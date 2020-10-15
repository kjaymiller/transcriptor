from datetime import timedelta
from dataclasses import dataclass
import typing

@dataclass
class Alternative:
    content: str
    confidence: float
    _type: str
    start_time: typing.Optional[float] = 0.0 
    end_time: typing.Optional[float] = 0.0
    # regional times for loading from text
    tag: typing.Optional[str] = None
    regional_start_time: typing.Optional[float]=None 
    regional_end_time: typing.Optional[float]=None

def gen_alternatives(alternatives):
    for alternative in alternatives:
        yield Alternative(**kwargs)

