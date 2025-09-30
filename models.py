from pydantic import BaseModel, Field
from typing import List, Optional


class Course(BaseModel):
    name: str
    id: str
    credit: int
    prerequisite: List[dict] = Field(
        default_factory=list, description="Các khóa học tiên quyết, cần hoàn thành trước khi học khóa này")
    before: List[dict] = Field(
        default_factory=list, description="Các khóa học cần hoàn thành trước khi học khóa này")
    semester: Optional[int] = Field(description="Học kỳ của khóa học")
    optional_group: Optional[str] = Field(
        description="Nhóm tự chọn của khóa học")

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Course):
            return self.id == other.id
        return False

    def __str__(self):
        return f"{self.name} (ID: {self.id}, Credit: {self.credit}, Prerequisite: {', '.join(self.prerequisite) if self.prerequisite else 'None'}, Before: {self.before})"


class Semester(BaseModel):
    name: int = Field(description="Thứ tự của Học kỳ")
    courses: List[Course] = Field(
        default_factory=list, description="Danh sách các khóa học trong học kỳ")
    total_credit: int = Field(0, description="Tổng tín chỉ của học kỳ")


class Student(BaseModel):
    name: str = Field(description="Tên sinh viên")
    student_id: str = Field(description="Mã số sinh viên")
    program: str = Field(
        description="Chương trình đào tạo (ngành học, ví dụ: CNTT, Kinh tế, ...)")
    learned: List[Course] = Field(
        default_factory=list, description="Danh sách các môn đã hoàn thành")
    semester: int = Field(description="Học kỳ hiện tại của sinh viên")

    def __str__(self):
        return f"{self.name} (ID: {self.student_id}, Program: {self.program}, Semester: {self.semester}, Learned Courses: {len(self.learned)})"


class State(BaseModel):
    student: Student = Field(description="Thông tin sinh viên")
    semester: Semester = Field(description="Thông tin học kỳ hiện tại")
    total_credit: int = Field(
        0, description="Tổng tín chỉ đã đăng ký trong học kỳ hiện tại")


class CoursePlanRequest(BaseModel):
    proposed_courses: List[str] = Field(
        default_factory=list, description="Danh sách mã các khóa học đề xuất để lên kế hoạch")
    max_credits: int = Field(
        25, description="Tổng tín chỉ mà sinh viên muốn đăng ký", ge=11, le=27)
    brute_force: Optional[bool] = Field(
        False, description="Nếu True, sử dụng phương pháp tìm kiếm tất cả các dãy con để chọn dãy có tổng tín chỉ lớn nhất mà không vượt quá max_credits. Nếu False, sử dụng thuật toán tham lam.")
    # student_info: Optional[Student] = Field(
    #     None, description="Thông tin sinh viên, nếu không có sẽ dùng thông tin mặc định trong trạng thái")
    # available_courses: Optional[List[Course]] = Field(
    #     None, description="Danh sách các khóa học có sẵn, nếu không có sẽ dùng danh sách mặc định trong trạng thái")
    # state: Optional[State] = Field(
    #     None, description="Trạng thái hiện tại của sinh viên, nếu không có sẽ dùng trạng thái mặc định")


class CoursePlanResponse(BaseModel):
    planned_courses: List[Course] = Field(
        default_factory=list, description="Danh sách các khóa học được lên kế hoạch")
    total_credits: int = Field(
        0, description="Tổng tín chỉ của các khóa học được lên kế hoạch")
