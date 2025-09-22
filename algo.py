from models import Student, Course, Semester, State
from typing import Tuple, List
import json
import random
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def course_checking(state: State, course: Course, max_credits: int) -> Tuple[bool, str]:
    """Check if a course can be added to the current state based on several conditions.

    Args:
        state (State): state of the student
        course (Course): course to be checked
        max_credits (int): maximum credits allowed

    Returns:
        Tuple[bool, str]: _description_
    """
    # Check if the course has already been learned
    if course.id in [c[0] if isinstance(c, tuple) else c.id for c in state.student.learned]:
        return (False, f"Course {course.name} with ID {course.id} already learned")

    # Check prerequisite courses
    for before in course.before:
        if before not in [c[0] if isinstance(c, tuple) else c.id for c in state.student.learned]:
            return (False, f"Course {course.name} with ID {course.id} has not completed prerequisite course {before}")

    # Check prerequisite courses
    for prereq in course.prerequisite:
        if prereq not in [c[0] if isinstance(c, tuple) else c.id for c in state.student.learned]:
            return (False, f"Course {course.name} with ID {course.id} has not completed prerequisite course {prereq}")

    # Check if adding the course would exceed the maximum credit limit
    if state.total_credit + course.credit > max_credits:
        return (False, f"Total credits would exceed the limit of {max_credits}")

    # If all conditions are satisfied, return True
    return (True, "All conditions are satisfied")


def add_course(state: State, course: Course):
    """Add a course to the current state.

    Args:
        state (State): _description_
        course (Course): _description_
    """
    state.student.learned.append(course)
    state.total_credit += course.credit
    state.semester.courses.append(course)
    state.semester.total_credit += course.credit


def greedy_adding_algorithm(state: State, proposed_courses: list[Course], available_courses: list[Course], max_credits: int) -> Tuple[List[Course], int]:
    """Algorithm to greedily add courses based on certain conditions.

    Args:
        state (State): Current state of the student
        proposed_courses (list[Course]): Proposed courses to consider first
        available_courses (list[Course]): Available courses to choose from
        max_credits (int): Maximum credits allowed

    Returns:
        Tuple[List[Course], int]: List of added courses and total credits
    """

    # Set semester of proposed courses to 0 if different from student's current semester
    for course in proposed_courses:
        if course.semester != state.student.semester:
            course.semester = 0

    # Sort available courses by semester to prioritize adding courses from lower semesters first
    tong = 0
    for course in sorted(available_courses, key=lambda c: c.semester):
        can_add, message = course_checking(state, course, max_credits)
        # Just one course from each optional group in a semester
        if course.optional_group:
            if any(c.optional_group == course.optional_group for c in state.semester.courses):
                can_add = False
                message = f"Đã có khóa học từ nhóm tự chọn {course.optional_group} trong học kỳ này."
        if can_add:
            add_course(state, course)
            tong += course.credit
            print(
                f"Currently add: {course.name} with {course.credit} credits. {message}")
        if tong >= max_credits:
            break
    return (state.semester.courses, state.total_credit)


# if __name__ == "__main__":
semesters = [
    Semester(name=1),
    Semester(name=2),
    Semester(name=3),
    Semester(name=4),
    Semester(name=5),
    Semester(name=6),
    Semester(name=7),
    Semester(name=8)
]
program_framework = json.load(
    open("khung_ctrinh_cntt_14_9_processed.json", 'r', encoding='utf-8'))
