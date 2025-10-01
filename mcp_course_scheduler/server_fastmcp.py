"""
FastMCP Server for Optimized Course Scheduling Suggestion System
Compatible with 'mcp dev' command
"""

from mcp.server.fastmcp import FastMCP
from course_scheduler import CourseScheduler, CourseSuggestion, StrategyType
import json
from pathlib import Path
from typing import Optional
from inittialize import learned_course, student_semester
import logging
import sys
import io

# Force UTF-8 encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Create FastMCP server instance
mcp = FastMCP("course-scheduler")

# Global scheduler instance
scheduler: Optional[CourseScheduler] = None
curriculum_file: Optional[str] = None
processed_file: Optional[str] = None


@mcp.tool()
def fetch_student_info():
    return {
        "learned_course": learned_course,
        "student_semester": student_semester
    }


@mcp.tool()
def initialize_scheduler(
    curriculum_file_path: str = r"D:\HaUI-Agent\khung ctrinh cntt.json",
    processed_file_path: str = r"D:\HaUI-Agent\sample.json"
) -> str:
    """
    Initialize the course scheduler with curriculum data files.
    Must be called before using other tools.

    Args:
        curriculum_file_path: Absolute path to curriculum JSON file
        processed_file_path: Absolute path to processed curriculum JSON file

    Returns:
        JSON string with initialization result
    """
    global scheduler, curriculum_file, processed_file

    try:
        # Verify files exist
        if not Path(curriculum_file_path).exists():
            return json.dumps({
                "error": f"Curriculum file not found: {curriculum_file_path}",
                "success": False
            }, indent=2)

        if not Path(processed_file_path).exists():
            return json.dumps({
                "error": f"Processed file not found: {processed_file_path}",
                "success": False
            }, indent=2)

        curriculum_file = curriculum_file_path
        processed_file = processed_file_path
        scheduler = CourseScheduler(curriculum_file, processed_file)

        result = {
            "success": True,
            "message": "Course scheduler initialized successfully",
            "curriculum_file": curriculum_file,
            "processed_file": processed_file,
            "total_courses": len(scheduler.course_map)
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "success": False
        }, indent=2)


@mcp.tool()
def suggest_courses(
    completed_courses: list[str] = learned_course,
    current_semester: int = student_semester,
    max_credits: int = 20,
    priority_courses: list[str] = [],
    non_priority_courses: list[str] = [],
    strict_credit_limit: bool = False  # ✅ NEW: Đảm bảo nghiêm khắc số tín chỉ
) -> str:
    """
    Generate optimized course enrollment suggestions.

    Args:
        completed_courses: List of completed course codes (e.g., ['IT6015', 'BS6002'])
        current_semester: Current semester number (1-8)
        max_credits: Maximum number of credits to enroll (default: 20)
        priority_courses: Course names/codes the student WANTS to take (optional)
        non_priority_courses: Course names/codes the student DOES NOT want to take (optional)
        strict_credit_limit: If True, ensures total credits equals max_credits exactly (default: False)
                            If False, allows total credits <= max_credits

    Returns:
        JSON string with course suggestions and reasoning
    """
    if scheduler is None:
        return json.dumps({
            "error": "Scheduler not initialized. Please call initialize_scheduler first.",
            "success": False
        }, indent=2)

    try:
        result = scheduler.suggest_courses(
            priority_courses=priority_courses or [],
            non_priority_courses=non_priority_courses or [],
            max_credits=max_credits,
            completed_courses=completed_courses,
            current_semester=current_semester
        )

        # ✅ NEW: Áp dụng strict credit limit nếu được yêu cầu
        if strict_credit_limit:
            result = _apply_strict_credit_limit(
                result,
                max_credits,
                completed_courses,
                current_semester
            )

        # Convert suggestions to serializable format
        suggestions_data = []
        for sugg in result["suggestions"]:
            suggestions_data.append({
                "course_code": sugg.ma_hoc_phan,
                "course_name": sugg.ten_hoc_phan,
                "credits": sugg.so_tin_chi,
                "reason": sugg.reason,
                "strategy": sugg.strategy.value,
                "warnings": sugg.warnings,
                "is_auto_included": sugg.is_auto_included
            })

        output = {
            "success": True,
            "suggestions": suggestions_data,
            "total_credits": result["total_credits"],
            "warnings": result["warnings"],
            "errors": result["errors"],
            "strict_mode": strict_credit_limit,
            "credit_status": "exact_match" if result["total_credits"] == max_credits else "under_limit"
        }

        return json.dumps(output, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "success": False
        }, indent=2)


