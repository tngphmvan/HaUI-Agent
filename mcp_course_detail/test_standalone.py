"""
Standalone test for Course Detail functions
Tests core functionality without MCP dependencies
"""
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass
from difflib import SequenceMatcher

# Course data structures


@dataclass
class Course:
    code: str
    name: str
    credits: int
    semester: int
    type: str  # mandatory, elective
    prerequisites: List[str]
    corequisites: List[str]
    optional_group: Optional[str] = None


# Global state
course_catalog: Dict[str, Course] = {}
curriculum_data: Optional[Dict] = None


def initialize_catalog(curriculum_file: str) -> str:
    """Initialize course catalog from JSON file"""
    global course_catalog, curriculum_data

    try:
        with open(curriculum_file, 'r', encoding='utf-8') as f:
            curriculum_data = json.load(f)

        # Parse courses
        course_catalog = {}
        programs = set()

        for semester_name, courses_data in curriculum_data.items():
            if not isinstance(courses_data, list):
                continue

            semester_num = int(semester_name.replace("ky", ""))

            for course_data in courses_data:
                if not isinstance(course_data, dict):
                    continue

                code = course_data.get("ma_mon", "")
                name = course_data.get("ten_mon", "")

                if not code or not name:
                    continue

                # Extract program
                if code.startswith("BS"):
                    program = "General"
                elif code.startswith("IT"):
                    program = "Information Technology"
                else:
                    program = "Unknown"

                programs.add(program)

                # Parse prerequisites
                prereq = course_data.get("mon_hoc_truoc", [])
                if isinstance(prereq, str):
                    prereq = [prereq] if prereq else []
                elif not isinstance(prereq, list):
                    prereq = []

                # Parse corequisites
                coreq = course_data.get("mon_tien_quyet", [])
                if isinstance(coreq, str):
                    coreq = [coreq] if coreq else []
                elif not isinstance(coreq, list):
                    coreq = []

                course = Course(
                    code=code,
                    name=name,
                    credits=int(course_data.get("so_tin_chi", 0)),
                    semester=semester_num,
                    type=course_data.get("loai", "mandatory"),
                    prerequisites=prereq,
                    corequisites=coreq,
                    optional_group=course_data.get("nhom_tc", None)
                )

                course_catalog[code] = course

        return json.dumps({
            "status": "success",
            "message": f"Initialized catalog with {len(course_catalog)} courses",
            "total_courses": len(course_catalog),
            "programs": list(programs)
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to initialize catalog: {str(e)}"
        }, ensure_ascii=False)


def fuzzy_match_course(query: str, threshold: float = 0.6) -> List[Dict]:
    """Find courses matching query with fuzzy matching"""
    matches = []

    query_lower = query.lower()

    for code, course in course_catalog.items():
        # Exact code match
        if code.lower() == query_lower:
            matches.append({
                "code": code,
                "name": course.name,
                "similarity": 1.0
            })
            continue

        # Fuzzy name match
        name_lower = course.name.lower()
        similarity = SequenceMatcher(None, query_lower, name_lower).ratio()

        if similarity >= threshold:
            matches.append({
                "code": code,
                "name": course.name,
                "similarity": similarity
            })

    # Sort by similarity
    matches.sort(key=lambda x: x['similarity'], reverse=True)
    return matches[:5]  # Return top 5


def check_readiness(course: Course, completed_courses: List[str]) -> Dict:
    """Check if student is ready for a course"""
    unmet_prereq = [
        p for p in course.prerequisites if p not in completed_courses]
    unmet_coreq = [
        c for c in course.corequisites if c not in completed_courses]

    is_ready = len(unmet_prereq) == 0 and len(unmet_coreq) == 0

    return {
        "is_ready": is_ready,
        "unmet_prerequisites": unmet_prereq,
        "unmet_corequisites": unmet_coreq
    }


