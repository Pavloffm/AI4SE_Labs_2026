# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp==1.30.0"]
# ///
"""A local MCP server exposing exactly one arithmetic tool."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Task 7 Calculator")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers and return their sum."""
    return a + b


if __name__ == "__main__":
    mcp.run(transport="stdio")