def _apply_strict_credit_limit(
    result: dict,
    target_credits: int,
    completed_courses: list[str] = learned_course,
    current_semester: int = student_semester
) -> dict:
    """
    Áp dụng strict credit limit - đảm bảo tổng tín chỉ đúng bằng target_credits

    Chiến lược:
    1. Nếu total < target: Thêm môn học từ các kỳ tiếp theo (theo thứ tự ưu tiên), loại bỏ ngẫu nhiên 1 môn và thêm môn khác cho đến khi đạt đủ
    2. Nếu total > target: Loại bỏ môn học ít ưu tiên nhất (giữ lại catch-up và priority)
    3. Ưu tiên: CATCH-UP > PRIORITY > ON-TRACK > ADVANCED

    Args:
        result: Kết quả gợi ý ban đầu
        target_credits: Số tín chỉ mục tiêu
        completed_courses: Danh sách môn đã học
        current_semester: Kỳ hiện tại

    Returns:
        dict: Kết quả đã điều chỉnh
    """
    from copy import deepcopy
    import random

    adjusted_result = deepcopy(result)
    current_total = adjusted_result["total_credits"]
    suggestions = adjusted_result["suggestions"]

    # Trường hợp 1: Cần thêm tín chỉ
    if current_total < target_credits:
        deficit = target_credits - current_total
        completed_set = set(completed_courses)

        adjusted_result["warnings"].append(
            f"⚠️ Chế độ nghiêm ngặt: Cần thêm {deficit} tín chỉ để đạt đúng {target_credits} tín chỉ."
        )

        # Thuật toán lặp: loại bỏ và thêm môn cho đến khi đạt target
        max_iterations = 10  # Giới hạn số lần lặp để tránh vòng lặp vô hạn
        iteration = 0

        while current_total < target_credits and iteration < max_iterations:
            iteration += 1
            remaining_deficit = target_credits - current_total

            print(
                f"Iteration {iteration}: Need {remaining_deficit} more credits")

            # Bước 1: Tìm tất cả môn có thể thêm (theo thứ tự khung chương trình)
            suggested_codes = {s.ma_hoc_phan for s in suggestions}
            candidate_courses = []

            for code, course in scheduler.course_map.items():
                if (code not in completed_set and
                    code not in suggested_codes and
                        scheduler._check_prerequisites(course, completed_set)):

                    # Tính độ ưu tiên theo khung chương trình (semester trước → sau)
                    priority_score = 0
                    if course.hoc_ky < current_semester:
                        priority_score = 1000 + \
                            (current_semester - course.hoc_ky) * 100  # CATCH-UP
                    elif course.hoc_ky == current_semester:
                        priority_score = 500  # ON-TRACK
                    else:
                        priority_score = 100 - \
                            (course.hoc_ky - current_semester) * 10  # ADVANCED

                    candidate_courses.append({
                        "course": course,
                        "priority": priority_score,
                        "credits": course.so_tin_chi
                    })

            # Sắp xếp theo khung chương trình (semester tăng dần, rồi priority giảm dần)
            candidate_courses.sort(key=lambda x: (
                x["course"].hoc_ky, -x["priority"]))

            # Bước 2: Thử thêm môn đầu tiên có thể thêm
            added_any = False
            for candidate in candidate_courses:
                if current_total + candidate["credits"] <= target_credits:
                    # Thêm môn này
                    course = candidate["course"]

                    # Xác định strategy
                    if course.hoc_ky < current_semester:
                        strategy = StrategyType.CATCH_UP
                        reason = f"CATCH-UP (Strict Mode): Môn học kỳ {course.hoc_ky} - Bạn đang kỳ {current_semester}"
                    elif course.hoc_ky == current_semester:
                        strategy = StrategyType.ON_TRACK
                        reason = f"ON-TRACK (Strict Mode): Môn học đúng kỳ {current_semester}"
                    else:
                        strategy = StrategyType.ADVANCED
                        reason = f"ADVANCED (Strict Mode): Môn học kỳ {course.hoc_ky} - Học sớm hơn kế hoạch"

                    suggestion = CourseSuggestion(
                        ma_hoc_phan=course.ma_hoc_phan,
                        ten_hoc_phan=course.ten_hoc_phan,
                        so_tin_chi=course.so_tin_chi,
                        reason=reason,
                        strategy=strategy,
                        warnings=[
                            "Thêm tự động để đạt đúng số tín chỉ mục tiêu"] if strategy == StrategyType.ADVANCED else [],
                        is_auto_included=True
                    )

                    suggestions.append(suggestion)
                    current_total += candidate["credits"]
                    added_any = True
                    print(
                        f"Added: {course.ma_hoc_phan} ({candidate['credits']} credits)")
                    break

            # Bước 3: Nếu không thể thêm môn nào, loại bỏ 1 môn ít quan trọng
            if not added_any and suggestions:
                # Tìm môn ít quan trọng nhất để loại bỏ (không phải CATCH-UP hoặc PRIORITY)
                removable_courses = []

                for sugg in suggestions:
                    if sugg.strategy in [StrategyType.ON_TRACK, StrategyType.ADVANCED]:
                        # Ưu tiên loại bỏ: ADVANCED > ON-TRACK
                        priority_score = 10 if sugg.strategy == StrategyType.ADVANCED else 50
                        removable_courses.append({
                            "suggestion": sugg,
                            "priority": priority_score,
                            "credits": sugg.so_tin_chi
                        })

                if removable_courses:
                    # Loại bỏ 1 môn ít quan trọng nhất
                    # Ưu tiên thấp + tín chỉ cao
                    removable_courses.sort(key=lambda x: (
                        x["priority"], -x["credits"]))
                    to_remove = removable_courses[0]["suggestion"]

                    suggestions.remove(to_remove)
                    current_total -= to_remove.so_tin_chi
                    print(
                        f"Removed: {to_remove.ma_hoc_phan} ({to_remove.so_tin_chi} credits)")

                    adjusted_result["warnings"].append(
                        f"🔄 Iteration {iteration}: Đã loại bỏ {to_remove.ten_hoc_phan} để tạo chỗ cho môn phù hợp hơn"
                    )
                else:
                    # Không thể loại bỏ môn nào (chỉ còn CATCH-UP/PRIORITY)
                    print("Cannot remove any courses (only CATCH-UP/PRIORITY left)")
                    break

            # Kiểm tra xem có đạt target chưa
            if current_total == target_credits:
                print(f"Target achieved: {current_total} credits")
                break

        # Cập nhật kết quả
        adjusted_result["total_credits"] = current_total
        adjusted_result["suggestions"] = suggestions

        if current_total < target_credits:
            adjusted_result["warnings"].append(
                f"Sau {iteration} lần thử: Chỉ đạt {current_total}/{target_credits} tín chỉ. "
                f"Không thể tối ưu thêm với các ràng buộc hiện tại."
            )
    # Trường hợp 2: Cần giảm tín chỉ
    elif current_total > target_credits:
        excess = current_total - target_credits

        # Phân loại môn học theo độ ưu tiên (không thể xóa CATCH-UP và PRIORITY)
        removable_courses = []

        for sugg in suggestions:
            if (sugg.strategy in [StrategyType.ON_TRACK, StrategyType.ADVANCED] and
                    not sugg.is_auto_included):

                # Độ ưu tiên thấp = dễ xóa
                priority_score = 0
                if sugg.strategy == StrategyType.ADVANCED:
                    priority_score = 10  # Xóa ADVANCED trước
                elif sugg.strategy == StrategyType.ON_TRACK:
                    priority_score = 50  # Xóa ON-TRACK sau

                removable_courses.append({
                    "suggestion": sugg,
                    "priority": priority_score,
                    "credits": sugg.so_tin_chi
                })

        # Sắp xếp theo độ ưu tiên tăng dần (xóa môn ít quan trọng trước)
        removable_courses.sort(key=lambda x: x["priority"])

        # Xóa môn để đạt đúng target_credits
        removed_credits = 0
        courses_to_remove = []

        for removable in removable_courses:
            if removed_credits + removable["credits"] <= excess:
                courses_to_remove.append(removable["suggestion"])
                removed_credits += removable["credits"]

                if removed_credits == excess:
                    break

        # Loại bỏ các môn đã chọn
        for course_to_remove in courses_to_remove:
            suggestions.remove(course_to_remove)

        adjusted_result["total_credits"] = current_total - removed_credits

        if removed_credits < excess:
            adjusted_result["warnings"].append(
                f"⚠️ Chỉ có thể giảm {removed_credits}/{excess} tín chỉ. "
                f"Các môn còn lại là CATCH-UP hoặc PRIORITY, không thể loại bỏ."
            )

    # Cập nhật suggestions
    adjusted_result["suggestions"] = suggestions

    # Thêm thông báo về strict mode
    # Cập nhật thông báo về strict mode
    if adjusted_result["total_credits"] == target_credits:
        adjusted_result["warnings"].insert(0,
                                           f"✅ STRICT MODE: Đã đạt đúng {target_credits} tín chỉ sau {iteration} lần điều chỉnh"
                                           )
    else:
        adjusted_result["warnings"].insert(0,
                                           f"⚠️ STRICT MODE: Không thể đạt đúng {target_credits} tín chỉ. "
                                           f"Hiện tại: {adjusted_result['total_credits']} tín chỉ"
                                           )

    return adjusted_result


