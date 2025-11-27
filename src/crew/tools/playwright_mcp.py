"""
Playwright MCP Tool for CrewAI agents.

This tool wraps the Playwright MCP server to provide web browsing capabilities to agents.
"""

import json
import subprocess
from typing import Any, List

from crewai_tools import BaseTool
from pydantic import Field


class PlaywrightMCPTool(BaseTool):
    """Tool for interacting with web pages via Playwright MCP server"""

    name: str = "playwright_browser"
    description: str = """
    A powerful web browsing tool that can navigate to URLs, interact with pages,
    take screenshots, and extract content from web pages.

    Available capabilities:
    - Navigate to URLs
    - Click elements
    - Fill forms
    - Extract text content
    - Take screenshots
    - Execute JavaScript

    Use this tool for any web browsing or web scraping tasks.
    """

    mcp_command: str = Field(default="npx")
    mcp_args: List[str] = Field(
        default_factory=lambda: ["-y", "@playwright/mcp@latest"]
    )

    def _run(self, action: str, **kwargs: Any) -> str:
        """
        Execute a Playwright action via MCP server.

        Args:
            action: The action to perform (e.g., 'navigate', 'screenshot', 'get_content')
            **kwargs: Action-specific parameters

        Returns:
            str: Result of the action
        """
        try:
            # Start MCP server process
            process = subprocess.Popen(
                [self.mcp_command] + self.mcp_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Send action request to MCP server
            request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": f"playwright_{action}", "arguments": kwargs},
                "id": 1,
            }

            # Send request and get response
            stdout, stderr = process.communicate(
                input=json.dumps(request) + "\n", timeout=30
            )

            if stderr:
                return f"Error: {stderr}"

            # Parse response
            response = json.loads(stdout)
            if "result" in response:
                return json.dumps(response["result"], indent=2)
            elif "error" in response:
                return f"Error: {response['error']}"
            else:
                return "No response from Playwright MCP server"

        except subprocess.TimeoutExpired:
            return "Error: Playwright operation timed out"
        except Exception as e:
            return f"Error executing Playwright action: {str(e)}"


class PlaywrightNavigateTool(BaseTool):
    """Navigate to a URL and get page content"""

    name: str = "browse_url"
    description: str = """
    Navigate to a URL and retrieve the page content.

    Input: A URL string (e.g., "https://example.com")
    Output: The text content of the page

    Use this for visiting websites and reading their content.
    """

    def _run(self, url: str) -> str:
        """Navigate to URL and return content"""
        playwright = PlaywrightMCPTool()
        return playwright._run(action="navigate", url=url)


class PlaywrightScreenshotTool(BaseTool):
    """Take a screenshot of a web page"""

    name: str = "screenshot_page"
    description: str = """
    Take a screenshot of the current web page or a specific URL.

    Input: A URL string
    Output: Path to the screenshot file or base64 image data

    Use this to capture visual information from web pages.
    """

    def _run(self, url: str) -> str:
        """Take screenshot of URL"""
        playwright = PlaywrightMCPTool()
        return playwright._run(action="screenshot", url=url)
