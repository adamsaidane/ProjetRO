from typing import Set
from dataclasses import dataclass

@dataclass
class Teacher:
    name: str
    subjects: Set[str]

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Teacher name cannot be empty")
        if not self.subjects:
            raise ValueError(f"Teacher {self.name} must teach at least one subject")