#!/usr/bin/env python3
"""Quick test of the Wikipedia MCP server tools."""

import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def test_server():
    """Test the MCP server connection and tools."""
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "wikipedia_mcp_server.py"],
    )

    print("🔌 Connecting to Wikipedia MCP server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected!\n")

            # List available tools
            print("📋 Available tools:")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()

            # Test search_wikipedia
            print("🔍 Testing search_wikipedia...")
            result = await session.call_tool("search_wikipedia", {"query": "Python programming"})
            print(f"Result: {result.content[0].text[:200]}...\n")

            # Test request_page
            print("📄 Testing request_page...")
            result = await session.call_tool(
                "request_page",
                {"url": "https://en.wikipedia.org/wiki/Python_(programming_language)"}
            )
            print(f"Result: {result.content[0].text[:300]}...\n")

            # Test read_further
            print("📖 Testing read_further...")
            result = await session.call_tool("read_further", {})
            print(f"Result: {result.content[0].text[:300]}...\n")

            print("✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_server())
