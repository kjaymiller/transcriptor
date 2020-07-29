from dataclasses import dataclass
from typing import Optional

@dataclass
class Alternative:
    content: str
    confidence: float
    _type: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
