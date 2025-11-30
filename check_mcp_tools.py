"""Quick script to check available MCP Playwright tools."""

import os
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

# Set up MCP Playwright server
server_params = StdioServerParameters(
    command="npx",
    args=["@playwright/mcp@latest"],
    env={**os.environ, "PLAYWRIGHT_HEADLESS": "true"},
)

print("🔌 Connecting to MCP Playwright server...\n")

# Create MCP adapter
mcp_adapter = MCPServerAdapter(server_params, connect_timeout=60)
mcp_tools = mcp_adapter.tools

print(f"📋 Found {len(mcp_tools)} tools:\n")

for i, tool in enumerate(mcp_tools, 1):
    print(f"{i}. {tool.name}")
    print(f"   Description: {tool.description}")
    print()

# Clean up
mcp_adapter.stop()
print("✅ Done!")
