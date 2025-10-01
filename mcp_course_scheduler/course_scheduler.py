"""
Optimized Course Scheduling Suggestion System
Use Case ID: UC-001
Version: 1.0
Date: October 1, 2025

This module implements an intelligent course scheduling algorithm that:
- Complies with prerequisite and co-requisite requirements
- Respects student preferences
- Optimizes learning path according to curriculum framework
- Provides clear reasoning for each suggestion
"""

import json
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class StrategyType(Enum):
    """Enumeration for course selection strategies"""
    CATCH_UP = "CATCH-UP"
    ON_TRACK = "ON-TRACK"
    ADVANCED = "ADVANCED"
    PRIORITY = "PRIORITY REQUEST"
    NOT_OPTIMAL = "NOT OPTIMAL"


@dataclass
class CourseDetail:
    """Data class representing a course with all its metadata"""
    ma_hoc_phan: str
    ten_hoc_phan: str
    so_tin_chi: float
    hoc_ky: int
    mon_tien_quyet: List[str]
    mon_hoc_truoc: List[str]
    is_mandatory: bool
    elective_group: Optional[str] = None
    group_min_credits: Optional[float] = None


@dataclass
class CourseSuggestion:
    """Data class representing a suggested course with reasoning"""
    ma_hoc_phan: str
    ten_hoc_phan: str
    so_tin_chi: float
    reason: str
    strategy: StrategyType
    warnings: List[str]
    is_auto_included: bool = False  # For co-requisites


