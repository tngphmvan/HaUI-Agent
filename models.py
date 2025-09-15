class Student:
    def __init__(self, name, student_id, program, learned: list[tuple | dict]=[], ):
        self.name = name
        self.student_id = student_id
        self.program = program
        self.learned = learned

class Course:
    def __init__(self, name, credit, prerequisite: list[str] = [], before: list[str] = []):
        self.name = name
        self.credit = credit
        self.prerequisite = prerequisite
        self.before = before

class Semester:
    def __init__(self, name, courses: list[Course] = []):
        self.name = name
        self.courses = courses
        self.total_credit = sum(course.credit for course in courses)

class State:
    def __init__(self, student: Student, semester: Semester ):
        self.student = student
        self.semester = semester
        self.total_credit = semester.total_credit

