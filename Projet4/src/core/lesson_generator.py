from typing import List, Set
from ..models.teacher import Teacher
from ..models.school_class import SchoolClass
from ..models.lesson import Lesson

def generate_lessons(
    teachers: List[Teacher],
    classes: List[SchoolClass]
) -> List[Lesson]:
    lessons = []
    for cls in classes:
        for subject in cls.subjects:
            for teacher in teachers:
                if subject in teacher.subjects:
                    lessons.append(Lesson(cls.name, subject, teacher.name))
    return lessons