@mcp.tool()
def validate_prerequisites(
    course_code: str,
    completed_courses: list[str] = learned_course
) -> str:
    """
    Check if a student has met the prerequisites for a specific course.

    Args:
        course_code: Course code to validate (e.g., 'IT6002')
        completed_courses: List of completed course codes

    Returns:
        JSON string with validation result and missing prerequisites
    """
    if scheduler is None:
        return json.dumps({
            "error": "Scheduler not initialized. Please call initialize_scheduler first.",
            "success": False
        }, indent=2)

    try:
        course_code = course_code.upper()
        completed_set = set(completed_courses)

        if course_code not in scheduler.course_map:
            return json.dumps({
                "error": f"Course not found: {course_code}",
                "success": False
            }, indent=2)

        course = scheduler.course_map[course_code]
        is_valid = scheduler._check_prerequisites(course, completed_set)

        missing_prereqs = []
        if not is_valid and course.mon_tien_quyet:
            missing_prereqs = [
                {
                    "code": prereq,
                    "name": scheduler.course_map[prereq].ten_hoc_phan
                    if prereq in scheduler.course_map else "Unknown"
                }
                for prereq in course.mon_tien_quyet
                if prereq not in completed_set
            ]

        result = {
            "success": True,
            "course_code": course_code,
            "course_name": course.ten_hoc_phan,
            "is_valid": is_valid,
            "prerequisites_required": course.mon_tien_quyet,
            "missing_prerequisites": missing_prereqs,
            "message": "Prerequisites satisfied" if is_valid else "Missing required prerequisites"
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "success": False
        }, indent=2)


