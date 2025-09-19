from pydantic import BaseModel, Field
from typing import List, Optional


class Course(BaseModel):
    name: str
    id: str
    credit: int
    prerequisite: List = Field(default_factory=list)
    before: List = Field(default_factory=list)
    semester: Optional[int] = None
    optional_group: Optional[str] = ""

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Course):
            return self.id == other.id
        return False

    def __str__(self):
        return f"{self.name} (ID: {self.id}, Credit: {self.credit}, Prerequisite: {', '.join(self.prerequisite) if self.prerequisite else 'None'})"


class Semester(BaseModel):
    name: str
    courses: List[Course] = Field(default_factory=list)
    total_credit: int = 0


class Student(BaseModel):
    name: str
    student_id: str
    program: str
    learned: List[Course] = Field(default_factory=list)
    semester: int = 2

    def __str__(self):
        return f"{self.name} (ID: {self.student_id}, Program: {self.program}, Semester: {self.semester}, Learned Courses: {len(self.learned)})"


class State(BaseModel):
    student: Student
    semester: Semester
    total_credit: int
