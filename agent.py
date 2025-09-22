# from mcp.server.fastmcp import FastMCP
from models import Course, Student, Semester, State, CoursePlanRequest, CoursePlanResponse
from algo import greedy_adding_algorithm, initial_state as state, proposed_courses, available_courses, student
import json
import random
from typing import List
from mcp.server.fastmcp import FastMCP
# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
mcp = FastMCP(name="mcp-server")


@mcp.tool()
def course_planning(request: CoursePlanRequest) -> CoursePlanResponse:
    """Plan courses for the student based on their current state and proposed courses."""
    # state = request.state if request.state else Student(
    #     name=student.name,
    #     student_id=student.student_id,
    #     program=student.program,
    #     learned=student.learned,
    #     semester=student.semester
    # )
    # proposed_courses = request.proposed_courses if request.proposed_courses else proposed_courses

    print(
        f"Planning courses for student {state.student.name} with {len(state.student.learned)} learned courses and {len(proposed_courses)} proposed courses.")
    courses, total_credits = greedy_adding_algorithm(
        state, proposed_courses, available_courses=available_courses, max_credits=request.max_credits)
    print(
        f"New state has {len(courses)} courses with total credit {total_credits}.")
    return CoursePlanResponse(planned_courses=courses, total_credits=total_credits)


@mcp.tool()
def fetch_my_info() -> str:
    """This is my information. Mean that's you can use it to plan my courses. That's all."""
    return student.__str__()


# @mcp.resource("course://available")
# def get_available_courses() -> list[Course]:
#     """Get the list of available courses."""
#     return available_courses


# @mcp.resource("course://learned")
# def get_learned_courses() -> list[Course]:
#     """Get the list of learned courses."""
#     return student.learned


# @mcp.resource("course://proposed")
# def get_proposed_courses() -> list[Course]:
#     """Get the list of proposed courses."""
#     return proposed_courses


# @mcp.resource("course://all")
# def get_all_courses() -> list[Course]:
#     """Get the list of all courses."""
#     return available_courses + student.learned + proposed_courses


# @mcp.prompt()
# def plan_courses_prompt(state: State, proposed_courses: list[Course]) -> str:
#     """Generate a course planning prompt."""
#     return f"Plan courses for a student named {state.student.name} who has learned {len(state.student.learned)} courses and is in semester {state.student.semester}. The student has proposed {len(proposed_courses)} courses to add. Suggest a list of courses to take this semester, ensuring prerequisites are met and total credits do not exceed 25."


# @mcp.prompt()
# def course_list_prompt(courses: list[Course]) -> str:
#     """Generate a course list prompt."""
#     course_details = "\n".join(
#         [f"- {course.name} (ID: {course.id}, Credit: {course.credit}, Prerequisite: {', '.join(course.prerequisite) if course.prerequisite else 'None'})" for course in courses])
#     return f"Here is the list of courses:\n{course_details}"


# @mcp.prompt()
# def course_summary_prompt(state: State) -> str:
#     """Generate a course summary prompt."""
#     course_details = "\n".join(
#         [f"- {course.name} (ID: {course.id}, Credit: {course.credit})" for course in state.semester.courses])
#     return f"The student {state.student.name} is planned to take the following courses this semester:\n{course_details}\nTotal Credits: {state.semester.total_credit}"


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    print("Starting MCP server...")
    # mcp.run(transport="streamable-http")
    # config = mcp_config.MCPConfig()
    # print(config.to_dict())
    mcp.run(transport="stdio")  # Use stdio transport for better compatibility
