from dataclasses import dataclass

@dataclass
class Speaker:
    base_name: str=None # default name
    name: str=None # User given name

    @property
    def label(self):
        return self.name or self.base_name
