from models import Student, Course, Semester, State
def course_checking(state: State, course: Course, max_credits) -> bool:
    """
    Thêm một khóa học vào trạng thái hiện tại nếu thỏa mãn các điều kiện.
    Điều kiện:
    1. Khóa học chưa được học.
    2. Đã hoàn thành tất cả các khóa học tiên quyết.
    3. Tổng tín chỉ không vượt quá max_credits.
    """
    # Kiểm tra nếu khóa học đã được học
    if course.name in [c[0] if isinstance(c, tuple) else c['name'] for c in state.student.learned]:
        return False

    # Kiểm tra các khóa học tiên quyết
    for prereq in course.prerequisite:
        if prereq not in [c[0] if isinstance(c, tuple) else c['name'] for c in state.student.learned]:
            return False

    # Kiểm tra tổng tín chỉ
    if state.total_credit + course.credit > max_credits:
        return False

    # Nếu tất cả điều kiện đều thỏa mãn, trả về True
    return True

def add_course(state: State, course: Course):
    """
    Thêm một khóa học vào trạng thái hiện tại.
    Cập nhật danh sách các khóa học đã học và tổng tín chỉ.
    """
    state.student.learned.append((course.name, course.credit))
    state.total_credit += course.credit
    state.semester.courses.append(course)
    state.semester.total_credit += course.credit


