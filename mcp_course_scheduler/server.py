"""
MCP Server for Optimized Course Scheduling Suggestion System
Implements Model Context Protocol to expose course scheduling functionality
"""

import mcp.types as types
import mcp.server.stdio
from mcp.server.models import InitializationOptions
from mcp.server import Server, NotificationOptions
from course_scheduler import CourseScheduler, CourseSuggestion, StrategyType
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Optional
from inittialize import learned_course, student_semester

# Add parent directory to path to import course_scheduler
sys.path.insert(0, str(Path(__file__).parent.parent))


class CourseSchedulerMCPServer:
    """MCP Server wrapper for Course Scheduler"""

    def __init__(self):
        self.server = Server("course-scheduler")
        self.scheduler: Optional[CourseScheduler] = None
        self.curriculum_file: Optional[str] = None
        self.processed_file: Optional[str] = None

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register all MCP handlers"""

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="initialize_scheduler",
                    description="Initialize the course scheduler with curriculum data files. Must be called before using other tools.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "curriculum_file": {
                                "type": "string",
                                "description": "Absolute path to the curriculum JSON file (khung ctrinh cntt.json)"
                            },
                            "processed_file": {
                                "type": "string",
                                "description": "Absolute path to the processed curriculum JSON file (sample.json)"
                            }
                        },
                        "required": ["curriculum_file", "processed_file"]
                    }
                ),
                types.Tool(
                    name="suggest_courses",
                    description="Generate optimized course enrollment suggestions based on student's learning history, preferences, and credit constraints. Returns a list of recommended courses with reasoning.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "priority_courses": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of course names or codes the student WANTS to take this semester (optional)"
                            },
                            "non_priority_courses": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of course names or codes the student DOES NOT want to take this semester (optional)"
                            },
                            "max_credits": {
                                "type": "integer",
                                "description": "Maximum number of credits the student wants to enroll in",
                                "minimum": 11,
                                "maximum": 27,
                                "default": 20
                            },
                            "completed_courses": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of completed course codes (e.g., ['IT6015', 'BS6002'])"
                            },
                            "current_semester": {
                                "type": "integer",
                                "description": "Current semester number (1-8)",
                                "minimum": 1,
                                "maximum": 8,
                                "default": 1
                            }
                        },
                        "required": ["completed_courses", "current_semester", "max_credits"]
                    }
                ),
                types.Tool(
                    name="validate_prerequisites",
                    description="Check if a student has met the prerequisites for a specific course. Returns validation result and missing prerequisites if any.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_code": {
                                "type": "string",
                                "description": "Course code to validate (e.g., 'IT6002')"
                            },
                            "completed_courses": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of completed course codes"
                            }
                        },
                        "required": ["course_code", "completed_courses"]
                    }
                ),
                types.Tool(
                    name="get_course_info",
                    description="Get detailed information about a specific course including prerequisites, co-requisites, credits, and semester.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_identifier": {
                                "type": "string",
                                "description": "Course code (e.g., 'IT6015') or course name (e.g., 'Kỹ thuật lập trình')"
                            }
                        },
                        "required": ["course_identifier"]
                    }
                ),
                types.Tool(
                    name="search_courses",
                    description="Search for courses by name, code, or keywords. Supports fuzzy matching.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (course name or code)"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 10,
                                "minimum": 1
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="get_semester_courses",
                    description="Get all courses scheduled for a specific semester according to the curriculum framework.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "semester": {
                                "type": "integer",
                                "description": "Semester number (1-8)",
                                "minimum": 1,
                                "maximum": 8
                            },
                            "include_electives": {
                                "type": "boolean",
                                "description": "Whether to include elective courses",
                                "default": True
                            }
                        },
                        "required": ["semester"]
                    }
                ),
                types.Tool(
                    name="calculate_remaining_credits",
                    description="Calculate remaining credits needed for graduation based on completed courses.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "completed_courses": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of completed course codes"
                            }
                        },
                        "required": ["completed_courses"]
                    }
                ),
                types.Tool(
                    name="format_suggestions",
                    description="Format course suggestions into human-readable text with detailed reasoning and warnings.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "suggestions_json": {
                                "type": "string",
                                "description": "JSON string of suggestions result from suggest_courses"
                            }
                        },
                        "required": ["suggestions_json"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool calls"""

            if name == "initialize_scheduler":
                return await self._initialize_scheduler(arguments or {})

            # Check if scheduler is initialized for other tools
            if self.scheduler is None:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Scheduler not initialized. Please call initialize_scheduler first.",
                        "success": False
                    }, indent=2)
                )]

            if name == "suggest_courses":
                return await self._suggest_courses(arguments or {})
            elif name == "validate_prerequisites":
                return await self._validate_prerequisites(arguments or {})
            elif name == "get_course_info":
                return await self._get_course_info(arguments or {})
            elif name == "search_courses":
                return await self._search_courses(arguments or {})
            elif name == "get_semester_courses":
                return await self._get_semester_courses(arguments or {})
            elif name == "calculate_remaining_credits":
                return await self._calculate_remaining_credits(arguments or {})
            elif name == "format_suggestions":
                return await self._format_suggestions(arguments or {})
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _initialize_scheduler(self, arguments: dict) -> list[types.TextContent]:
        """Initialize the course scheduler"""
        try:
            curriculum_file = arguments.get(
                "curriculum_file", "E:\HaUI_Agent\khung ctrinh cntt.json")
            processed_file = arguments.get(
                "processed_file", "E:\HaUI_Agent\sample.json")

            if not curriculum_file or not processed_file:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Both curriculum_file and processed_file are required",
                        "success": False
                    }, indent=2)
                )]

            # Verify files exist
            if not Path(curriculum_file).exists():
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Curriculum file not found: {curriculum_file}",
                        "success": False
                    }, indent=2)
                )]

            if not Path(processed_file).exists():
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Processed file not found: {processed_file}",
                        "success": False
                    }, indent=2)
                )]

            self.curriculum_file = curriculum_file
            self.processed_file = processed_file
            self.scheduler = CourseScheduler(curriculum_file, processed_file)

            result = {
                "success": True,
                "message": "Course scheduler initialized successfully",
                "curriculum_file": curriculum_file,
                "processed_file": processed_file,
                "total_courses": len(self.scheduler.course_map)
            }

            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "success": False
                }, indent=2)
            )]

    async def _suggest_courses(self, arguments: dict) -> list[types.TextContent]:
        """Generate course suggestions"""
        try:
            priority_courses = arguments.get("priority_courses", [])
            non_priority_courses = arguments.get("non_priority_courses", [])
            max_credits = arguments.get("max_credits", 20)
            completed_courses = arguments.get(
                "completed_courses", learned_course)
            current_semester = arguments.get("current_semester", semester)

            result = self.scheduler.suggest_courses(
                priority_courses=priority_courses,
                non_priority_courses=non_priority_courses,
                max_credits=max_credits,
                completed_courses=completed_courses,
                current_semester=current_semester
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
                "errors": result["errors"]
            }

            return [types.TextContent(type="text", text=json.dumps(output, indent=2, ensure_ascii=False))]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "success": False
                }, indent=2)
            )]

    async def _validate_prerequisites(self, arguments: dict) -> list[types.TextContent]:
        """Validate course prerequisites"""
        try:
            course_code = arguments.get("course_code", "").upper()
            completed_courses = set(arguments.get(
                "completed_courses", learned_course))

            if course_code not in self.scheduler.course_map:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Course not found: {course_code}",
                        "success": False
                    }, indent=2)
                )]

            course = self.scheduler.course_map[course_code]
            is_valid = self.scheduler._check_prerequisites(
                course, completed_courses)

            missing_prereqs = []
            if not is_valid and course.mon_tien_quyet:
                missing_prereqs = [
                    {
                        "code": prereq,
                        "name": self.scheduler.course_map[prereq].ten_hoc_phan
                        if prereq in self.scheduler.course_map else "Unknown"
                    }
                    for prereq in course.mon_tien_quyet
                    if prereq not in completed_courses
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

            return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "success": False
                }, indent=2)
            )]

    async def _get_course_info(self, arguments: dict) -> list[types.TextContent]:
        """Get detailed course information"""
        try:
            identifier = arguments.get("course_identifier", "")

            # Try to find course by code or name
            course_code = None
            if identifier.upper() in self.scheduler.course_map:
                course_code = identifier.upper()
            else:
                # Try name mapping
                codes, _ = self.scheduler.map_course_names_to_codes([
                                                                    identifier])
                if codes:
                    course_code = codes[0]

            if not course_code:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Course not found: {identifier}",
                        "success": False
                    }, indent=2)
                )]

            course = self.scheduler.course_map[course_code]

            prereq_details = [
                {
                    "code": prereq,
                    "name": self.scheduler.course_map[prereq].ten_hoc_phan
                    if prereq in self.scheduler.course_map else "Unknown"
                }
                for prereq in course.mon_tien_quyet
            ]

            coreq_details = [
                {
                    "code": coreq,
                    "name": self.scheduler.course_map[coreq].ten_hoc_phan
                    if coreq in self.scheduler.course_map else "Unknown"
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

            return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "success": False
                }, indent=2)
            )]

    async def _search_courses(self, arguments: dict) -> list[types.TextContent]:
        """Search for courses"""
        try:
            query = arguments.get("query", "").lower()
            max_results = arguments.get("max_results", 10)

            results = []
            for code, course in self.scheduler.course_map.items():
                if (query in course.ten_hoc_phan.lower() or
                        query in code.lower()):
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

            return [types.TextContent(type="text", text=json.dumps(output, indent=2, ensure_ascii=False))]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "success": False
                }, indent=2)
            )]

    async def _get_semester_courses(self, arguments: dict) -> list[types.TextContent]:
        """Get courses for a specific semester"""
        try:
            semester = arguments.get("semester", 1)
            include_electives = arguments.get("include_electives", True)

            courses = []
            for code, course in self.scheduler.course_map.items():
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

            return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "success": False
                }, indent=2)
            )]

    async def _calculate_remaining_credits(self, arguments: dict) -> list[types.TextContent]:
        """Calculate remaining credits for graduation"""
        try:
            completed_courses = arguments.get(
                "completed_courses", learned_course)

            completed_credits = sum(
                self.scheduler.course_map[code].so_tin_chi
                for code in completed_courses
                if code in self.scheduler.course_map
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
                "courses_completed": len([c for c in completed_courses if c in self.scheduler.course_map])
            }

            return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "success": False
                }, indent=2)
            )]

    async def _format_suggestions(self, arguments: dict) -> list[types.TextContent]:
        """Format suggestions to human-readable text"""
        try:
            suggestions_json = arguments.get("suggestions_json", "{}")
            result_data = json.loads(suggestions_json)

            # Reconstruct result with CourseSuggestion objects for formatting
            suggestions = []
            for sugg_data in result_data.get("suggestions", []):
                strategy = StrategyType(sugg_data["strategy"])
                suggestion = CourseSuggestion(
                    ma_hoc_phan=sugg_data["course_code"],
                    ten_hoc_phan=sugg_data["course_name"],
                    so_tin_chi=sugg_data["credits"],
                    reason=sugg_data["reason"],
                    strategy=strategy,
                    warnings=sugg_data["warnings"],
                    is_auto_included=sugg_data.get("is_auto_included", False)
                )
                suggestions.append(suggestion)

            result = {
                "suggestions": suggestions,
                "total_credits": result_data.get("total_credits", 0),
                "warnings": result_data.get("warnings", []),
                "errors": result_data.get("errors", [])
            }

            formatted = self.scheduler.format_suggestions(result)

            return [types.TextContent(type="text", text=formatted)]

        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "success": False
                }, indent=2)
            )]

    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="course-scheduler",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


async def main():
    """Main entry point"""
    server = CourseSchedulerMCPServer()
    await server._initialize_scheduler(arguments={
        "curriculum_file": "E:\HaUI_Agent\khung ctrinh cntt.json",
        "processed_file": "E:\HaUI_Agent\sample.json"
    })
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