def get_course_detail(course_identifier: str, completed_courses: List[str] = None) -> str:
    """Get detailed course information"""
    if completed_courses is None:
        completed_courses = []

    # Try exact match first
    if course_identifier in course_catalog:
        course = course_catalog[course_identifier]
        readiness = check_readiness(course, completed_courses)

        return json.dumps({
            "status": "success",
            "course": {
                "code": course.code,
                "name": course.name,
                "credits": course.credits,
                "semester": course.semester,
                "type": course.type,
                "prerequisites": course.prerequisites,
                "corequisites": course.corequisites,
                "optional_group": course.optional_group
            },
            "readiness": readiness
        }, ensure_ascii=False)

    # Try fuzzy matching
    matches = fuzzy_match_course(course_identifier)

    if len(matches) == 0:
        return json.dumps({
            "status": "not_found",
            "message": f"No course found matching '{course_identifier}'"
        }, ensure_ascii=False)

    if len(matches) == 1:
        # Single match - return it
        course = course_catalog[matches[0]["code"]]
        readiness = check_readiness(course, completed_courses)

        return json.dumps({
            "status": "success",
            "course": {
                "code": course.code,
                "name": course.name,
                "credits": course.credits,
                "semester": course.semester,
                "type": course.type,
                "prerequisites": course.prerequisites,
                "corequisites": course.corequisites,
                "optional_group": course.optional_group
            },
            "readiness": readiness
        }, ensure_ascii=False)

    # Multiple matches
    return json.dumps({
        "status": "found_multiple",
        "message": f"Found {len(matches)} courses matching '{course_identifier}'. Please be more specific.",
        "matches": matches
    }, ensure_ascii=False)


def get_assessment_blueprint(course_code: str) -> str:
    """Generate assessment blueprint for a course"""
    if course_code not in course_catalog:
        return json.dumps({
            "status": "not_found",
            "message": f"Course {course_code} not found"
        }, ensure_ascii=False)

    course = course_catalog[course_code]

    # Generate mock blueprint (in real implementation, this would come from syllabus)
    blueprint = {
        "course_code": course.code,
        "course_name": course.name,
        "foundation_topics": [
            {
                "topic": f"Prerequisites review for {course.name}",
                "weight_percentage": 15,
                "difficulty": "Easy",
                "description": "Review of prerequisite concepts",
                "key_concepts": course.prerequisites
            }
        ],
        "core_concepts": [
            {
                "topic": f"Core theory of {course.name}",
                "weight_percentage": 50,
                "difficulty": "Medium",
                "description": "Main theoretical content",
                "key_concepts": ["Theory 1", "Theory 2", "Theory 3"]
            }
        ],
        "applied_skills": [
            {
                "topic": f"Practical applications",
                "weight_percentage": 35,
                "difficulty": "Hard",
                "description": "Hands-on problem solving",
                "key_concepts": ["Practice 1", "Practice 2", "Project"]
            }
        ],
        "readiness_checklist": [
            f"Completed all prerequisites: {', '.join(course.prerequisites) if course.prerequisites else 'None'}",
            "Reviewed course syllabus",
            "Prepared study materials",
            "Formed study group"
        ],
        "estimated_prep_hours": course.credits * 10
    }

    return json.dumps({
        "status": "success",
        "blueprint": blueprint
    }, ensure_ascii=False)