@mcp.tool()
def get_course_info(course_identifier: str) -> str:
    """
    Get detailed information about a specific course.

    Args:
        course_identifier: Course code (e.g., 'IT6015') or name (e.g., 'Kỹ thuật lập trình')

    Returns:
        JSON string with course details including prerequisites, co-requisites, credits, semester
    """
    if scheduler is None:
        return json.dumps({
            "error": "Scheduler not initialized. Please call initialize_scheduler first.",
            "success": False
        }, indent=2)

    try:
        # Try to find course by code or name
        course_code = None
        if course_identifier.upper() in scheduler.course_map:
            course_code = course_identifier.upper()
        else:
            # Try name mapping
            codes, _ = scheduler.map_course_names_to_codes([course_identifier])
            if codes:
                course_code = codes[0]

        if not course_code:
            return json.dumps({
                "error": f"Course not found: {course_identifier}",
                "success": False
            }, indent=2)

        course = scheduler.course_map[course_code]

        prereq_details = [
            {
                "code": prereq,
                "name": scheduler.course_map[prereq].ten_hoc_phan
                if prereq in scheduler.course_map else "Unknown"
            }
            for prereq in course.mon_tien_quyet
        ]

        coreq_details = [
            {
                "code": coreq,
                "name": scheduler.course_map[coreq].ten_hoc_phan
                if coreq in scheduler.course_map else "Unknown"
            }
            for coreq in course.mon_hoc_truoc
        ]

        result = {
            "success": True,
            "course_code": course.ma_hoc_phan,
            "course_name": course.ten_hoc_phan,
            "credits": course.so_tin_chi,
            "semester": course.hoc_ky,
            "is_mandatory": course.is_mandatory,
            "elective_group": course.elective_group,
            "group_min_credits": course.group_min_credits,
            "prerequisites": prereq_details,
            "co_requisites": coreq_details
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "success": False
        }, indent=2)


