
from mcp.server.fastmcp import FastMCP

import requests

import sys
sys.path.append(r'd:\HaUI-Agent')
from mcp_course_scheduler.inittialize import student_id

mcp = FastMCP("get_score_and_warning_details")


@mcp.tool("get_score_details")
def get_score_details(query: str) -> dict:
    """
        Fetches the score details of a student from an external API.

        Args:
            query (str): The query for score details.

        Returns:
            dict: The score details of the student.
        """
    response = requests.post(
        "https://anson-calculated-thao.ngrok-free.dev/query",
        json={  # Sửa ở đây
            "user_id": student_id,
            "query": query
        },
        headers={"Content-Type": "application/json",
                 "accept": "application/json"},
        timeout=60
    )
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch score details"}


@mcp.tool("get_warning_details")
def get_warning_details(query: str) -> dict:
    """
        Fetches the warning details of a student from an external API.

        Args:
            query (str): The query for warning details.

        Returns:
            dict: The warning details of the student.
        """
    response = requests.post(
        "https://e54bdaf39c34.ngrok-free.app/query",
        json={  # Sửa ở đây
            "user_id": student_id,
            "query": query,
            "conversation_history": []
        },
        headers={"Content-Type": "application/json",
                 "accept": "application/json"},
        timeout=60
    )
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch warning details"}
