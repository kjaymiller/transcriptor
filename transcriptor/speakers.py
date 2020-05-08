from dataclasses import dataclass

@dataclass
class Speaker:
    speaker_index: int
    base_name: str=None
    label: str=None
