from typing import Set
from dataclasses import dataclass

@dataclass
class SchoolClass:
    name: str
    subjects: Set[str]

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Class name cannot be empty")
        if not self.subjects:
            raise ValueError(f"Class {self.name} must have at least one subject")