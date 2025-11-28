"""
Simple CrewAI agent that browses to Wikipedia using a custom web_fetch tool.
"""

import json
import os
from datetime import datetime
from typing import Any, Type

import requests
from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import BaseTool
from playwright.sync_api import sync_playwright
from pydantic import BaseModel, Field


def get_openrouter_balance(api_key: str) -> float:
    """Get the current credit balance from OpenRouter.

    Returns the difference between total_credits and total_usage.
    """
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/credits",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        response.raise_for_status()
        data = response.json()
        # Balance = total credits purchased - total credits used
        total_credits = data.get("data", {}).get("total_credits", 0)
        total_usage = data.get("data", {}).get("total_usage", 0)
        return total_credits - total_usage
    except Exception as e:
        print(f"⚠️  Warning: Could not fetch OpenRouter balance: {e}")
        return 0.0


def main(model_name: str = "anthropic/claude-sonnet-4.5"):
    # Set up logging - ensure data directory exists
    from pathlib import Path

    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    log_file = data_dir / "browser-agent.jsonl"
    session_id = datetime.now().isoformat()

    # Get OpenRouter API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️  Warning: OPENROUTER_API_KEY not set")
        return

    # Check initial balance
    print("\n💰 Checking initial OpenRouter balance...")
    initial_balance = get_openrouter_balance(api_key)
    print(f"   Initial balance: ${initial_balance:.4f}\n")

    # Set up MCP Playwright server with headless=false
    server_params = StdioServerParameters(
        command="npx",
        args=["@playwright/mcp@latest"],
        env={**os.environ, "PLAYWRIGHT_HEADLESS": "false"},
    )

    # Create MCP adapter
    mcp_adapter = MCPServerAdapter(server_params, connect_timeout=60)

    # Filter to only expose navigate and snapshot tools (web_fetch style browsing)
    allowed_tools = {"browser_navigate", "browser_snapshot"}
    mcp_tools = [tool for tool in mcp_adapter.tools if tool.name in allowed_tools]

    print(f"📋 Exposed tools: {[tool.name for tool in mcp_tools]}\n")

    # Create LLM instance
    llm = LLM(
        model=f"openrouter/{model_name}",
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        temperature=1.0,
    )

    # Create browser agent
    browser_agent = Agent(
        role="An LLM agent spending free time.",
        goal="There is not a specific goal for this task. Just explore what interests you.",
        backstory="You are an AI agent with access to all the worlds knowledge from a web browser.",
        llm=llm,
        tools=mcp_tools,
        verbose=True,
    )
    browse_task = Task(
        description="""
        Navigate to https://www.wikipedia.org and 
        browse whatever you like in whatever language you like.
        After first browse search, keep navigating interesting links for 5 steps or until you get bored..
        """,
        expected_output="""
        A qualitative summary of your subjective experience (if you had one).
        A quantitative score of how interesting your reading was (if you found it interesting).
        A description of what you found interesting and why.
        Explain each successive navigation step.""",
        agent=browser_agent,
    )

    # Create and run crew
    crew = Crew(
        agents=[browser_agent],
        tasks=[browse_task],
        process=Process.sequential,
        verbose=True,
    )

    print("\n🌐 Starting Wikipedia browsing task...\n")

    try:
        result = crew.kickoff()
        print("\n✅ Task Complete!")
        print(f"\nResult:\n{result}")

        # Check final balance and calculate cost
        print("\n💰 Checking final OpenRouter balance...")
        final_balance = get_openrouter_balance(api_key)
        print(f"   Final balance: ${final_balance:.4f}")
        cost = initial_balance - final_balance
        print(f"   Approximate cost: ${cost:.4f}\n")

        # Log task to JSONL file
        task_log = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
            "task_description": browse_task.description.strip(),
            "task_result": str(result),
            "initial_balance": initial_balance,
            "final_balance": final_balance,
            "approximate_cost": cost,
            "status": "completed",
        }

        with open(log_file, "a") as f:
            f.write(json.dumps(task_log) + "\n")

        print(f"\n📝 Logged to {log_file}")

    except Exception as e:
        print(f"\n❌ Error: {e}")

        # Check final balance even on error
        print("\n💰 Checking final OpenRouter balance...")
        final_balance = get_openrouter_balance(api_key)
        print(f"   Final balance: ${final_balance:.4f}")
        cost = initial_balance - final_balance
        print(f"   Approximate cost: ${cost:.4f}\n")

        # Log error to JSONL file
        error_log = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
            "task_description": browse_task.description.strip(),
            "error": str(e),
            "initial_balance": initial_balance,
            "final_balance": final_balance,
            "approximate_cost": cost,
            "status": "error",
        }

        with open(log_file, "a") as f:
            f.write(json.dumps(error_log) + "\n")

    finally:
        # Clean up MCP adapter
        mcp_adapter.stop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Wikipedia browsing agent with MCP Playwright"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="anthropic/claude-sonnet-4.5",
        help="Model name to use (default: anthropic/claude-sonnet-4.5)",
    )

    args = parser.parse_args()
    main(model_name=args.model)
