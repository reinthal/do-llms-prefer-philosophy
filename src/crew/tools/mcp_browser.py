"""
MCP Browser Tool for CrewAI agents using Playwright MCP Server.

This connects to the Playwright MCP server using CrewAI's built-in MCP adapter.
"""

from crewai_tools import MCPServerAdapter


def create_playwright_mcp_tool():
    """
    Create an MCP tool that connects to the Playwright server.

    Returns:
        MCPServerAdapter: Tool for web browsing via Playwright
    """
    return MCPServerAdapter(
        command="npx",
        args=["-y", "@playwright/mcp@latest"],
        env=None,  # Use default environment
    )
