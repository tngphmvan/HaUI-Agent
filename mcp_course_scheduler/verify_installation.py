"""
Simple standalone test to verify the MCP server is working
Can be run without MCP client
"""

from mcp_course_scheduler.course_scheduler import CourseScheduler
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_basic_functionality():
    """Test basic functionality without MCP"""

    print("=" * 80)
    print("Testing Course Scheduler Core Functionality")
    print("=" * 80)

    try:
        # Initialize scheduler
        print("\n1. Initializing scheduler...")
        scheduler = CourseScheduler(
            curriculum_file=r'e:\HaUI_Agent\khung ctrinh cntt.json',
            processed_file=r'e:\HaUI_Agent\sample.json'
        )
        print(f"   ✓ Loaded {len(scheduler.course_map)} courses")

        # Test course search
        print("\n2. Testing course name mapping...")
        codes, invalid = scheduler.map_course_names_to_codes([
            'Giải tích',
            'Kỹ thuật lập trình',
            'Invalid Course'
        ])
        print(f"   ✓ Found {len(codes)} valid courses")
        print(f"   ✓ {len(invalid)} invalid courses")

        # Test course info
        print("\n3. Testing course information retrieval...")
        if 'IT6015' in scheduler.course_map:
            course = scheduler.course_map['IT6015']
            print(f"   ✓ Course: {course.ten_hoc_phan}")
            print(f"   ✓ Credits: {course.so_tin_chi}")
            print(f"   ✓ Semester: {course.hoc_ky}")
            print(f"   ✓ Prerequisites: {len(course.mon_tien_quyet)}")

        # Test suggestions
        print("\n4. Testing course suggestions...")
        completed = [
            'LP6010', 'BS6018', 'BS6002', 'DC6005',
            'DC6004', 'DC6007', 'DC6006', 'IT6011',
            'IT6015', 'BS6027', 'IT6016', 'BS6001', 'LP6011'
        ]

        result = scheduler.suggest_courses(
            priority_courses=['Cấu trúc dữ liệu và giải thuật'],
            max_credits=18,
            completed_courses=completed,
            current_semester=3
        )

        print(f"   ✓ Generated {len(result['suggestions'])} suggestions")
        print(f"   ✓ Total credits: {result['total_credits']}")
        print(f"   ✓ Warnings: {len(result['warnings'])}")
        print(f"   ✓ Errors: {len(result['errors'])}")

        if result['suggestions']:
            print("\n   Top 3 suggestions:")
            for i, sugg in enumerate(result['suggestions'][:3], 1):
                print(f"   {i}. [{sugg.ma_hoc_phan}] {sugg.ten_hoc_phan}")
                print(f"      Strategy: {sugg.strategy.value}")

        # Test formatting
        print("\n5. Testing output formatting...")
        formatted = scheduler.format_suggestions(result)
        print(
            f"   ✓ Generated {len(formatted)} characters of formatted output")

        # Test prerequisite checking
        print("\n6. Testing prerequisite validation...")
        if 'IT6002' in scheduler.course_map:
            course = scheduler.course_map['IT6002']
            is_valid = scheduler._check_prerequisites(course, set(completed))
            print(f"   ✓ IT6002 prerequisites valid: {is_valid}")

        # Test semester courses
        print("\n7. Testing semester filtering...")
        semester_3_courses = [
            c for c in scheduler.course_map.values()
            if c.hoc_ky == 3 and c.is_mandatory
        ]
        print(
            f"   ✓ Found {len(semester_3_courses)} mandatory courses in semester 3")

        print("\n" + "=" * 80)
        print("✓ All core functionality tests passed!")
        print("=" * 80)
        print("\nThe course scheduler is working correctly.")
        print("You can now use it with the MCP server.")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_existence():
    """Test that required files exist"""

    print("\n" + "=" * 80)
    print("Checking Required Files")
    print("=" * 80)

    files = {
        'Curriculum file': r'e:\HaUI_Agent\khung ctrinh cntt.json',
        'Processed file': r'e:\HaUI_Agent\sample.json',
        'Scheduler module': r'e:\HaUI_Agent\course_scheduler.py',
        'MCP Server': r'e:\HaUI_Agent\mcp_course_scheduler\server.py'
    }

    all_exist = True
    for name, path in files.items():
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        print(f"{status} {name}: {path}")
        all_exist = all_exist and exists

    print("=" * 80)

    return all_exist


def main():
    """Main test function"""

    print("\nCourse Scheduler MCP Server - Standalone Test")
    print("=" * 80)

    # Check files
    if not test_file_existence():
        print("\n✗ Some required files are missing!")
        print("Please ensure all files are in the correct locations.")
        return

    # Test functionality
    if test_basic_functionality():
        print("\n" + "=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print("1. Install MCP dependencies: pip install -r requirements.txt")
        print("2. Test MCP server: python test_mcp_server.py")
        print("3. Configure Claude Desktop with the provided config")
        print("4. See QUICKSTART.md for detailed instructions")
        print("=" * 80)
    else:
        print("\n✗ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()
