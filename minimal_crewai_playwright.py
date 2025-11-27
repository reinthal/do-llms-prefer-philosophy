"""
Minimal CrewAI agent that browses Wikipedia using MCP Playwright.
"""

import os

from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters


def main():
    # Set up MCP Playwright server
    server_params = StdioServerParameters(
        command="npx",
        args=["@playwright/mcp@latest"],
        env={**os.environ, "PLAYWRIGHT_HEADLESS": "true"},  # Run headless for testing
    )

    # Create MCP adapter and get tools
    mcp_adapter = MCPServerAdapter(server_params, connect_timeout=60)
    mcp_tools = mcp_adapter.tools

    # Create LLM instance
    llm = LLM(
        model="openrouter/anthropic/claude-sonnet-4.5",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=1.0,
    )

    # Create browser agent
    browser_agent = Agent(
        role="Web Browser Agent",
        goal="Browse to Wikipedia and explore interesting content",
        backstory="You are an AI agent with web browsing capabilities",
        llm=llm,
        tools=mcp_tools,
        verbose=True,
    )

    # Create browsing task
    browse_task = Task(
        description="Navigate to https://www.wikipedia.org and click on an interesting article",
        expected_output="A summary of what you found",
        agent=browser_agent,
    )

    # Create and run crew
    crew = Crew(
        agents=[browser_agent],
        tasks=[browse_task],
        process=Process.sequential,
        verbose=True,
    )

    try:
        print("\n🌐 Starting Wikipedia browsing...\n")
        result = crew.kickoff()
        print(f"\n✅ Complete!\n\nResult: {result}\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        mcp_adapter.stop()


if __name__ == "__main__":
    main()
