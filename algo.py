from models import CoursePlanResponse, Student, Course, Semester, State, CoursePlanRequest
from typing import Tuple, List
import json
import random
import sys
import io
import logging
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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


# def greedy_adding_algorithm(state: State, proposed_courses: list[Course], available_courses: list[Course], max_credits: int) -> Tuple[List[Course], int]:
#     """Algorithm to greedily add courses based on certain conditions.

#     Args:
#         state (State): Current state of the student
#         proposed_courses (list[Course]): Proposed courses to consider first
#         available_courses (list[Course]): Available courses to choose from
#         max_credits (int): Maximum credits allowed

#     Returns:
#         Tuple[List[Course], int]: List of added courses and total credits
#     """

#     # Set semester of proposed courses to 0 if different from student's current semester
#     for course in proposed_courses:
#         if course.semester != state.student.semester:
#             course.semester = 0
#     for course in proposed_courses:
#         add_course(state, course)
#     # Sort available courses by semester to prioritize adding courses from lower semesters first
#     tong = 0
#     for course in sorted(available_courses, key=lambda c: c.semester):
#         if course.name.find("Tiếng Trung") != -1 or course.name.find("Tiếng Hàn") != -1 or course.name.find("Tiếng Nhật") != -1:
#             continue
#         if course in state.student.learned:
#             print(f"Skipping {course.name} as it is already learned.")
#             continue
#             # Just one course from each optional group in a semester
#         if course.optional_group:
#             if any(c.optional_group == course.optional_group for c in state.semester.courses):
#                 print(
#                     f"Skipping {course.name} as it conflicts with another course in the same optional group.")
#                 continue

#         tong += course.credit
#         add_course(state, course)
#         logger.debug(
#             f"Added course: {course.id} with {course.credit} credits.")
#         logger.debug(f"Total credits now: {tong}.")
#         if tong >= max_credits:
#             break
#     return (state.semester.courses, state.semester.total_credit)

# def greedy_adding_algorithm(state: State, proposed_courses: list[Course], available_courses: list[Course], max_credits: int) -> Tuple[List[Course], int]:
#     # Reset trước khi bắt đầu
#     state.semester.courses = []
#     state.semester.total_credit = 0
#     state.total_credit = 0

#     # Add proposed courses trước
#     for course in proposed_courses:
#         logger.debug(f"Adding proposed course: {course.id}")
#         add_course(state, course)

#     for course in sorted(available_courses, key=lambda c: c.semester):
#         if course.name.find("Tiếng Trung") != -1 or course.name.find("Tiếng Hàn") != -1 or course.name.find("Tiếng Nhật") != -1:
#             continue
#         if course in state.student.learned:
#             continue
#         if course.optional_group and any(c.optional_group == course.optional_group for c in state.semester.courses):
#             continue

#         if state.semester.total_credit + course.credit > max_credits:
#             break

#         add_course(state, course)
#         logger.debug(
#             f"Added course: {course.id} with {course.credit} credits.")
#         logger.debug(f"Total credits now: {state.semester.total_credit}.")

#     return (state.semester.courses, state.semester.total_credit)


def greedy_adding_algorithm(
    state: State,
    proposed_courses: list[Course],
    available_courses: list[Course],
    max_credits: int
) -> Tuple[List[Course], int]:
    # Reset trước khi bắt đầu
    state.semester.courses = []
    state.semester.total_credit = 0
    state.total_credit = 0

    # B1: Add các môn đề xuất (proposed) trước
    for course in proposed_courses:
        if course not in state.student.learned and course not in state.semester.courses:
            if state.semester.total_credit + course.credit <= max_credits:
                add_course(state, course)
            #     logger.debug(
            #         f"Added proposed course: {course.id} ({course.credit} credits).")
            # else:
                # logger.debug(
                #     f"Skip proposed course {course.id}, would exceed max credits.")

    # B2: Sau đó add các môn khả dụng (available) theo thứ tự kỳ học và thứ tự tín chỉ tăng dần
    for course in sorted(available_courses, key=lambda c: (c.semester, c.credit)):
        if "Tiếng Trung" in course.name or "Tiếng Hàn" in course.name or "Tiếng Nhật" in course.name:
            continue
        if course in state.student.learned or course in state.semester.courses:
            continue
        if course.optional_group and (any(c.optional_group == course.optional_group for c in state.semester.courses) or
                                      any(c.optional_group == course.optional_group for c in state.student.learned)):
            continue
        if state.semester.total_credit + course.credit > max_credits:
            break
        add_course(state, course)

        # logger.debug(
        #     f"Added available course: {course.id} ({course.credit} credits).")

    return (state.semester.courses, state.semester.total_credit)


