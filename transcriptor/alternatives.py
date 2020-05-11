from dataclasses import dataclass
import typing

@dataclass
class Alternative:
    content: str
    confidence: float
    start_time: float
    end_time: float