def search_learning_resources(course_code: str, include_web: bool = True,
                              include_nonweb: bool = True, max_results: int = 10) -> str:
    """Search for learning resources"""
    if course_code not in course_catalog:
        return json.dumps({
            "status": "not_found",
            "message": f"Course {course_code} not found"
        }, ensure_ascii=False)

    course = course_catalog[course_code]

    # Mock resources (in real implementation, this would search actual sources)
    web_sources = []
    nonweb_sources = []

    if include_web:
        web_sources = [
            {
                "title": f"Official Syllabus - {course.name}",
                "type": "official_doc",
                "url": f"https://haui.edu.vn/syllabus/{course.code}",
                "author": "HaUI",
                "date": "2024",
                "credibility_score": 1.0,
                "notes": "Official course syllabus"
            },
            {
                "title": f"Video Lectures - {course.name}",
                "type": "video",
                "url": f"https://youtube.com/search?q={course.name}",
                "author": "Various",
                "date": "2023-2024",
                "credibility_score": 0.8,
                "notes": "YouTube educational content"
            }
        ]

    if include_nonweb:
        nonweb_sources = [
            {
                "title": f"Textbook for {course.name}",
                "type": "textbook",
                "url": None,
                "author": "Academic Press",
                "date": "2022",
                "credibility_score": 0.95,
                "location": "Library - Section C, Shelf 23",
                "notes": "Standard textbook"
            },
            {
                "title": f"Lecture Notes - {course.name}",
                "type": "pdf",
                "url": None,
                "author": "Course Instructor",
                "date": "2024",
                "credibility_score": 1.0,
                "location": "Course portal",
                "notes": "Official lecture slides"
            }
        ]

    return json.dumps({
        "status": "success",
        "course_code": course.code,
        "course_name": course.name,
        "web_sources": web_sources[:max_results],
        "nonweb_sources": nonweb_sources[:max_results]
    }, ensure_ascii=False)


def generate_course_summary_table(course_codes: List[str], completed_courses: List[str] = None) -> str:
    """Generate summary table for multiple courses"""
    if completed_courses is None:
        completed_courses = []

    courses_info = []
    total_credits = 0
    mandatory_count = 0
    elective_count = 0
    ready_count = 0

    for code in course_codes:
        if code not in course_catalog:
            continue

        course = course_catalog[code]
        readiness = check_readiness(course, completed_courses)

        courses_info.append({
            "code": course.code,
            "name": course.name,
            "credits": course.credits,
            "semester": course.semester,
            "type": course.type,
            "prerequisites": course.prerequisites,
            "corequisites": course.corequisites,
            "is_ready": readiness["is_ready"]
        })

        total_credits += course.credits
        if course.type == "mandatory":
            mandatory_count += 1
        else:
            elective_count += 1

        if readiness["is_ready"]:
            ready_count += 1

    return json.dumps({
        "status": "success",
        "courses": courses_info,
        "statistics": {
            "total_courses": len(courses_info),
            "total_credits": total_credits,
            "mandatory_count": mandatory_count,
            "elective_count": elective_count,
            "ready_count": ready_count
        }
    }, ensure_ascii=False)


# Test functions
def test_initialize():
    """Test catalog initialization"""
    print("\n=== TEST 1: Initialize Catalog ===")
    curriculum_file = Path(__file__).parent.parent / "khung ctrinh cntt.json"

    if not curriculum_file.exists():
        print(f"❌ Curriculum file not found: {curriculum_file}")
        return False

    try:
        result = initialize_catalog(str(curriculum_file))
        data = json.loads(result)
        print(f"✅ Initialized: {data['total_courses']} courses")
        print(f"   Programs: {', '.join(data['programs'])}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_course_detail():
    """Test getting course detail"""
    print("\n=== TEST 2: Get Course Detail ===")

    try:
        result = get_course_detail(
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
        result = get_course_detail(
            course_identifier="Cau truc du lieu",
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
        import traceback
        traceback.print_exc()
        return False


def test_assessment_blueprint():
    """Test assessment blueprint generation"""
    print("\n=== TEST 4: Generate Assessment Blueprint ===")

    try:
        result = get_assessment_blueprint("IT6002")
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
        result = search_learning_resources(
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

            if data['web_sources']:
                print(f"\n   Sample web source:")
                source = data['web_sources'][0]
                print(f"   - {source['title']}")
                print(f"     Type: {source['type']}")
                print(f"     Credibility: {source['credibility_score']:.2f}")
                if source['url']:
                    print(f"     URL: {source['url']}")

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
        result = generate_course_summary_table(
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

            print(f"\n   Summary Table:")
            print(
                f"   {'Code':<10} {'Name':<30} {'Credits':<8} {'Semester':<10} {'Type':<12} {'Ready':<10}")
            print(f"   {'-'*90}")

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
    print("COURSE DETAIL - STANDALONE TEST SUITE")
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
