from models import Student, Course, Semester, State
from typing import Tuple
import json
import random


def course_checking(state: State, course: Course, max_credits) -> Tuple[bool, str]:
    """
    Thêm một khóa học vào trạng thái hiện tại nếu thỏa mãn các điều kiện.
    Điều kiện:
    1. Khóa học chưa được học.
    2. Đã hoàn thành tất cả các khóa học tiên quyết.
    3. Tổng tín chỉ không vượt quá max_credits.
    """
    # Kiểm tra nếu khóa học đã được học
    if course.id in [c[0] if isinstance(c, tuple) else c.id for c in state.student.learned]:
        return (False, f"Khóa học {course.name} với mã {course.id} đã được học")

    # Kiểm tra các khóa học trước
    for before in course.before:
        if before not in [c[0] if isinstance(c, tuple) else c.id for c in state.student.learned]:
            return (False, f"Khóa học {course.name} với mã {course.id} chưa hoàn thành khóa học trước {before}")

    # Kiểm tra các khóa học tiên quyết
    for prereq in course.prerequisite:
        if prereq not in [c[0] if isinstance(c, tuple) else c.id for c in state.student.learned]:
            return (False, f"Khóa học {course.name} với mã {course.id} chưa hoàn thành khóa học tiên quyết {prereq}")

    # Kiểm tra tổng tín chỉ
    if state.total_credit + course.credit > max_credits:
        return (False, f"Tổng tín chỉ đã vượt quá giới hạn {max_credits}")

    # Nếu tất cả điều kiện đều thỏa mãn, trả về True
    return (True, "Tất cả các điều kiện đều thỏa mãn")


def add_course(state: State, course: Course):
    """
    Thêm một khóa học vào trạng thái hiện tại.
    Cập nhật danh sách các khóa học đã học và tổng tín chỉ.
    """
    state.student.learned.append((course.name, course.credit))
    state.total_credit += course.credit
    state.semester.courses.append(course)
    state.semester.total_credit += course.credit


def greedy_adding_algorithm(state: State, proposed_courses: list[Course], available_courses: list[Course], max_credits: int) -> State:
    """
    Thuật toán thêm khóa học dựa trên cây.
    Duyệt qua danh sách các khóa học có sẵn và thêm vào trạng thái hiện tại nếu thỏa mãn điều kiện.
    """

    # Đặt các khóa học đề xuất có kỳ bằng 0, nếu semester khác student semester
    for course in proposed_courses:
        if course.semester != state.student.semester:
            course.semester = 0

    # Sắp xếp các khóa học có sẵn theo học kỳ (semester) để ưu tiên thêm các khóa học ở học kỳ thấp hơn trước
    tong = 0
    for course in sorted(available_courses, key=lambda c: c.semester):
        can_add, message = course_checking(state, course, max_credits)
        if can_add:
            add_course(state, course)
            tong += course.credit
            print(
                f"Đã thêm khóa học: {course.name} ({course.credit} tín chỉ). {message}")
        if tong >= max_credits:
            break
    return state


if __name__ == "__main__":
    semesters = [
        Semester("Học kỳ 1"),
        Semester("Học kỳ 2"),
        Semester("Học kỳ 3"),
        Semester("Học kỳ 4"),
        Semester("Học kỳ 5"),
        Semester("Học kỳ 6"),
        Semester("Học kỳ 7"),
        Semester("Học kỳ 8"),
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

        semesters[int(ky_hoc.split('_')[1]) - 1].total_credit = sum(
            course.credit for course in semesters[int(ky_hoc.split('_')[1]) - 1].courses)

    optional_groups = list(set(
        course for semester in semesters for course in semester.courses if course.optional_group))

    print("Optional groups found:", len(optional_groups))
    student = Student(name="Nguyen Van A", student_id="123456", program="CNTT")
    initial_state = State(student=student, semester=semesters[1])

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
    learned_courses.extend(TcGDTC[0:5])
    learned_courses.append(TcNN4[0])

    for course in learned_courses:
        print(f"Kỳ: {course.semester}, {course.name}, {course.credit}")

    student.learned = learned_courses
    print(f"Student {student.name} đã học {len(student.learned)} khóa học.")
