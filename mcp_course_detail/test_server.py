"""
Test script for Course Detail MCP Server
Tests the core functionality without needing MCP client
"""
import server
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock FastMCP if not available
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("⚠️  Warning: mcp package not installed. Creating mock for testing...")

    class FastMCP:
        def __init__(self, name):
            self.name = name

        def tool(self):
            def decorator(func):
                return func
            return decorator

# Now import the server module
sys.path.insert(0, str(Path(__file__).parent))


def test_initialize():
    """Test catalog initialization"""
    print("\n=== TEST 1: Initialize Catalog ===")
    curriculum_file = Path(__file__).parent.parent / "khung ctrinh cntt.json"

    if not curriculum_file.exists():
        print(f"❌ Curriculum file not found: {curriculum_file}")
        return False

    try:
        result = server.initialize_catalog(str(curriculum_file))
        data = json.loads(result)
        print(f"✅ Initialized: {data['total_courses']} courses")
        print(f"   Programs: {', '.join(data['programs'])}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_get_course_detail():
    """Test getting course detail"""
    print("\n=== TEST 2: Get Course Detail ===")

    try:
        # Test with course code
        result = server.get_course_detail(
            course_identifier="IT6002",
            completed_courses=["BS6001", "BS6002", "BS6003"]
        )
        data = json.loads(result)

        if data["status"] == "success":
            print(f"✅ Found course: {data['course']['name']}")
            print(f"   Credits: {data['course']['credits']}")
            print(f"   Semester: {data['course']['semester']}")
            print(f"   Ready: {data['readiness']['is_ready']}")
            if data['readiness']['unmet_prerequisites']:
                print(
                    f"   Missing: {', '.join(data['readiness']['unmet_prerequisites'])}")
            return True
        else:
            print(f"❌ {data['message']}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fuzzy_search():
    """Test fuzzy course name search"""
    print("\n=== TEST 3: Fuzzy Course Name Search ===")

    try:
        result = server.get_course_detail(
            course_identifier="Cau truc du lieu",  # Fuzzy Vietnamese
            completed_courses=["BS6001", "BS6002"]
        )
        data = json.loads(result)

        if data["status"] == "found_multiple":
            print(f"✅ Found {len(data['matches'])} matches:")
            for match in data['matches']:
                print(
                    f"   - {match['code']}: {match['name']} (similarity: {match['similarity']:.2f})")
            return True
        elif data["status"] == "success":
            print(f"✅ Exact match: {data['course']['name']}")
            return True
        else:
            print(f"❌ {data['message']}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_assessment_blueprint():
    """Test assessment blueprint generation"""
    print("\n=== TEST 4: Generate Assessment Blueprint ===")

    try:
        result = server.get_assessment_blueprint("IT6002")
        data = json.loads(result)

        if data["status"] == "success":
            blueprint = data["blueprint"]
            print(f"✅ Generated blueprint for: {blueprint['course_name']}")
            print(
                f"   Foundation topics: {len(blueprint['foundation_topics'])}")
            print(f"   Core concepts: {len(blueprint['core_concepts'])}")
            print(f"   Applied skills: {len(blueprint['applied_skills'])}")
            print(f"   Estimated hours: {blueprint['estimated_prep_hours']}h")
            print(
                f"   Checklist items: {len(blueprint['readiness_checklist'])}")

            # Print sample topics
            if blueprint['core_concepts']:
                print(f"\n   Sample core concept:")
                topic = blueprint['core_concepts'][0]
                print(
                    f"   - {topic['topic']} ({topic['weight_percentage']}%, {topic['difficulty']})")

            return True
        else:
            print(f"❌ {data['message']}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_learning_resources():
    """Test learning resource search"""
    print("\n=== TEST 5: Search Learning Resources ===")

    try:
        result = server.search_learning_resources(
            course_code="IT6002",
            include_web=True,
            include_nonweb=True,
            max_results=5
        )
        data = json.loads(result)

        if data["status"] == "success":
            print(f"✅ Found resources for: {data['course_name']}")
            print(f"   Web sources: {len(data['web_sources'])}")
            print(f"   Non-web sources: {len(data['nonweb_sources'])}")

            # Print sample web source
            if data['web_sources']:
                print(f"\n   Sample web source:")
                source = data['web_sources'][0]
                print(f"   - {source['title']}")
                print(f"     Type: {source['type']}")
                print(f"     Credibility: {source['credibility_score']:.2f}")
                if source['url']:
                    print(f"     URL: {source['url']}")

            # Print sample non-web source
            if data['nonweb_sources']:
                print(f"\n   Sample non-web source:")
                source = data['nonweb_sources'][0]
                print(f"   - {source['title']}")
                print(f"     Type: {source['type']}")
                if source['author']:
                    print(f"     Author: {source['author']}")

            return True
        else:
            print(f"❌ {data['message']}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_course_summary_table():
    """Test course summary table generation"""
    print("\n=== TEST 6: Generate Course Summary Table ===")

    try:
        result = server.generate_course_summary_table(
            course_codes=["IT6002", "IT6015", "IT6003"],
            completed_courses=["BS6001", "BS6002", "BS6003"]
        )
        data = json.loads(result)

        if data["status"] == "success":
            print(f"✅ Generated table with {len(data['courses'])} courses")
            print(f"   Total credits: {data['statistics']['total_credits']}")
            print(f"   Mandatory: {data['statistics']['mandatory_count']}")
            print(f"   Elective: {data['statistics']['elective_count']}")
            print(f"   Ready: {data['statistics']['ready_count']}")

            # Print table header
            print(f"\n   Summary Table:")
            print(
                f"   {'Code':<10} {'Name':<30} {'Credits':<8} {'Semester':<10} {'Type':<12} {'Ready':<10}")
            print(f"   {'-'*90}")

            # Print courses
            for course in data['courses']:
                ready = "✅ Yes" if course['is_ready'] else "❌ No"
                print(
                    f"   {course['code']:<10} {course['name'][:28]:<30} {course['credits']:<8} {course['semester']:<10} {course['type']:<12} {ready:<10}")

            return True
        else:
            print(f"❌ {data['message']}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("COURSE DETAIL MCP SERVER - TEST SUITE")
    print("=" * 70)

    tests = [
        test_initialize,
        test_get_course_detail,
        test_fuzzy_search,
        test_assessment_blueprint,
        test_learning_resources,
        test_course_summary_table
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