# print(program_framework)
for ky_hoc in program_framework.keys():
    for course_tup in program_framework[ky_hoc]:
        if isinstance(course_tup, (list, tuple)) and len(course_tup) == 5:
            course_id, course_name, credit, prerequisite, before = course_tup
            course = Course(
                name=course_name,
                credit=int(float(credit)),
                prerequisite=prerequisite,
                before=before,
                id=course_id,
                # Giả sử tên kỳ học có định dạng 'ky_X'
                semester=int(ky_hoc.split('_')[1]),
                optional_group=""  # Hoặc gán giá trị phù hợp nếu có
            )

            semesters[course.semester-1].courses.append(course)
            # print(
            #     f"Added course: {course.name} to semester {course.semester}")
            # print("course", course.name)
        elif isinstance(course_tup, dict):
            # Handle dict items (e.g., TcCNTT5) if needed, or skip
            # print("course_tup", course_tup)
            optional_group = list(course_tup.keys())[0]
            # print("optional_group", optional_group[0])
            for sub_course_tup in course_tup.values():
                for course in sub_course_tup:
                    course_id, course_name, credit, prerequisite, before = course
                    course = Course(
                        name=course_name,
                        credit=int(float(credit)),
                        prerequisite=prerequisite,
                        before=before,
                        id=course_id,
                        # Giả sử tên kỳ học có định dạng 'ky_X'
                        semester=int(ky_hoc.split('_')[1]),
                        # Hoặc gán giá trị phù hợp nếu có
                        optional_group=optional_group
                    )
                    # print(int(ky_hoc.split('_')[1]))
                    # print("holaa", course.optional_group)
                    # print(
                    #     f"Added course: {course.name} to semester {course.semester} in optional group {course.optional_group}")
                    semesters[course.semester - 1].courses.append(course)

    # Tính tổng tín chỉ: các môn bắt buộc cộng hết, mỗi nhóm tự chọn chỉ lấy 1 môn (tín chỉ cao nhất)
    semester_courses = semesters[int(ky_hoc.split('_')[1]) - 1].courses
    total_credit = 0
    # Nhóm các môn tự chọn theo optional_group
    optional_group_seen = set()
    for course in semester_courses:
        if course.optional_group:
            if course.optional_group not in optional_group_seen:
                # Lấy tất cả môn cùng nhóm trong kỳ này
                same_group_courses = [
                    c for c in semester_courses if c.optional_group == course.optional_group]
                # Lấy môn có tín chỉ cao nhất
                max_course = max(same_group_courses,
                                 key=lambda c: c.credit)
                total_credit += max_course.credit
                optional_group_seen.add(course.optional_group)
        else:
            total_credit += course.credit
    semesters[int(ky_hoc.split('_')[1]) - 1].total_credit = total_credit

optional_groups = list(set(
    course for semester in semesters for course in semester.courses if course.optional_group))

print("Optional groups found:", len(optional_groups))
student = Student(name="Nguyen Van A", student_id="123456",
                  program="CNTT", semester=3, learned=[])
initial_state = State(
    student=student, semester=Semester(name=3, courses=[], total_credit=0), total_credit=0)

proposed_courses = random.sample(semesters[7].courses, k=min(0, 3))

learned_courses = [
    course for course in semesters[0].courses + semesters[1].courses if not course.optional_group
]

TcGDTC = [
    course for course in optional_groups if course.optional_group == "TcGDTC"]
TcCNTT1 = [
    course for course in optional_groups if course.optional_group == "TcCNTT1"]
TcCNTT2 = [
    course for course in optional_groups if course.optional_group == "TcCNTT2"]
TcNN = [
    course for course in optional_groups if course.optional_group == "Tc Ôn tập NN"]
TcCNTT3 = [
    course for course in optional_groups if course.optional_group == "TcCNTT3"]
TcCNTT4 = [
    course for course in optional_groups if course.optional_group == "TcCNTT4"]
TcCNTT5 = [
    course for course in optional_groups if course.optional_group == "TcCNTT5"]
TcCNTT6 = [
    course for course in optional_groups if course.optional_group == "TcCNTT6"]
TcNN4 = [
    course for course in optional_groups if course.optional_group == "TcNN4"]

learned_courses.append(TcCNTT1[0])
learned_courses.append(TcCNTT2[0])
learned_courses.extend(sorted(TcGDTC, key=lambda c: c.semester)[0:2])
learned_courses.extend(sorted(TcNN4, key=lambda c: c.semester)[0:2])

# for course in learned_courses:
#     print(f"Kỳ: {course.semester}, {course.name}, {course.credit}")

student.learned = learned_courses
print(f"Student {student.name} has learned {len(student.learned)} courses.")

available_courses = [
    course for semester in semesters[2:9] for course in semester.courses
]
print(f"There are {len(available_courses)} courses available to add.")
# for course in available_courses:
#     print(
#         f"Kỳ: {course.semester}, {course.name}, {course.credit}, {course.optional_group}")

designed_credits = [semester.total_credit for semester in semesters]
print(designed_credits)
courses, total_credits = greedy_adding_algorithm(
    initial_state, proposed_courses, available_courses, max_credits=33)
for course in courses:
    print(
        f"Semester: {course.semester}, {course.name}, {course.credit}, {course.optional_group}")

# for course in semesters[0].courses:
#     print(
#         f"Kỳ: {course.semester}, {course.name}, {course.credit}, {course.optional_group}")
