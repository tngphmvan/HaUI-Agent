"""
Test client for Course Scheduler MCP Server
Demonstrates how to use the MCP server tools
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """Test the Course Scheduler MCP Server"""

    # Server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["-u", "server.py"],
        env={"PYTHONPATH": ".."}
    )

    print("=" * 80)
    print("Testing Course Scheduler MCP Server")
    print("=" * 80)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Initialize the session
            await session.initialize()

            # List available tools
            print("\n1. Listing available tools...")
            tools = await session.list_tools()
            print(f"   Available tools: {len(tools.tools)}")
            for tool in tools.tools:
                print(f"   - {tool.name}: {tool.description[:60]}...")

            # Test 1: Initialize scheduler
            print("\n2. Initializing scheduler...")
            result = await session.call_tool(
                "initialize_scheduler",
                arguments={
                    "curriculum_file": "e:\\HaUI_Agent\\khung ctrinh cntt.json",
                    "processed_file": "e:\\HaUI_Agent\\sample.json"
                }
            )
            response = json.loads(result.content[0].text)
            print(f"   Status: {'✓' if response.get('success') else '✗'}")
            if response.get('success'):
                print(
                    f"   Total courses loaded: {response.get('total_courses')}")
            else:
                print(f"   Error: {response.get('error')}")
                return

            # Test 2: Search courses
            print("\n3. Searching for courses containing 'lập trình'...")
            result = await session.call_tool(
                "search_courses",
                arguments={
                    "query": "lập trình",
                    "max_results": 5
                }
            )
            response = json.loads(result.content[0].text)
            print(f"   Found: {response.get('results_found')} courses")
            for course in response.get('results', [])[:3]:
                print(
                    f"   - [{course['course_code']}] {course['course_name']} ({course['credits']} credits)")

            # Test 3: Get course info
            print("\n4. Getting info for course IT6015...")
            result = await session.call_tool(
                "get_course_info",
                arguments={
                    "course_identifier": "IT6015"
                }
            )
            response = json.loads(result.content[0].text)
            if response.get('success'):
                print(f"   Course: {response['course_name']}")
                print(f"   Credits: {response['credits']}")
                print(f"   Semester: {response['semester']}")
                print(
                    f"   Prerequisites: {len(response['prerequisites'])} courses")

            # Test 4: Get semester courses
            print("\n5. Getting courses for semester 3...")
            result = await session.call_tool(
                "get_semester_courses",
                arguments={
                    "semester": 3,
                    "include_electives": True
                }
            )
            response = json.loads(result.content[0].text)
            print(f"   Total courses: {response.get('total_courses')}")
            print(
                f"   Mandatory: {len(response.get('mandatory_courses', []))}")
            print(f"   Elective: {len(response.get('elective_courses', []))}")

            # Test 5: Validate prerequisites
            print("\n6. Validating prerequisites for IT6002...")
            result = await session.call_tool(
                "validate_prerequisites",
                arguments={
                    "course_code": "IT6002",
                    "completed_courses": ["IT6015", "BS6001"]
                }
            )
            response = json.loads(result.content[0].text)
            print(f"   Valid: {response.get('is_valid')}")
            print(f"   Message: {response.get('message')}")
            if not response.get('is_valid'):
                print(
                    f"   Missing: {len(response.get('missing_prerequisites', []))} prerequisites")

            # Test 6: Suggest courses
            print("\n7. Generating course suggestions...")
            completed_courses = [
                'LP6010', 'BS6018', 'BS6002', 'DC6005',
                'DC6004', 'DC6007', 'DC6006', 'IT6011',
                'IT6015', 'BS6027', 'IT6016', 'BS6001',
                'LP6011'
            ]

            result = await session.call_tool(
                "suggest_courses",
                arguments={
                    "priority_courses": ["Cấu trúc dữ liệu và giải thuật"],
                    "non_priority_courses": [],
                    "max_credits": 18,
                    "completed_courses": completed_courses,
                    "current_semester": 3
                }
            )
            response = json.loads(result.content[0].text)
            print(f"   Status: {'✓' if response.get('success') else '✗'}")
            print(
                f"   Suggestions: {len(response.get('suggestions', []))} courses")
            print(f"   Total credits: {response.get('total_credits')}")

            if response.get('suggestions'):
                print("\n   Top 5 suggested courses:")
                for i, sugg in enumerate(response['suggestions'][:5], 1):
                    print(
                        f"   {i}. [{sugg['course_code']}] {sugg['course_name']} ({sugg['credits']} credits)")
                    print(f"      Strategy: {sugg['strategy']}")
                    if sugg.get('warnings'):
                        print(f"      ⚠️  {sugg['warnings'][0]}")

            # Test 7: Calculate remaining credits
            print("\n8. Calculating remaining credits...")
            result = await session.call_tool(
                "calculate_remaining_credits",
                arguments={
                    "completed_courses": completed_courses
                }
            )
            response = json.loads(result.content[0].text)
            print(f"   Completed: {response.get('completed_credits')} credits")
            print(f"   Remaining: {response.get('remaining_credits')} credits")
            print(f"   Progress: {response.get('completion_percentage'):.1f}%")

            # Test 8: Format suggestions
            print("\n9. Formatting suggestions to readable text...")
            result = await session.call_tool(
                "format_suggestions",
                arguments={
                    "suggestions_json": json.dumps({
                        "suggestions": response.get('suggestions', [])[:3] if 'suggestions' in locals() else [],
                        "total_credits": response.get('total_credits', 0) if 'total_credits' in locals() else 0,
                        "warnings": [],
                        "errors": []
                    })
                }
            )
            formatted_text = result.content[0].text
            print(
                "\n" + formatted_text[:500] + "..." if len(formatted_text) > 500 else formatted_text)

            print("\n" + "=" * 80)
            print("All tests completed successfully!")
            print("=" * 80)


async def test_error_handling():
    """Test error handling"""

    server_params = StdioServerParameters(
        command="python",
        args=["-u", "server.py"],
        env={"PYTHONPATH": ".."}
    )

    print("\n" + "=" * 80)
    print("Testing Error Handling")
    print("=" * 80)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Test 1: Call tool without initialization
            print("\n1. Testing uninitialized scheduler...")
            result = await session.call_tool(
                "suggest_courses",
                arguments={
                    "completed_courses": [],
                    "current_semester": 1,
                    "max_credits": 20
                }
            )
            response = json.loads(result.content[0].text)
            print(f"   Expected error: {'✓' if 'error' in response else '✗'}")
            print(f"   Message: {response.get('error', 'No error')[:60]}...")

            # Initialize properly
            await session.call_tool(
                "initialize_scheduler",
                arguments={
                    "curriculum_file": "e:\\HaUI_Agent\\khung ctrinh cntt.json",
                    "processed_file": "e:\\HaUI_Agent\\sample.json"
                }
            )

            # Test 2: Invalid course code
            print("\n2. Testing invalid course code...")
            result = await session.call_tool(
                "get_course_info",
                arguments={
                    "course_identifier": "INVALID123"
                }
            )
            response = json.loads(result.content[0].text)
            print(f"   Expected error: {'✓' if 'error' in response else '✗'}")
            print(f"   Message: {response.get('error', 'No error')}")

            # Test 3: Invalid max credits
            print("\n3. Testing invalid max credits...")
            result = await session.call_tool(
                "suggest_courses",
                arguments={
                    "max_credits": 0,
                    "completed_courses": [],
                    "current_semester": 1
                }
            )
            response = json.loads(result.content[0].text)
            print(
                f"   Expected error: {'✓' if response.get('errors') else '✗'}")
            if response.get('errors'):
                print(f"   Message: {response['errors'][0]}")

            print("\n" + "=" * 80)
            print("Error handling tests completed!")
            print("=" * 80)


def main():
    """Main entry point"""
    print("\nCourse Scheduler MCP Server - Test Client")
    print("==========================================\n")

    # Run basic tests
    asyncio.run(test_mcp_server())

    # Run error handling tests
    asyncio.run(test_error_handling())


if __name__ == "__main__":
    main()
