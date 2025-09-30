# from mcp.server.fastmcp import FastMCP
from models import Course, Student, Semester, State, CoursePlanRequest, CoursePlanResponse
from algo import greedy_adding_algorithm, initial_state, student, course_mapping, total_course
import json
import random
from typing import List
from mcp.server.fastmcp import FastMCP
import logging
import copy
# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
mcp = FastMCP(name="mcp-server")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# @mcp.tool()
# def check_course_validity(course_ids: List[str]) -> str:
#     """Check if the proposed courses are valid for the student."""
#     proposed_courses = [course_mapping(course_id, total_course)
#                         for course_id in course_ids]
#     available_courses = [
#         course for course in total_course if course not in initial_state.student.learned and course.before == [] and course.prerequisite == []]
#     for course in proposed_courses:
#         if course not in available_courses:
#             return f"Course {course.id} is not available."
#     return "All proposed courses are valid."

@mcp.tool()
def check_course_validity(course_ids: List[str]) -> str:
    """Check if the proposed courses are valid for the student."""
    proposed_courses = []
    invalid_courses = []
    not_found_courses = []
    for course_id in course_ids:
        course = course_mapping(course_id, total_course)
        if course is None:
            not_found_courses.append(course_id)
        proposed_courses.append(course)
    if not_found_courses:
        return f"Courses not found: {', '.join(not_found_courses)}"
    for course in proposed_courses:
        # Kiểm tra prerequisite
        for pre in course.prerequisite:
            if pre['ModulesCode'] not in [c.id for c in initial_state.student.learned]:
                invalid_courses.append(
                    f"Course {course.id} requires prerequisite {pre}.")
        # Kiểm tra before
        for bef in course.before:
            if bef['ModulesCode'] not in [c.id for c in initial_state.student.learned]:
                invalid_courses.append(
                    f"Course {course.id} requires to complete {bef} before.")
    if invalid_courses:
        return '\n'.join(invalid_courses)

    return "All proposed courses are valid."


@mcp.tool()
def course_planning(proposed_courses: list[str], max_credits: int) -> CoursePlanResponse | str:
    """Plan courses for the student based on their current state and proposed courses.

    Args:
        proposed_courses (list[str]): List of proposed course IDs, if user not specified, it will be empty list.
        max_credits (int): Maximum credits allowed for the semester.

    Returns:
        CoursePlanResponse | str: Response containing planned courses and total credits or an error message.
    """
    # state = request.state if request.state else Student(
    #     name=student.name,
    #     student_id=student.student_id,
    #     program=student.program,
    #     learned=student.learned,
    #     semester=student.semester
    # )
    # proposed_courses = request.proposed_courses if request.proposed_courses else proposed_courses
    state = copy.deepcopy(initial_state)  # Luôn tạo state mới
    proposed_courses_processed = [course_mapping(course_id, total_course)
                                  for course_id in proposed_courses]
    # logger.debug(f"Request received: {request}")
    logger.debug(f"Total courses in the program: {len(total_course)}")
    logger.debug(
        f"Proposed courses: {[course.id for course in proposed_courses_processed]}")
    max_credits = int(max_credits)
    # logger.debug(f"Request received: {request}")
    # logger.debug(f"State: {state}")
    # logger.debug(f"Proposed courses: {proposed_courses}")
    logger.debug(f"Max credits: {max_credits}")
    available_courses = []
    logger.debug(
        f"Student learned courses: {[course.id for course in initial_state.student.learned]}")
    logger.debug(f"Total courses: {[course.id for course in total_course]}")
    for course in total_course:
        if course not in initial_state.student.learned:
            # Kiểm tra prerequisite
            prerequisites_met = all(
                pre['ModulesCode'] in [c.id for c in initial_state.student.learned] for pre in course.prerequisite)
            # Kiểm tra before
            before_met = all(
                bef['ModulesCode'] in [c.id for c in initial_state.student.learned] for bef in course.before)
            if prerequisites_met and before_met:
                available_courses.append(course)
    logger.debug(
        f"Available courses: {[course.id for course in available_courses]}")
    logger.debug(
        f"Available courses after filtering: {len(available_courses)}")
    courses, total_credits = greedy_adding_algorithm(
        state, proposed_courses_processed, available_courses, max_credits)
    print(
        f"Planning courses for student {state.student.name} with {len(state.student.learned)} learned courses and {len(proposed_courses_processed)} proposed courses.")
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

    logging.basicConfig(level=logging.DEBUG)
    print("Starting MCP server...")
    # mcp.run(transport="streamable-http")
    # config = mcp_config.MCPConfig()
    # print(config.to_dict())
    mcp.run(transport="stdio")  # Use stdio transport for better compatibility
