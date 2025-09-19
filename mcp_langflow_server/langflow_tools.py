from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from langflow import Langflow, Flow
import json


class LangflowTools:
    def __init__(self, langflow: Langflow):
        self.langflow = langflow

    def list_components(self) -> str:
        """List all available Langflow components."""
        components = self.langflow.list_components()
        return json.dumps(components, indent=2)

    def create_flow(self, flow_data: Dict[str, Any]) -> str:
        """Create a new Langflow flow from JSON data."""
        try:
            flow = self.langflow.create_flow(flow_data)
            return f"Flow created successfully with ID: {flow.id}"
        except Exception as e:
            return f"Error creating flow: {str(e)}"

    def run_flow(self, flow_id: str, inputs: Dict[str, Any]) -> str:
        """Run a specific Langflow flow."""
        try:
            result = self.langflow.run_flow(flow_id, inputs)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error running flow: {str(e)}"

    def get_flow(self, flow_id: str) -> str:
        """Get details of a specific Langflow flow."""
        try:
            flow = self.langflow.get_flow(flow_id)
            return json.dumps(flow.dict(), indent=2)
        except Exception as e:
            return f"Error retrieving flow: {str(e)}"

    def update_flow(self, flow_id: str, flow_data: Dict[str, Any]) -> str:
        """Update an existing Langflow flow."""
        try:
            updated_flow = self.langflow.update_flow(flow_id, flow_data)
            return f"Flow updated successfully: {updated_flow.id}"
        except Exception as e:
            return f"Error updating flow: {str(e)}"

    def delete_flow(self, flow_id: str) -> str:
        """Delete a specific Langflow flow."""
        try:
            self.langflow.delete_flow(flow_id)
            return f"Flow {flow_id} deleted successfully"
        except Exception as e:
            return f"Error deleting flow: {str(e)}"

    def list_flows(self) -> str:
        """List all available flows."""
        try:
            flows = self.langflow.list_flows()
            return json.dumps([flow.dict() for flow in flows], indent=2)
        except Exception as e:
            return f"Error listing flows: {str(e)}"