class CourseScheduler:
    """
    Main class implementing the optimized course scheduling algorithm
    """

    def __init__(self, curriculum_file: str, processed_file: str):
        """
        Initialize the scheduler with curriculum data

        Args:
            curriculum_file: Path to 'khung ctrinh cntt.json'
            processed_file: Path to 'sample.json'
        """
        self.curriculum_data = self._load_json(curriculum_file)
        self.processed_data = self._load_json(processed_file)
        self.course_map: Dict[str, CourseDetail] = {}
        self.name_to_code_map: Dict[str, str] = {}
        self._build_course_maps()

    def _load_json(self, filepath: str) -> dict:
        """Load JSON file with error handling"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filepath}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in file: {filepath}")

    def _build_course_maps(self):
        """Build internal course mapping structures from curriculum data"""
        curriculum = self.curriculum_data.get('data', {})
        khung_chuong_trinh = curriculum.get('khung_chuong_trinh', [])

        for khoi in khung_chuong_trinh:
            for hoc_phan_kien_thuc in khoi.get('hoc_phan_kien_thuc', []):
                # Process mandatory courses
                
                for course in hoc_phan_kien_thuc.get('kien_thuc_bat_buoc', []):
                    self._add_course_to_map(course, is_mandatory=True)
                
                # Process elective courses
                for tu_chon_group in hoc_phan_kien_thuc.get('kien_thuc_tu_chon', []):

                    group_name = tu_chon_group.get('ten_nhom_tu_chon', '')
                    if group_name in ['TcNN1', 'TcNN2', 'TcNN3', 'Tc Ôn tập NN', 'TcGDTC']:
                        continue  # Skip language and physical education electives
                    group_min_credits = float(
                        tu_chon_group.get('tin_chi_toi_thieu', 0))

                    for course in tu_chon_group.get('danh_sach_mon_tu_chon', []):
                        self._add_course_to_map(
                            course,
                            is_mandatory=False,
                            elective_group=group_name,
                            group_min_credits=group_min_credits
                        )

    def _add_course_to_map(self, course_data: dict, is_mandatory: bool,
                           elective_group: Optional[str] = None,
                           group_min_credits: Optional[float] = None):
        """Add a course to the internal mapping structures"""
        ma_hoc_phan = course_data.get('ma_hoc_phan', '')
        ten_hoc_phan = course_data.get('ten_hoc_phan', '')

        if not ma_hoc_phan:
            return

        # Extract prerequisites and co-requisites from detail
        detail = course_data.get('detail', {})
        mon_tien_quyet = detail.get('mon_tien_quyet', [])
        mon_hoc_truoc = detail.get('mon_hoc_truoc', [])

        course_detail = CourseDetail(
            ma_hoc_phan=ma_hoc_phan,
            ten_hoc_phan=ten_hoc_phan,
            so_tin_chi=float(course_data.get('so_tin_chi', 0)),
            hoc_ky=int(course_data.get('hoc_ky', 1)),
            mon_tien_quyet=mon_tien_quyet if isinstance(
                mon_tien_quyet, list) else [],
            mon_hoc_truoc=mon_hoc_truoc if isinstance(
                mon_hoc_truoc, list) else [],
            is_mandatory=is_mandatory,
            elective_group=elective_group,
            group_min_credits=group_min_credits
        )

        self.course_map[ma_hoc_phan] = course_detail

        # Build name-to-code mapping (case-insensitive)
        if ten_hoc_phan:
            self.name_to_code_map[ten_hoc_phan.lower().strip()] = ma_hoc_phan

    def map_course_names_to_codes(self, course_names: List[str]) -> Tuple[List[str], List[str]]:
        """
        Map course names to course codes with fuzzy matching

        Args:
            course_names: List of course names entered by user

        Returns:
            Tuple of (valid_codes, invalid_names)
        """
        valid_codes = []
        invalid_names = []

        for name in course_names:
            normalized_name = name.lower().strip()

            # Direct match
            if normalized_name in self.name_to_code_map:
                valid_codes.append(self.name_to_code_map[normalized_name])
            # Try matching by code directly
            elif name.upper() in self.course_map:
                valid_codes.append(name.upper())
            else:
                # Fuzzy match - check if name is contained in any course name
                found = False
                for course_name, code in self.name_to_code_map.items():
                    if normalized_name in course_name or course_name in normalized_name:
                        valid_codes.append(code)
                        found = True
                        break

                if not found:
                    invalid_names.append(name)

        return valid_codes, invalid_names

    def _check_prerequisites(self, course: CourseDetail,
                             completed_courses: Set[str]) -> bool:
        """
        Check if prerequisites are satisfied (BR-001, BR-002)

        Args:
            course: Course to check
            completed_courses: Set of completed course codes

        Returns:
            True if prerequisites are satisfied
        """
        if not course.mon_tien_quyet:
            return True

        # Need at least 1 completed prerequisite
        for prereq in course.mon_tien_quyet:
            if prereq in completed_courses:
                return True

        return False

    def _check_elective_limit(self, course: CourseDetail,
                              completed_courses: Set[str],
                              current_suggestions: List[CourseSuggestion]) -> bool:
        """
        Check if elective credit limit is satisfied (BR-003)

        Args:
            course: Elective course to check
            completed_courses: Set of completed course codes
            current_suggestions: Currently suggested courses

        Returns:
            True if adding this course won't exceed elective group limit
        """
        if course.is_mandatory or not course.elective_group:
            return True

        # Calculate completed credits in this elective group
        completed_credits = sum(
            self.course_map[code].so_tin_chi
            for code in completed_courses
            if code in self.course_map
            and self.course_map[code].elective_group == course.elective_group
        )

        # Calculate suggested credits in this elective group
        suggested_credits = sum(
            sugg.so_tin_chi
            for sugg in current_suggestions
            if sugg.ma_hoc_phan in self.course_map
            and self.course_map[sugg.ma_hoc_phan].elective_group == course.elective_group
        )

        total_credits = completed_credits + suggested_credits + course.so_tin_chi

        return total_credits <= (course.group_min_credits or float('inf'))

    def _get_corequisites(self, course: CourseDetail,
                          completed_courses: Set[str]) -> List[str]:
        """
        Get unmet co-requisites that need to be included (BR-004)

        Args:
            course: Course to check
            completed_courses: Set of completed course codes

        Returns:
            List of co-requisite course codes that need to be added
        """
        unmet_coreqs = []

        for coreq in course.mon_hoc_truoc:
            if coreq not in completed_courses:
                unmet_coreqs.append(coreq)

        return unmet_coreqs

    def _determine_strategy(self, course: CourseDetail,
                            current_semester: int,
                            is_priority: bool,
                            has_unmet_coreqs: bool) -> Tuple[StrategyType, str]:
        """
        Determine the strategy and reasoning for a course

        Args:
            course: Course to evaluate
            current_semester: Current semester number
            is_priority: Whether this is a priority course
            has_unmet_coreqs: Whether course has unmet co-requisites

        Returns:
            Tuple of (StrategyType, reasoning_text)
        """
        if is_priority:
            return (StrategyType.PRIORITY,
                    f"Included based on your priority request")

        if course.hoc_ky < current_semester:
            return (StrategyType.CATCH_UP,
                    f"CATCH-UP: You are behind the standard curriculum pace for this course (scheduled for Semester {course.hoc_ky})")

        if course.hoc_ky == current_semester:
            return (StrategyType.ON_TRACK,
                    f"ON-TRACK: This course aligns with your current semester in the curriculum")

        # course.hoc_ky > current_semester
        if has_unmet_coreqs:
            return (StrategyType.NOT_OPTIMAL,
                    f"⚠️ WARNING: This course is scheduled for Semester {course.hoc_ky} (future). Not optimal path.")
        else:
            return (StrategyType.ADVANCED,
                    f"ADVANCED: Ahead of standard pace (Semester {course.hoc_ky}) but eligible")

    def _evaluate_course(self, course: CourseDetail,
                         completed_courses: Set[str],
                         non_priority_codes: Set[str],
                         current_suggestions: List[CourseSuggestion],
                         current_semester: int,
                         is_priority: bool = False,
                         is_coreq: bool = False) -> Optional[CourseSuggestion]:
        """
        Evaluate if a course should be suggested

        Args:
            course: Course to evaluate
            completed_courses: Set of completed course codes
            non_priority_codes: Set of non-priority course codes
            current_suggestions: Currently suggested courses
            current_semester: Current semester number
            is_priority: Whether this is a priority course
            is_coreq: Whether this is being added as a co-requisite

        Returns:
            CourseSuggestion if course should be added, None otherwise
        """
        # Skip if already completed
        if course.ma_hoc_phan in completed_courses:
            return None

        # Skip if already suggested
        suggested_codes = {sugg.ma_hoc_phan for sugg in current_suggestions}
        if course.ma_hoc_phan in suggested_codes:
            return None

        # BR-008: Skip non-priority courses unless they're co-requisites or catch-up
        if (course.ma_hoc_phan in non_priority_codes and
            not is_coreq and
            not is_priority and
                course.hoc_ky >= current_semester):
            return None

        # BR-001, BR-002: Check prerequisites
        if not self._check_prerequisites(course, completed_courses):
            return None

        # BR-003: Check elective limits
        if not self._check_elective_limit(course, completed_courses, current_suggestions):
            return None

        # Check co-requisites
        unmet_coreqs = self._get_corequisites(course, completed_courses)
        has_unmet_coreqs = len(unmet_coreqs) > 0

        # Determine strategy and reasoning
        strategy, reason = self._determine_strategy(
            course, current_semester, is_priority, has_unmet_coreqs
        )

        # Build warnings
        warnings = []
        if has_unmet_coreqs:
            coreq_names = [self.course_map[code].ten_hoc_phan
                           for code in unmet_coreqs if code in self.course_map]
            warnings.append(
                f"Co-requisite courses must be registered: {', '.join(coreq_names)}"
            )

        if course.hoc_ky > current_semester:
            warnings.append(
                f"Consider following the standard curriculum path for optimal learning progression"
            )

        return CourseSuggestion(
            ma_hoc_phan=course.ma_hoc_phan,
            ten_hoc_phan=course.ten_hoc_phan,
            so_tin_chi=course.so_tin_chi,
            reason=reason,
            strategy=strategy,
            warnings=warnings,
            is_auto_included=is_coreq
        )

    def suggest_courses(self,
                        priority_courses: List[str] = None,
                        non_priority_courses: List[str] = None,
                        max_credits: int = 20,
                        completed_courses: List[str] = None,
                        current_semester: int = 1) -> Dict:
        """
        Main function to generate optimized course suggestions

        Args:
            priority_courses: List of course names student WANTS to take
            non_priority_courses: List of course names student DOES NOT want
            max_credits: Maximum credits student wants to enroll
            completed_courses: List of completed course codes
            current_semester: Current semester number

        Returns:
            Dictionary containing:
                - suggestions: List of CourseSuggestion objects
                - total_credits: Total suggested credits
                - excluded_courses: Courses that couldn't be included
                - errors: Any validation errors
                - warnings: General warnings
        """
        # Initialize
        priority_courses = priority_courses or []
        non_priority_courses = non_priority_courses or []
        completed_courses = completed_courses or []

        result = {
            "suggestions": [],
            "total_credits": 0,
            "excluded_courses": [],
            "errors": [],
            "warnings": []
        }

        # Validate max credits
        if max_credits <= 0:
            result["errors"].append("Maximum credits must be greater than 0")
            return result

        # Map course names to codes
        priority_codes, invalid_priority = self.map_course_names_to_codes(
            priority_courses)
        non_priority_codes, invalid_non_priority = self.map_course_names_to_codes(
            non_priority_courses)

        if invalid_priority:
            result["errors"].append(
                f"Invalid priority courses: {', '.join(invalid_priority)}")

        if invalid_non_priority:
            result["errors"].append(
                f"Invalid non-priority courses: {', '.join(invalid_non_priority)}")

        if result["errors"]:
            return result

        # Convert to sets for faster lookup
        completed_set = set(completed_courses)
        non_priority_set = set(non_priority_codes)
        priority_set = set(priority_codes)

        suggestions: List[CourseSuggestion] = []
        total_credits = 0

        # Get all courses sorted by semester
        all_courses = sorted(self.course_map.values(), key=lambda c: c.hoc_ky)

        # STEP 1: Process catch-up courses (Strategy 1)
        for course in all_courses:
            if course.hoc_ky < current_semester:
                if total_credits + course.so_tin_chi <= max_credits:
                    suggestion = self._evaluate_course(
                        course, completed_set, non_priority_set,
                        suggestions, current_semester, is_priority=False
                    )
                    if suggestion:
                        suggestions.append(suggestion)
                        total_credits += course.so_tin_chi

                        # Add co-requisites (BR-004)
                        coreqs = self._get_corequisites(course, completed_set)
                        for coreq_code in coreqs:
                            if coreq_code in self.course_map:
                                coreq_course = self.course_map[coreq_code]
                                if total_credits + coreq_course.so_tin_chi <= max_credits:
                                    coreq_sugg = self._evaluate_course(
                                        coreq_course, completed_set, non_priority_set,
                                        suggestions, current_semester, is_coreq=True
                                    )
                                    if coreq_sugg:
                                        suggestions.append(coreq_sugg)
                                        total_credits += coreq_course.so_tin_chi

        # STEP 2: Process priority courses (BR-009)
        for priority_code in priority_set:
            if priority_code in self.course_map:
                course = self.course_map[priority_code]
                if total_credits + course.so_tin_chi <= max_credits:
                    suggestion = self._evaluate_course(
                        course, completed_set, non_priority_set,
                        suggestions, current_semester, is_priority=True
                    )
                    if suggestion:
                        suggestions.append(suggestion)
                        total_credits += course.so_tin_chi

                        # Add co-requisites
                        coreqs = self._get_corequisites(course, completed_set)
                        for coreq_code in coreqs:
                            if coreq_code in self.course_map:
                                coreq_course = self.course_map[coreq_code]
                                if total_credits + coreq_course.so_tin_chi <= max_credits:
                                    coreq_sugg = self._evaluate_course(
                                        coreq_course, completed_set, non_priority_set,
                                        suggestions, current_semester, is_coreq=True
                                    )
                                    if coreq_sugg:
                                        suggestions.append(coreq_sugg)
                                        total_credits += coreq_course.so_tin_chi
                    else:
                        result["warnings"].append(
                            f"Cannot include priority course '{course.ten_hoc_phan}' - prerequisites not met or credit limit reached"
                        )

        # STEP 3: Fill remaining credits with on-track/advanced courses (Strategy 2 & 3)
        for course in all_courses:
            if total_credits >= max_credits:
                break

            if total_credits + course.so_tin_chi <= max_credits:
                suggestion = self._evaluate_course(
                    course, completed_set, non_priority_set,
                    suggestions, current_semester
                )
                if suggestion:
                    suggestions.append(suggestion)
                    total_credits += course.so_tin_chi

                    # Add co-requisites
                    coreqs = self._get_corequisites(course, completed_set)
                    for coreq_code in coreqs:
                        if coreq_code in self.course_map:
                            coreq_course = self.course_map[coreq_code]
                            if total_credits + coreq_course.so_tin_chi <= max_credits:
                                coreq_sugg = self._evaluate_course(
                                    coreq_course, completed_set, non_priority_set,
                                    suggestions, current_semester, is_coreq=True
                                )
                                if coreq_sugg:
                                    suggestions.append(coreq_sugg)
                                    total_credits += coreq_course.so_tin_chi

        # Build result
        result["suggestions"] = suggestions
        result["total_credits"] = total_credits

        # Check if max credits reached
        if total_credits >= max_credits:
            result["warnings"].append(
                "Maximum credit limit reached. Some eligible courses could not be included."
            )

        # Check if no courses found
        if not suggestions:
            result["warnings"].append(
                "No eligible courses found based on your learning history and preferences."
            )

        return result

    def format_suggestions(self, result: Dict) -> str:
        """
        Format suggestions into human-readable text

        Args:
            result: Result dictionary from suggest_courses()

        Returns:
            Formatted string
        """
        output = []
        output.append("=" * 80)
        output.append("COURSE ENROLLMENT SUGGESTIONS")
        output.append("=" * 80)

        # Display errors
        if result["errors"]:
            output.append("\n❌ ERRORS:")
            for error in result["errors"]:
                output.append(f"  - {error}")
            return "\n".join(output)

        # Display warnings
        if result["warnings"]:
            output.append("\n⚠️  WARNINGS:")
            for warning in result["warnings"]:
                output.append(f"  - {warning}")

        # Display suggestions
        output.append(
            f"\n📚 SUGGESTED COURSES (Total: {result['total_credits']} credits)")
        output.append("-" * 80)

        for i, sugg in enumerate(result["suggestions"], 1):
            output.append(
                f"\n{i}. [{sugg.ma_hoc_phan}] {sugg.ten_hoc_phan} ({sugg.so_tin_chi} credits)")
            output.append(f"   📌 {sugg.reason}")

            if sugg.is_auto_included:
                output.append(f"   🔗 Auto-included as co-requisite")

            if sugg.warnings:
                for warning in sugg.warnings:
                    output.append(f"   ⚠️  {warning}")

        output.append("\n" + "=" * 80)

        return "\n".join(output)


def main():
    """Example usage of the CourseScheduler"""

    # Initialize scheduler
    scheduler = CourseScheduler(
        curriculum_file='e:\\HaUI_Agent\\khung ctrinh cntt.json',
        processed_file='e:\\HaUI_Agent\\sample.json'
    )

    # Example 1: Basic usage
    print("EXAMPLE 1: Student in Semester 3 with some completed courses")
    print("-" * 80)

    completed = ['BS6001', 'BS6002', 'IT6016', 'IT6015', 'LP6010', 'LP6011']

    result = scheduler.suggest_courses(
        priority_courses=['Cấu trúc dữ liệu và giải thuật',
                          'An toàn và bảo mật thông tin'],
        non_priority_courses=['Thiết kế đồ hoạ 2D'],
        max_credits=18,
        completed_courses=completed,
        current_semester=3
    )

    print(scheduler.format_suggestions(result))

    # Example 2: Advanced student
    print("\n\nEXAMPLE 2: Advanced student trying to take courses ahead")
    print("-" * 80)

    completed2 = completed + ['IT6035', 'IT6067', 'IT6126', 'IT6120', 'LP6012']

    result2 = scheduler.suggest_courses(
        priority_courses=['Trí tuệ nhân tạo'],
        max_credits=15,
        completed_courses=completed2,
        current_semester=4
    )

    print(scheduler.format_suggestions(result2))

    # Example 3: Invalid course names
    print("\n\nEXAMPLE 3: Handling invalid course names")
    print("-" * 80)

    result3 = scheduler.suggest_courses(
        priority_courses=['Invalid Course Name', 'Giải tích'],
        max_credits=12,
        completed_courses=[],
        current_semester=1
    )

    print(scheduler.format_suggestions(result3))


if __name__ == "__main__":
    main()
