from dataclasses import dataclass

@dataclass(frozen=True)  # immutable
class Lesson:
    class_name: str
    subject: str
    teacher_name: str

    def __str__(self) -> str:
        return f"{self.class_name} — {self.subject} ({self.teacher_name})"