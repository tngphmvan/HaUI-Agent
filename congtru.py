from pydantic import BaseModel
from fastmcp import FastMCP, mcp_config

mcp = FastMCP("BaseModelDemo")

# Định nghĩa input bằng BaseModel


class CalculatorInput(BaseModel):
    a: int
    b: int

# Định nghĩa output cũng có thể dùng BaseModel


class CalculatorOutput(BaseModel):
    result: int
    message: str


@mcp.tool()
def add_numbers(data: CalculatorInput) -> CalculatorOutput:
    """Cộng 2 số với input/output được validate bằng BaseModel."""
    result = data.a + data.b
    return CalculatorOutput(result=result, message=f"{data.a} + {data.b} = {result}")


if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run("stdio")
