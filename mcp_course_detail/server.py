"""
MCP Server for Course Detail and Assessment Preparation
Use Case: View Course Detail and Prepare for Assessment

This server provides comprehensive course information, recommended knowledge for exams,
and curated learning resources (web and non-web).
"""

from mcp.server.fastmcp import FastMCP
import json
import logging
import sys
import io
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Force UTF-8 encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Create FastMCP server instance
mcp = FastMCP("course-detail-server")

# Global state
course_catalog: Optional[Dict] = None
curriculum_data: Optional[Dict] = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class KnowledgeTopic:
    """Represents a knowledge topic for exam preparation"""
    topic: str
    weight_percentage: int
    difficulty: str  # Easy, Medium, Hard
    description: str
    key_concepts: List[str]


@dataclass
class AssessmentBlueprint:
    """Assessment blueprint for a course"""
    course_code: str
    course_name: str
    foundation_topics: List[KnowledgeTopic]
    core_concepts: List[KnowledgeTopic]
    applied_skills: List[KnowledgeTopic]
    readiness_checklist: List[str]
    estimated_prep_hours: int


@dataclass
class LearningSource:
    """Represents a learning resource"""
    title: str
    type: str  # web, pdf, textbook, video, official_doc
    url: Optional[str]
    author: Optional[str]
    date: Optional[str]
    credibility_score: float  # 0-1
    location: Optional[str]  # For non-web sources
    notes: str


@dataclass
class CourseDetail:
    """Comprehensive course details"""
    code: str
    name: str
    credits: int
    semester: int
    type: str  # mandatory, elective
    prerequisites: List[str]
    corequisites: List[str]
    learning_outcomes: List[str]
    description: str
    assessment_methods: List[str]
    elective_group: Optional[str]


