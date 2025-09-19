from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from langflow import Langflow
from langflow_tools import LangflowTools


class LangflowMCPServer:
    def __init__(self):
        # Initialize FastMCP server
        self.mcp = FastMCP("langflow-mcp-server")
        self.langflow = Langflow()
        self.tools = LangflowTools(self.langflow)

        # Register tools
        self.register_tools()

    def register_tools(self):
        @self.mcp.tool("list_components")
        def list_components() -> str:
            return self.tools.list_components()

        @self.mcp.tool("create_flow")
        def create_flow(flow_data: Dict[str, Any]) -> str:
            return self.tools.create_flow(flow_data)

        @self.mcp.tool("run_flow")
        def run_flow(flow_id: str, inputs: Dict[str, Any]) -> str:
            return self.tools.run_flow(flow_id, inputs)

        @self.mcp.tool("get_flow")
        def get_flow(flow_id: str) -> str:
            return self.tools.get_flow(flow_id)

        @self.mcp.tool("update_flow")
        def update_flow(flow_id: str, flow_data: Dict[str, Any]) -> str:
            return self.tools.update_flow(flow_id, flow_data)

        @self.mcp.tool("delete_flow")
        def delete_flow(flow_id: str) -> str:
            return self.tools.delete_flow(flow_id)

        @self.mcp.tool("list_flows")
        def list_flows() -> str:
            return self.tools.list_flows()

    def run(self):
        """Start the MCP server."""
        self.mcp.run(transport='stdio')


if __name__ == "__main__":
    server = LangflowMCPServer()
    server.run()