@mcp.tool()
def search_courses(query: str, max_results: int = 10) -> str:
    """
    Search for courses by name, code, or keywords. Supports fuzzy matching.

    Args:
        query: Search query (course name or code)
        max_results: Maximum number of results to return (default: 10)

    Returns:
        JSON string with search results
    """
    if scheduler is None:
        return json.dumps({
            "error": "Scheduler not initialized. Please call initialize_scheduler first.",
            "success": False
        }, indent=2)

    try:
        query_lower = query.lower()
        results = []

        for code, course in scheduler.course_map.items():
            if (query_lower in course.ten_hoc_phan.lower() or
                    query_lower in code.lower()):
                results.append({
                    "course_code": course.ma_hoc_phan,
                    "course_name": course.ten_hoc_phan,
                    "credits": course.so_tin_chi,
                    "semester": course.hoc_ky,
                    "is_mandatory": course.is_mandatory
                })

            if len(results) >= max_results:
                break

        output = {
            "success": True,
            "query": query,
            "results_found": len(results),
            "results": results
        }

        return json.dumps(output, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "success": False
        }, indent=2)


@mcp.tool()
def get_semester_courses(semester: int, include_electives: bool = True) -> str:
    """
    Get all courses scheduled for a specific semester.

    Args:
        semester: Semester number (1-8)
        include_electives: Whether to include elective courses (default: True)

    Returns:
        JSON string with courses for the semester
    """
    if scheduler is None:
        return json.dumps({
            "error": "Scheduler not initialized. Please call initialize_scheduler first.",
            "success": False
        }, indent=2)

    try:
        courses = []
        for code, course in scheduler.course_map.items():
            if course.hoc_ky == semester:
                if not include_electives and not course.is_mandatory:
                    continue

                courses.append({
                    "course_code": course.ma_hoc_phan,
                    "course_name": course.ten_hoc_phan,
                    "credits": course.so_tin_chi,
                    "is_mandatory": course.is_mandatory,
                    "elective_group": course.elective_group
                })

        # Separate mandatory and elective
        mandatory = [c for c in courses if c["is_mandatory"]]
        elective = [c for c in courses if not c["is_mandatory"]]

        result = {
            "success": True,
            "semester": semester,
            "total_courses": len(courses),
            "mandatory_courses": mandatory,
            "elective_courses": elective,
            "total_credits": sum(c["credits"] for c in courses)
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "success": False
        }, indent=2)


@mcp.tool()
def calculate_remaining_credits(completed_courses: list[str] = learned_course) -> str:
    """
    Calculate remaining credits needed for graduation.

    Args:
        completed_courses: List of completed course codes

    Returns:
        JSON string with credit calculation
    """
    if scheduler is None:
        return json.dumps({
            "error": "Scheduler not initialized. Please call initialize_scheduler first.",
            "success": False
        }, indent=2)

    try:
        completed_credits = sum(
            scheduler.course_map[code].so_tin_chi
            for code in completed_courses
            if code in scheduler.course_map
        )

        # Total required credits (from curriculum)
        total_required = 140  # Standard IT program

        remaining = total_required - completed_credits

        result = {
            "success": True,
            "total_required_credits": total_required,
            "completed_credits": completed_credits,
            "remaining_credits": max(0, remaining),
            "completion_percentage": (completed_credits / total_required * 100) if total_required > 0 else 0,
            "courses_completed": len([c for c in completed_courses if c in scheduler.course_map])
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "success": False
        }, indent=2)


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    print("Starting MCP server...")
    # mcp.run(transport="streamable-http")
    # config = mcp_config.MCPConfig()
    # print(config.to_dict())
    initialize_scheduler(
        curriculum_file_path=r"E:\HaUI_Agent\khung ctrinh cntt.json",
        processed_file_path=r"E:\HaUI_Agent\sample.json"
    )
    mcp.run(transport="stdio")  # Use stdio transport for better compatibility