def find_all_subsequences(proposed_courses: list[Course], available_courses: list[Course], max_credits: int):
    """Find all subsequences of courses with total credits equal to k and return the lexicographically smallest one, sort by (semester, credit)."""

    result = []  # Chứa các subsequence hợp lệ
    proposed_credits = sum(course.credit for course in proposed_courses)
    remaining_credits = max_credits - proposed_credits

    # Nếu proposed_courses đã vượt quá max_credits
    if remaining_credits < 0:
        return None

    # Nếu proposed_courses đúng bằng max_credits
    if remaining_credits == 0:
        return proposed_courses

    n = len(available_courses)

    def backtrack(index, current_sum, current_subsequence):
        if current_sum == remaining_credits:
            # Kết hợp proposed_courses + current_subsequence
            full_sequence = proposed_courses + current_subsequence[:]
            result.append(full_sequence)
            return

        if index >= n or current_sum > remaining_credits:
            return

        # Không lấy phần tử hiện tại
        backtrack(index + 1, current_sum, current_subsequence)

        # Lấy phần tử hiện tại
        current_subsequence.append(available_courses[index])
        backtrack(index + 1, current_sum +
                  available_courses[index].credit, current_subsequence)
        current_subsequence.pop()

    backtrack(0, 0, [])

    # Trả về dãy con có thứ tự từ điển nhỏ nhất
    if not result:
        return proposed_courses if proposed_credits <= max_credits else None

    return (min(result, key=lambda subseq: [(course.semester, course.credit) for course in subseq]),
            sum(course.credit for course in min(result, key=lambda subseq: [(course.semester, course.credit) for course in subseq])))


def course_mapping(course_id: str, courses_list: list[Course]) -> Course:
    for course in courses_list:
        if course.id == course_id:
            return course
    return None


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
    for nhom_tu_chon in program_framework[ky_hoc]['hoc_phan_tu_chon']:
        if "TcNN1" in nhom_tu_chon.keys():
            del nhom_tu_chon['TcNN1']
        if "TcNN2" in nhom_tu_chon.keys():
            del nhom_tu_chon['TcNN2']
        if "TcNN3" in nhom_tu_chon.keys():
            del nhom_tu_chon['TcNN3']
        if "Tc Ôn tập NN" in nhom_tu_chon.keys():
            del nhom_tu_chon['Tc Ôn tập NN']
        if "TcGDTC" in nhom_tu_chon.keys():
            del nhom_tu_chon['TcGDTC']
        if nhom_tu_chon == {}:
            program_framework[ky_hoc]['hoc_phan_tu_chon'].remove(nhom_tu_chon)

