class Course:
    def __init__(self, name, credit, optional_group, prerequisite: list[str] = [], before: list[str] = [], id: str = "", semester: int = None, ):
        self.name = name
        self.id = id
        self.credit = credit
        self.prerequisite = prerequisite
        self.before = before
        self.semester = semester
        self.optional_group = optional_group

    def __str__(self):
        return f"Course: {self.name}, ID: {self.id}, Credit: {self.credit}, Semester: {self.semester}, Optional Group: {self.optional_group}, Prerequisite: {self.prerequisite}, Before: {self.before}"

    def __eq__(self, value):
        # print("Checking equality between", self, "and", value)
        if isinstance(value, Course):
            return self.id == value.id
        elif isinstance(value, str):
            return self.id == value
        return False

    def __hash__(self):
        return hash(self.id)


class Semester:
    def __init__(self, name):
        self.name = name
        self.courses = []
        self.total_credit = 0

    def __str__(self):
        return f"Semester: {self.name}, Total Credits: {self.total_credit}"


class Student:
    def __init__(self, name, student_id, program, learned: list[Course] = [], semester: int = 2):
        self.name = name
        self.student_id = student_id
        self.program = program
        self.learned = learned
        self.semester = semester


class State:
    def __init__(self, student: Student, semester: Semester):
        self.student = student
        self.semester = semester
        self.total_credit = semester.total_credit
