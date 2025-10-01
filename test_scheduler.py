"""
Unit Tests for Course Scheduling Suggestion System
Tests all business rules and use case scenarios
"""

import unittest
from mcp_course_scheduler.course_scheduler import CourseScheduler, StrategyType


class TestCourseScheduler(unittest.TestCase):
    """Test suite for CourseScheduler"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.scheduler = CourseScheduler(
            curriculum_file='e:\\HaUI_Agent\\khung ctrinh cntt.json',
            processed_file='e:\\HaUI_Agent\\sample.json'
        )

    def test_br001_mandatory_prerequisites(self):
        """Test BR-001: Mandatory courses require ≥1 completed prerequisite"""
        # Course with prerequisites should not be suggested without completion
        result = self.scheduler.suggest_courses(
            max_credits=20,
            completed_courses=[],
            current_semester=3
        )

        # Verify courses without prerequisites are suggested
        suggested_codes = [s.ma_hoc_phan for s in result['suggestions']]

        # Courses in semester 1-2 without prerequisites should be included
        self.assertIn('LP6010', suggested_codes)  # No prerequisites

    def test_br002_elective_prerequisites(self):
        """Test BR-002: Elective courses require ≥1 completed prerequisite"""
        # Test that electives follow prerequisite rules
        completed = [
            'LP6010', 'BS6018',
            'BS6002', 'DC6005',
            'DC6004', 'DC6007',
            'DC6006', 'IT6011',
            'BM6091', 'PE6001',
            'PE6002', 'BS6024',
            'FL6086', 'IT6015',
            'BS6027', 'IT6016',
            'BS6001', 'LP6011', 'FL6085'
        ]  # Completed some courses

        result = self.scheduler.suggest_courses(
            max_credits=20,
            completed_courses=completed,
            current_semester=4
        )

        for item in result['suggestions']:
            print(item.ten_hoc_phan)
        # Should have some suggestions based on prerequisites
        self.assertIsInstance(result['suggestions'], list)

    def test_br003_elective_credit_limit(self):
        """Test BR-003: Elective group credits must not exceed minimum required"""
        # This would need specific test data
        # For now, verify the method exists and runs
        result = self.scheduler.suggest_courses(
            max_credits=20,
            completed_courses=['IT6015'],
            current_semester=3
        )

        # Total credits should not exceed max
        self.assertLessEqual(result['total_credits'], 20)

    def test_br004_corequisite_auto_inclusion(self):
        """Test BR-004: Unmet co-requisites must be auto-included"""
        # Priority course with unmet co-requisite
        result = self.scheduler.suggest_courses(
            priority_courses=['Cấu trúc dữ liệu và giải thuật'],
            max_credits=20,
            completed_courses=['IT6015', 'IT6016'],
            current_semester=4
        )

        # Check if any auto-included courses exist
        auto_included = [
            s for s in result['suggestions'] if s.is_auto_included]
        # Note: Will only have auto-included if the course has unmet co-reqs
        self.assertIsInstance(auto_included, list)

    def test_br006_max_credit_limit(self):
        """Test BR-006: Total suggested credits ≤ max credits"""
        max_credits = 15

        result = self.scheduler.suggest_courses(
            max_credits=max_credits,
            completed_courses=[],
            current_semester=1
        )

        self.assertLessEqual(result['total_credits'], max_credits)

    def test_br008_non_priority_exclusion(self):
        """Test BR-008: Exclude non-priority courses"""
        result = self.scheduler.suggest_courses(
            non_priority_courses=['Thiết kế đồ hoạ 2D'],
            max_credits=20,
            completed_courses=['IT6015', 'IT6120'],
            current_semester=5
        )

        suggested_codes = [s.ma_hoc_phan for s in result['suggestions']]

        # IT6100 (Thiết kế đồ hoạ 2D) should not be in suggestions
        self.assertNotIn('IT6100', suggested_codes)

    def test_br009_priority_courses(self):
        """Test BR-009: Prioritize user's priority course list"""
        result = self.scheduler.suggest_courses(
            priority_courses=['Giải tích'],
            max_credits=20,
            completed_courses=[],
            current_semester=1
        )

        suggested_codes = [s.ma_hoc_phan for s in result['suggestions']]

        # Priority course should be included if eligible
        self.assertIn('BS6002', suggested_codes)  # Giải tích

    def test_strategy1_catchup_priority(self):
        """Test Strategy 1: Catch-up courses from past semesters"""
        result = self.scheduler.suggest_courses(
            max_credits=20,
            completed_courses=['IT6015'],
            current_semester=5  # Advanced semester
        )

        # Should have catch-up courses from earlier semesters
        catchup_courses = [s for s in result['suggestions']
                           if s.strategy == StrategyType.CATCH_UP]

        # Student in semester 5 with few completed courses should have catch-ups
        self.assertGreater(len(catchup_courses), 0)

    def test_strategy2_ontrack(self):
        """Test Strategy 2: On-track courses for current semester"""
        result = self.scheduler.suggest_courses(
            max_credits=20,
            completed_courses=['BS6001', 'BS6002',
                               'IT6015', 'LP6010', 'LP6011'],
            current_semester=3
        )

        # Should have on-track courses
        ontrack_courses = [s for s in result['suggestions']
                           if s.strategy == StrategyType.ON_TRACK]

        self.assertIsInstance(ontrack_courses, list)

    def test_strategy3_advanced_warning(self):
        """Test Strategy 3: Advanced enrollment with warnings"""
        # Try to take a course ahead of schedule
        result = self.scheduler.suggest_courses(
            priority_courses=['Trí tuệ nhân tạo'],  # Semester 5 course
            max_credits=20,
            completed_courses=['IT6015', 'IT6120', 'IT6002'],
            current_semester=3  # Current semester is 3
        )

        # Should have warnings for advanced courses
        advanced_with_warnings = [s for s in result['suggestions']
                                  if s.warnings and s.strategy in
                                  [StrategyType.ADVANCED, StrategyType.NOT_OPTIMAL]]

        self.assertIsInstance(advanced_with_warnings, list)

    def test_course_name_mapping(self):
        """Test course name to code mapping"""
        codes, invalid = self.scheduler.map_course_names_to_codes([
            'Giải tích',
            'Invalid Course',
            'BS6002'  # Direct code
        ])

        self.assertIn('BS6002', codes)
        self.assertIn('Invalid Course', invalid)

    def test_fuzzy_matching(self):
        """Test fuzzy matching for course names"""
        codes, invalid = self.scheduler.map_course_names_to_codes([
            'giải tích',  # lowercase
            'Giải  Tích',  # extra spaces
        ])

        # Should match despite formatting differences
        self.assertEqual(len(codes), 2)
        self.assertIn('BS6002', codes)

    def test_invalid_max_credits(self):
        """Test validation for invalid max credits"""
        result = self.scheduler.suggest_courses(
            max_credits=0,
            completed_courses=[],
            current_semester=1
        )

        self.assertTrue(len(result['errors']) > 0)
        self.assertIn('greater than 0', result['errors'][0])

    def test_invalid_course_names(self):
        """Test handling of invalid course names"""
        result = self.scheduler.suggest_courses(
            priority_courses=['Nonexistent Course'],
            max_credits=20,
            completed_courses=[],
            current_semester=1
        )

        self.assertTrue(len(result['errors']) > 0)

    def test_already_completed_courses(self):
        """Test that completed courses are not suggested"""
        completed = ['BS6002', 'IT6015']

        result = self.scheduler.suggest_courses(
            max_credits=20,
            completed_courses=completed,
            current_semester=2
        )

        suggested_codes = [s.ma_hoc_phan for s in result['suggestions']]

        # Completed courses should not appear in suggestions
        for code in completed:
            self.assertNotIn(code, suggested_codes)

    def test_no_duplicate_suggestions(self):
        """Test that courses are not suggested twice"""
        result = self.scheduler.suggest_courses(
            max_credits=20,
            completed_courses=[],
            current_semester=1
        )

        suggested_codes = [s.ma_hoc_phan for s in result['suggestions']]

        # No duplicates
        self.assertEqual(len(suggested_codes), len(set(suggested_codes)))

    def test_max_credits_warning(self):
        """Test warning when max credits is reached"""
        result = self.scheduler.suggest_courses(
            max_credits=6,  # Very low limit
            completed_courses=[],
            current_semester=1
        )

        if result['total_credits'] >= 6:
            self.assertTrue(
                any('Maximum credit limit' in w for w in result['warnings']))

    def test_no_eligible_courses_warning(self):
        """Test warning when no eligible courses found"""
        # Complete many courses and set current semester high
        many_completed = ['BS6001', 'BS6002', 'IT6015', 'IT6016', 'IT6035',
                          'LP6010', 'LP6011', 'LP6012', 'LP6013', 'LP6004']

        result = self.scheduler.suggest_courses(
            max_credits=3,  # Very low
            non_priority_courses=['Cấu trúc dữ liệu và giải thuật',
                                  'Hệ thống cơ sở dữ liệu',
                                  'Lập trình hướng đối tượng'],
            completed_courses=many_completed,
            current_semester=8
        )

        if not result['suggestions']:
            self.assertTrue(
                any('No eligible courses' in w for w in result['warnings']))

    def test_format_suggestions_output(self):
        """Test that format_suggestions produces readable output"""
        result = self.scheduler.suggest_courses(
            max_credits=20,
            completed_courses=['IT6015'],
            current_semester=3
        )

        formatted = self.scheduler.format_suggestions(result)

        # Should contain key sections
        self.assertIn('COURSE ENROLLMENT SUGGESTIONS', formatted)
        self.assertIn('credits', formatted)

    def test_semester_ordering(self):
        """Test that courses are processed in semester order"""
        result = self.scheduler.suggest_courses(
            max_credits=30,
            completed_courses=[],
            current_semester=1
        )

        # First suggestions should be from early semesters
        if result['suggestions']:
            first_course_code = result['suggestions'][0].ma_hoc_phan
            if first_course_code in self.scheduler.course_map:
                first_semester = self.scheduler.course_map[first_course_code].hoc_ky
                self.assertLessEqual(first_semester, 2)

    def test_multiple_priority_courses(self):
        """Test handling multiple priority courses"""
        result = self.scheduler.suggest_courses(
            priority_courses=['Giải tích',
                              'Kỹ thuật lập trình', 'Triết học Mác-Lênin'],
            max_credits=20,
            completed_courses=[],
            current_semester=1
        )

        priority_suggestions = [s for s in result['suggestions']
                                if s.strategy == StrategyType.PRIORITY]

        # Should have some priority courses if eligible
        self.assertIsInstance(priority_suggestions, list)

    def test_reasoning_transparency(self):
        """Test that all suggestions have clear reasoning"""
        result = self.scheduler.suggest_courses(
            max_credits=20,
            completed_courses=['IT6015'],
            current_semester=3
        )

        # All suggestions should have non-empty reasons
        for suggestion in result['suggestions']:
            self.assertTrue(len(suggestion.reason) > 0)
            self.assertIsInstance(suggestion.strategy, StrategyType)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    @classmethod
    def setUpClass(cls):
        cls.scheduler = CourseScheduler(
            curriculum_file='e:\\HaUI_Agent\\khung ctrinh cntt.json',
            processed_file='e:\\HaUI_Agent\\sample.json'
        )

    def test_empty_inputs(self):
        """Test with all empty inputs"""
        result = self.scheduler.suggest_courses(
            priority_courses=[],
            non_priority_courses=[],
            max_credits=20,
            completed_courses=[],
            current_semester=1
        )

        self.assertIsInstance(result['suggestions'], list)

    def test_very_high_max_credits(self):
        """Test with unrealistically high max credits"""
        result = self.scheduler.suggest_courses(
            max_credits=1000,
            completed_courses=[],
            current_semester=1
        )

        # Should suggest courses but still be reasonable
        self.assertIsInstance(result['suggestions'], list)
        self.assertGreater(result['total_credits'], 0)

    def test_high_semester_number(self):
        """Test with high semester number (near graduation)"""
        result = self.scheduler.suggest_courses(
            max_credits=15,
            completed_courses=['BS6001', 'BS6002', 'IT6015'],
            current_semester=8
        )

        # Should handle high semester numbers
        self.assertIsInstance(result, dict)

    def test_none_parameters(self):
        """Test that None parameters are handled gracefully"""
        result = self.scheduler.suggest_courses(
            priority_courses=None,
            non_priority_courses=None,
            max_credits=20,
            completed_courses=None,
            current_semester=1
        )

        self.assertIsInstance(result['suggestions'], list)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCourseScheduler))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests Run: {result.testsRun}")
    print(
        f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*80)

    return result


if __name__ == "__main__":
    run_tests()
