import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_langflow_server():
    # Server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    # Connect to server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize session
            await session.initialize()

            # List available tools
            tools_response = await session.list_tools()
            print("\nAvailable tools:")
            for tool in tools_response.tools:
                print(f"- {tool.name}: {tool.description}")

            # Test list_components
            print("\nTesting list_components:")
            result = await session.call_tool("list_components")
            print(result.content)

            # Test creating a flow
            print("\nTesting create_flow:")
            flow_data = {
                "name": "Test Flow",
                "description": "A test flow",
                "nodes": []
            }
            result = await session.call_tool("create_flow", {"flow_data": flow_data})
            print(result.content)

if __name__ == "__main__":
    asyncio.run(test_langflow_server())
