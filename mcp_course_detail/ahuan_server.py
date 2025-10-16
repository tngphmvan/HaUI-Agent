import sys
from mcp.server.fastmcp import FastMCP
import io

mcp = FastMCP("ahuan_server")
# Force UTF-8 encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


@mcp.tool()
def get_course_details(content: str, query: str) -> str:
    """Get comprehensive course details from the Ahuan server.

    Args:
        content (str): The content/context to send to the server.
        query (str): The query string to send to the Ahuan server.

    Returns:
        str: The response from the Ahuan server.
    """
    import requests
    import json

    url = "http://172.16.16.153:1000/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "user_id": "1",
        "session_id": "1",
        "messages": [{"role": "user", "content": content}],
        "query": query
    }

    try:
        response = requests.post(url, headers=headers,
                                 data=json.dumps(payload))
        response.raise_for_status()
        print("Ahuan server response:", response.json())
        return response.json().get("reply", "No response field in JSON.")
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Ahuan server: {e}"