@mcp.tool()
def initialize_catalog(
    curriculum_file: str = r"D:\HaUI-Agent\khung ctrinh cntt.json"
) -> str:
    """
    Initialize the course catalog from curriculum file.
    Must be called before using other tools.

    Args:
        curriculum_file: Path to curriculum JSON file

    Returns:
        JSON string with initialization status
    """
    global course_catalog, curriculum_data

    try:
        if not Path(curriculum_file).exists():
            return json.dumps({
                "success": False,
                "error": f"Curriculum file not found: {curriculum_file}"
            }, indent=2, ensure_ascii=False)

        with open(curriculum_file, 'r', encoding='utf-8') as f:
            curriculum_data = json.load(f)

        # Build course catalog
        course_catalog = {}

        if 'data' in curriculum_data and 'khung_chuong_trinh' in curriculum_data['data']:
            for block in curriculum_data['data']['khung_chuong_trinh']:
                for subject_group in block.get('hoc_phan_kien_thuc', []):
                    # Process mandatory courses
                    if subject_group.get('kien_thuc_bat_buoc'):
                        for course in subject_group['kien_thuc_bat_buoc']:
                            code = course.get('ma_hoc_phan', '')
                            if code:
                                course_catalog[code] = {
                                    'code': code,
                                    'name': course.get('ten_hoc_phan', ''),
                                    'credits': int(float(course.get('so_tin_chi', 0))),
                                    'semester': course.get('hoc_ky', 0),
                                    'type': 'mandatory',
                                    'prerequisites': [p['ModulesCode'] for p in course.get('detail', {}).get('relations', {}).get('prerequisite', [])],
                                    'corequisites': [c['ModulesCode'] for c in course.get('detail', {}).get('relations', {}).get('before', [])],
                                    'description': course.get('mo_ta', ''),
                                    'elective_group': None
                                }

                    # Process elective courses
                    if subject_group.get('kien_thuc_tu_chon'):
                        for elective_group in subject_group['kien_thuc_tu_chon']:
                            group_name = elective_group.get(
                                'ten_nhom_tu_chon', '')
                            if elective_group.get('danh_sach_mon_tu_chon'):
                                for course in elective_group['danh_sach_mon_tu_chon']:
                                    code = course.get('ma_hoc_phan', '')
                                    if code:
                                        course_catalog[code] = {
                                            'code': code,
                                            'name': course.get('ten_hoc_phan', ''),
                                            'credits': int(float(course.get('so_tin_chi', 0))),
                                            'semester': course.get('hoc_ky', 0),
                                            'type': 'elective',
                                            'prerequisites': [p['ModulesCode'] for p in course.get('detail', {}).get('relations', {}).get('prerequisite', [])],
                                            'corequisites': [c['ModulesCode'] for c in course.get('detail', {}).get('relations', {}).get('before', [])],
                                            'description': course.get('mo_ta', ''),
                                            'elective_group': group_name
                                        }

        return json.dumps({
            "success": True,
            "message": "Course catalog initialized successfully",
            "total_courses": len(course_catalog),
            "program": curriculum_data['data'].get('ten_nganh', 'Unknown'),
            "department": curriculum_data['data'].get('ten_khoa', 'Unknown')
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error initializing catalog: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2, ensure_ascii=False)


@mcp.tool()
def get_course_detail(
    course_identifier: str,
    completed_courses: List[str] = []
) -> str:
    """
    Get comprehensive course details with readiness assessment.

    Args:
        course_identifier: Course code (e.g., 'IT6015') or name
        completed_courses: List of completed course codes for prerequisite checking

    Returns:
        JSON string with detailed course information
    """
    if course_catalog is None:
        return json.dumps({
            "success": False,
            "error": "Catalog not initialized. Call initialize_catalog first."
        }, indent=2, ensure_ascii=False)

    try:
        # Find course (exact match or fuzzy)
        course_code = None
        if course_identifier.upper() in course_catalog:
            course_code = course_identifier.upper()
        else:
            # Fuzzy search by name
            for code, info in course_catalog.items():
                if course_identifier.lower() in info['name'].lower():
                    course_code = code
                    break

        if not course_code:
            # Return suggestions
            suggestions = []
            query_lower = course_identifier.lower()
            for code, info in list(course_catalog.items())[:10]:
                if query_lower in info['name'].lower() or query_lower in code.lower():
                    suggestions.append({
                        "code": code,
                        "name": info['name']
                    })

            return json.dumps({
                "success": False,
                "error": "Course not found",
                "suggestions": suggestions[:5]
            }, indent=2, ensure_ascii=False)

        course = course_catalog[course_code]

        # Check prerequisites
        unmet_prereqs = [p for p in course['prerequisites']
                         if p not in completed_courses]
        unmet_coreqs = [c for c in course['corequisites']
                        if c not in completed_courses]

        readiness_status = "Ready" if not unmet_prereqs and not unmet_coreqs else "Not Ready"

        # Generate bridging path if not ready
        bridging_path = []
        if unmet_prereqs:
            for prereq in unmet_prereqs:
                if prereq in course_catalog:
                    bridging_path.append({
                        "code": prereq,
                        "name": course_catalog[prereq]['name'],
                        "type": "prerequisite"
                    })

        result = {
            "success": True,
            "course_detail": {
                "code": course['code'],
                "name": course['name'],
                "credits": course['credits'],
                "semester": course['semester'],
                "type": course['type'],
                "elective_group": course['elective_group'],
                "description": course['description'],
                "prerequisites": [
                    {
                        "code": p,
                        "name": course_catalog.get(p, {}).get('name', 'Unknown'),
                        "met": p in completed_courses
                    }
                    for p in course['prerequisites']
                ],
                "corequisites": [
                    {
                        "code": c,
                        "name": course_catalog.get(c, {}).get('name', 'Unknown'),
                        "met": c in completed_courses
                    }
                    for c in course['corequisites']
                ]
            },
            "readiness": {
                "status": readiness_status,
                "unmet_prerequisites": len(unmet_prereqs),
                "unmet_corequisites": len(unmet_coreqs),
                "bridging_path": bridging_path
            },
            "next_steps": _generate_next_steps(course, unmet_prereqs, unmet_coreqs)
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error getting course detail: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2, ensure_ascii=False)


@mcp.tool()
def get_assessment_blueprint(course_code: str) -> str:
    """
    Generate assessment blueprint with recommended knowledge for exam preparation.

    Args:
        course_code: Course code (e.g., 'IT6015')

    Returns:
        JSON string with assessment blueprint including topics, weights, and difficulty
    """
    if course_catalog is None:
        return json.dumps({
            "success": False,
            "error": "Catalog not initialized. Call initialize_catalog first."
        }, indent=2, ensure_ascii=False)

    try:
        course_code = course_code.upper()

        if course_code not in course_catalog:
            return json.dumps({
                "success": False,
                "error": f"Course {course_code} not found"
            }, indent=2, ensure_ascii=False)

        course = course_catalog[course_code]

        # Generate blueprint based on course type and name
        blueprint = _generate_assessment_blueprint(course)

        result = {
            "success": True,
            "course_code": course_code,
            "course_name": course['name'],
            "assessment_blueprint": {
                "foundation_topics": [asdict(t) for t in blueprint.foundation_topics],
                "core_concepts": [asdict(t) for t in blueprint.core_concepts],
                "applied_skills": [asdict(t) for t in blueprint.applied_skills],
                "total_weight": sum(t.weight_percentage for t in blueprint.foundation_topics + blueprint.core_concepts + blueprint.applied_skills)
            },
            "readiness_checklist": blueprint.readiness_checklist,
            "estimated_prep_hours": blueprint.estimated_prep_hours,
            "study_plan": _generate_study_plan(blueprint)
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error generating assessment blueprint: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2, ensure_ascii=False)


@mcp.tool()
def search_learning_resources(
    course_code: str,
    include_web: bool = True,
    include_nonweb: bool = True,
    max_results: int = 10
) -> str:
    """
    Search and curate learning resources for a course (web and non-web).

    Args:
        course_code: Course code (e.g., 'IT6015')
        include_web: Include web resources (default: True)
        include_nonweb: Include non-web resources like PDFs, textbooks (default: True)
        max_results: Maximum number of results per category

    Returns:
        JSON string with curated learning resources
    """
    if course_catalog is None:
        return json.dumps({
            "success": False,
            "error": "Catalog not initialized. Call initialize_catalog first."
        }, indent=2, ensure_ascii=False)

    try:
        course_code = course_code.upper()

        if course_code not in course_catalog:
            return json.dumps({
                "success": False,
                "error": f"Course {course_code} not found"
            }, indent=2, ensure_ascii=False)

        course = course_catalog[course_code]

        # Generate search queries
        search_queries = [
            f"{course_code} syllabus",
            f"{course['name']} tutorial",
            f"{course['name']} lecture notes",
            f"{course_code} exam questions"
        ]

        # Simulate resource discovery (in production, integrate with real search APIs)
        web_resources = []
        nonweb_resources = []

        if include_web:
            web_resources = _generate_web_resources(course)

        if include_nonweb:
            nonweb_resources = _generate_nonweb_resources(course)

        result = {
            "success": True,
            "course_code": course_code,
            "course_name": course['name'],
            "search_queries": search_queries,
            "resources": {
                "web": [asdict(r) for r in web_resources[:max_results]],
                "non_web": [asdict(r) for r in nonweb_resources[:max_results]],
                "total_web": len(web_resources),
                "total_nonweb": len(nonweb_resources)
            },
            "quality_metrics": {
                "average_credibility": sum(r.credibility_score for r in web_resources + nonweb_resources) / max(len(web_resources) + len(nonweb_resources), 1),
                "official_sources": len([r for r in web_resources + nonweb_resources if 'official' in r.type or r.credibility_score > 0.9]),
                "recent_sources": len([r for r in web_resources + nonweb_resources if r.date and int(r.date[:4]) >= 2022])
            },
            "citation_guide": _generate_citation_guide()
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error searching learning resources: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2, ensure_ascii=False)


@mcp.tool()
def generate_course_summary_table(
    course_codes: List[str],
    completed_courses: List[str] = []
) -> str:
    """
    Generate a comprehensive summary table for multiple courses.

    Args:
        course_codes: List of course codes
        completed_courses: List of completed course codes

    Returns:
        JSON string with tabular summary of all courses
    """
    if course_catalog is None:
        return json.dumps({
            "success": False,
            "error": "Catalog not initialized. Call initialize_catalog first."
        }, indent=2, ensure_ascii=False)

    try:
        summary_rows = []

        for code in course_codes:
            code = code.upper()
            if code not in course_catalog:
                continue

            course = course_catalog[code]

            prereq_met = all(
                p in completed_courses for p in course['prerequisites'])
            coreq_met = all(
                c in completed_courses for c in course['corequisites'])

            summary_rows.append({
                "code": course['code'],
                "name": course['name'],
                "credits": course['credits'],
                "semester": course['semester'],
                "type": course['type'],
                "prerequisites": ', '.join(course['prerequisites']) if course['prerequisites'] else 'None',
                "corequisites": ', '.join(course['corequisites']) if course['corequisites'] else 'None',
                "elective_group": course['elective_group'] or 'N/A',
                "readiness": "✓ Ready" if prereq_met and coreq_met else "✗ Not Ready"
            })

        result = {
            "success": True,
            "total_courses": len(summary_rows),
            "summary_table": summary_rows,
            "statistics": {
                "total_credits": sum(row['credits'] for row in summary_rows),
                "mandatory": len([r for r in summary_rows if r['type'] == 'mandatory']),
                "elective": len([r for r in summary_rows if r['type'] == 'elective']),
                "ready": len([r for r in summary_rows if '✓' in r['readiness']]),
                "not_ready": len([r for r in summary_rows if '✗' in r['readiness']])
            }
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error generating summary table: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2, ensure_ascii=False)


# Helper functions

def _generate_next_steps(course: Dict, unmet_prereqs: List[str], unmet_coreqs: List[str]) -> List[str]:
    """Generate actionable next steps based on readiness status"""
    steps = []

    if unmet_prereqs:
        steps.append(
            f"Complete {len(unmet_prereqs)} prerequisite(s): {', '.join(unmet_prereqs[:3])}")

    if unmet_coreqs:
        steps.append(
            f"Plan to take {len(unmet_coreqs)} corequisite(s) simultaneously: {', '.join(unmet_coreqs[:3])}")

    if not unmet_prereqs and not unmet_coreqs:
        steps.append("✓ You're ready to enroll in this course")
        steps.append(f"Review assessment blueprint for {course['code']}")
        steps.append("Search for learning resources to prepare ahead")

    return steps


def _generate_assessment_blueprint(course: Dict) -> AssessmentBlueprint:
    """Generate assessment blueprint based on course characteristics"""

    # This is a template - in production, load from database or course syllabus
    course_name_lower = course['name'].lower()

    # Default blueprint
    foundation = [
        KnowledgeTopic(
            topic="Prerequisites Review",
            weight_percentage=10,
            difficulty="Easy",
            description=f"Review concepts from prerequisite courses",
            key_concepts=course['prerequisites'][:3] if course['prerequisites'] else [
                "Basic knowledge"]
        )
    ]

    core = [
        KnowledgeTopic(
            topic="Core Theory",
            weight_percentage=40,
            difficulty="Medium",
            description=f"Main theoretical concepts of {course['name']}",
            key_concepts=["Fundamental principles",
                          "Key algorithms", "Design patterns"]
        )
    ]

    applied = [
        KnowledgeTopic(
            topic="Practical Application",
            weight_percentage=50,
            difficulty="Medium-Hard",
            description="Hands-on implementation and problem-solving",
            key_concepts=["Coding exercises", "Case studies", "Project work"]
        )
    ]

    # Customize based on course type
    if "cấu trúc dữ liệu" in course_name_lower or "data structure" in course_name_lower:
        core = [
            KnowledgeTopic("Arrays & Linked Lists", 15, "Medium", "Linear data structures", [
                           "Arrays", "Linked Lists", "Iterators"]),
            KnowledgeTopic("Stacks & Queues", 10, "Easy-Medium",
                           "LIFO and FIFO structures", ["Stack operations", "Queue operations"]),
            KnowledgeTopic("Trees & Heaps", 20, "Medium-Hard", "Hierarchical structures",
                           ["Binary Trees", "BST", "Heaps", "Tree traversal"]),
            KnowledgeTopic("Graphs", 20, "Medium-Hard",
                           "Graph algorithms", ["BFS", "DFS", "Shortest path"]),
            KnowledgeTopic("Sorting & Searching", 15, "Medium", "Algorithm efficiency", [
                           "QuickSort", "MergeSort", "Binary Search"])
        ]

    checklist = [
        f"Understand all core concepts of {course['name']}",
        "Can implement key algorithms/solutions",
        "Solve practice problems within time limits",
        "Explain trade-offs and design decisions"
    ]

    prep_hours = course['credits'] * 10  # Estimate: 10 hours per credit

    return AssessmentBlueprint(
        course_code=course['code'],
        course_name=course['name'],
        foundation_topics=foundation,
        core_concepts=core,
        applied_skills=applied,
        readiness_checklist=checklist,
        estimated_prep_hours=prep_hours
    )


def _generate_study_plan(blueprint: AssessmentBlueprint) -> Dict:
    """Generate time-boxed study plan"""
    total_hours = blueprint.estimated_prep_hours

    return {
        "total_hours": total_hours,
        "weekly_breakdown": {
            "week_1-2": "Foundation topics and prerequisites review",
            "week_3-5": "Core concepts with examples and practice",
            "week_6-8": "Applied skills and project work",
            "week_9": "Comprehensive review and mock exams"
        },
        "daily_commitment": f"{total_hours // 60} hours/day for 2 months" if total_hours > 100 else f"{total_hours // 30} hours/day for 1 month"
    }


def _generate_web_resources(course: Dict) -> List[LearningSource]:
    """Generate web-based learning resources"""
    resources = [
        LearningSource(
            title=f"Official Syllabus - {course['name']}",
            type="official_doc",
            url=f"https://edu.haui.edu.vn/course/{course['code']}/syllabus",
            author="Hanoi University of Industry",
            date="2024",
            credibility_score=1.0,
            location=None,
            notes="Official course syllabus from university website"
        ),
        LearningSource(
            title=f"{course['name']} - Lecture Notes",
            type="web",
            url=f"https://scholar.google.com/scholar?q={course['code']}+lecture+notes",
            author="Various",
            date="2023-2024",
            credibility_score=0.8,
            location=None,
            notes="Academic search results for lecture materials"
        ),
        LearningSource(
            title=f"{course['name']} Tutorial",
            type="web",
            url=f"https://www.youtube.com/results?search_query={course['name']}+tutorial",
            author="Educational Channels",
            date="2024",
            credibility_score=0.7,
            location=None,
            notes="Video tutorials and explanations"
        )
    ]

    return resources


def _generate_nonweb_resources(course: Dict) -> List[LearningSource]:
    """Generate non-web learning resources"""
    resources = [
        LearningSource(
            title=f"Course Textbook - {course['name']}",
            type="textbook",
            url=None,
            author="Department recommended",
            date="Latest edition",
            credibility_score=0.95,
            location="University Library / E-library",
            notes="Official textbook recommended by the department"
        ),
        LearningSource(
            title=f"Internal Lecture Slides - {course['code']}",
            type="pdf",
            url=None,
            author="Course Instructor",
            date="Current semester",
            credibility_score=1.0,
            location="Course management system / LMS",
            notes="Instructor's lecture slides and materials"
        ),
        LearningSource(
            title=f"Past Exam Papers - {course['code']}",
            type="pdf",
            url=None,
            author="Department Archive",
            date="Previous semesters",
            credibility_score=0.9,
            location="Department office / Student portal",
            notes="Previous examination papers for practice"
        )
    ]

    return resources


def _generate_citation_guide() -> Dict:
    """Generate citation guide for resources"""
    return {
        "web_format": "[Title] — [URL] — Accessed: [Date]",
        "textbook_format": "[Author]. [Title]. [Edition]. [Publisher], [Year]. ISBN: [Number]",
        "pdf_format": "[Author]. [Title]. [Location/Repository], [Date]",
        "example_web": "Official Syllabus — https://edu.haui.edu.vn/course/IT6015 — Accessed: 2024-10-14",
        "example_textbook": "Cormen, T. H. Introduction to Algorithms. 4th ed. MIT Press, 2022. ISBN: 978-0262046305",
        "note": "Always verify source credibility and use most recent versions"
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Starting Course Detail MCP Server...")

    # Auto-initialize with default curriculum
    # initialize_catalog()

    mcp.run(transport="stdio")