for ky_hoc in program_framework.keys():
    for course in program_framework[ky_hoc]['hoc_phan_bat_buoc']:
        course = Course(
            name=course['ten_hp'],
            credit=int(float(course['so_tc'])),
            prerequisite=course['prerequisite'],
            before=course['before'],
            id=course['ma_hp'],
            semester=int(course['hoc_ky']),
            optional_group=""
        )
        semesters[course.semester-1].courses.append(course)
        # print(
        #     f"Added course: {course.name} to semester {course.semester}")
        # print("course", course.name)
    for course_optional in program_framework[ky_hoc]['hoc_phan_tu_chon']:
        # Handle dict items (e.g., TcCNTT5) if needed, or skip
        # print("course_tup", course_tup)
        optional_group = list(course_optional.keys())[0]
        for sub_course in course_optional[optional_group]:
            course = Course(
                name=sub_course['ten_hp'],
                credit=int(float(sub_course['so_tc'])),
                prerequisite=sub_course['prerequisite'],
                before=sub_course['before'],
                id=sub_course['ma_hp'],
                # Giả sử tên kỳ học có định dạng 'ky_X'
                semester=int(sub_course['hoc_ky']),
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

total_course = [
    course for semester in semesters for course in semester.courses]
logger.debug(f"Total courses in the program: {len(total_course)}")

# for course in total_course:
#     print(
#         f"Kỳ: {course.semester}, {course.name}, {course.credit}, {course.optional_group}")
# print(f"Total courses in the program: {len(total_course)}")


proposed_courses = random.sample(semesters[7].courses, k=min(0, 3))

learned_courses = [
    course for course in semesters[0].courses + semesters[1].courses if not course.optional_group
]


TcCNTT1 = [
    course for course in optional_groups if course.optional_group == "TcCNTT1"]
TcCNTT2 = [
    course for course in optional_groups if course.optional_group == "TcCNTT2"]
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
learned_courses.extend(sorted(TcNN4, key=lambda c: c.semester)[0:2])

# learned_courses.remove(course_mapping("LP6010", total_course))
# learned_courses.remove(course_mapping("IT6015", total_course))
# learned_courses.remove(course_mapping("FL6086", total_course))

# for course in learned_courses:
#     print(f"Kỳ: {course.semester}, {course.name}, {course.credit}")

student = Student(name="Nguyen Van A", student_id="123456",
                  program="CNTT", semester=3, learned=learned_courses)
initial_state = State(
    student=student, semester=Semester(name=3, courses=[], total_credit=0), total_credit=0)
print(f"Student {student.name} has learned {len(student.learned)} courses.")
available_courses = [
    course for course in total_course if course not in student.learned and course.before == [] and course.prerequisite == []]

print(f"Có {len(available_courses)} khóa học có sẵn để thêm.")
print(f"There are {len(available_courses)} courses available to add.")
# for course in available_courses:
#     print(
#         f"Kỳ: {course.semester}, {course.name}, {course.credit}, {course.optional_group}")

designed_credits = [semester.total_credit for semester in semesters]
# print(designed_credits)
# courses, total_credits = greedy_adding_algorithm(
#     initial_state, proposed_courses, available_courses, max_credits=15)
# for course in courses:
#     print(
#         f"Semester: {course.semester}, {course.name}, {course.credit}, {course.optional_group}")

# for course in available_courses:
#     print(
#         f"Kỳ: {course.semester}, {course.name}, {course.credit}, {course.optional_group}")
# for course in semesters[0].courses:
#     print(
#         f"Kỳ: {course.semester}, {course.name}, {course.credit}, {course.optional_group}")


def check_course_validity(course_ids: List[str]) -> str:
    """Check if the proposed courses are valid for the student."""
    proposed_courses = [course_mapping(course_id, total_course)
                        for course_id in course_ids]
    for course in proposed_courses:
        if course not in available_courses:
            return f"Course {course.id} is not available."
    return "All proposed courses are valid."


print(course_mapping("IT6047", total_course))


def course_planning(request: CoursePlanRequest) -> CoursePlanResponse | str:
    """Plan courses for the student based on their current state and proposed courses."""
    # state = request.state if request.state else Student(
    #     name=student.name,
    #     student_id=student.student_id,
    #     program=student.program,
    #     learned=student.learned,
    #     semester=student.semester
    # )
    # proposed_courses = request.proposed_courses if request.proposed_courses else proposed_courses
    proposed_courses = [course_mapping(course_id, total_course)
                        for course_id in request.proposed_courses]
    available_courses = []
    if request.brute_force:
        for course in total_course:
            if course not in initial_state.student.learned:
                prerequisites_met = all(
                    pre['ModulesCode'] in [c.id for c in initial_state.student.learned] for pre in course.prerequisite)
                if prerequisites_met:
                    available_courses.append(course)
    else:
        for course in total_course:
            if course not in initial_state.student.learned:
                # Kiểm tra prerequisite
                prerequisites_met = all(
                    pre['ModulesCode'] in [c.id for c in initial_state.student.learned] for pre in course.prerequisite)
                # Kiểm tra before
                before_met = any(
                    bef['ModulesCode'] in [c.id for c in initial_state.student.learned] for bef in course.before)
                if prerequisites_met and (not before_met and course.semester <= initial_state.student.semester):
                    available_courses.append(course)
    # print(
    #     f"Available courses: {[course.id for course in available_courses]}")
    print(f"Available courses after filtering: {len(available_courses)}")

    print(
        f"Planning courses for student {initial_state.student.name} with {len(initial_state.student.learned)} learned courses and {len(proposed_courses)} proposed courses.")
    course, total_credits = None, 0
    if not request.brute_force:
        courses, total_credits = greedy_adding_algorithm(state=initial_state,
                                                         proposed_courses=proposed_courses,
                                                         available_courses=available_courses,
                                                         max_credits=request.max_credits)
    else:
        courses, total_credits = find_all_subsequences(
            proposed_courses, available_courses, request.max_credits)
    print(
        f"New state has {len(courses)} courses with total credit {total_credits}.")
    return CoursePlanResponse(planned_courses=courses, total_credits=total_credits)


print(course_planning(CoursePlanRequest(
    proposed_courses=["IT6120"], max_credits=27, brute_force=True)))

# print(find_all_subsequences(proposed_courses, available_courses, 15))
# print(find_all_subsequences(
#     [course_mapping("IT6120", total_course)], available_courses, 28))
