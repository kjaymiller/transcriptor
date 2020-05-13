from dataclasses import dataclass
import typing

@dataclass
class Alternative:
    content: str
    confidence: float
    _type: str
    start_time: float = None
    end_time: float = None
