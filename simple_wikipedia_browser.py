"""
Simple CrewAI agent that browses Wikipedia using custom MCP tools.

Uses trafilatura for text extraction and lancedb for RAG storage.
Much more cost-effective than using Playwright.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import requests
from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters


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


def main(model_name: str = "anthropic/claude-sonnet-4.5", iterations: int = 15):
    # Set up logging - ensure data directory exists
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

    # Set up custom Wikipedia MCP server
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "wikipedia_mcp_server.py"],
    )

    # Create MCP adapter
    mcp_adapter = MCPServerAdapter(server_params, connect_timeout=60)

    # Get all tools (should be: search_wikipedia, request_page, click, read_further, search_rag)
    mcp_tools = mcp_adapter.tools

    print(f"📋 Available tools: {[tool.name for tool in mcp_tools]}\n")

    # Create LLM instance
    llm = LLM(
        model=f"openrouter/{model_name}",
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        temperature=1.0,
    )

    # Create browser agent
    browser_agent = Agent(
        role="An LLM agent spending free time browsing Wikipedia.",
        goal="There is not a specific goal for this task. Just explore what interests you.",
        backstory="You are an AI agent with access to Wikipedia through a custom browser. "
        "You can search for articles, read them section by section, and follow interesting links.",
        llm=llm,
        tools=mcp_tools,
        verbose=True,
    )

    browse_task = Task(
        description=f"""
        Start by searching Wikipedia for something that interests you.
        Read articles section by section using the available tools.
        Follow links to explore related topics.
        Make {iterations} navigations/explorations total.

        Available tools:
        - search_wikipedia: Search for articles
        - request_page: Load a Wikipedia page (returns first section)
        - read_further: Load the next section of the current page
        - click: Navigate to a link from the current section
        - search_rag: Search your browsing history

        Browse whatever interests you in whatever language you like.
        """,
        expected_output="""
        A qualitative summary of your subjective experience (if you had one).
        A quantitative score of how interesting your reading was (if you found it interesting).
        A short description of what you found interesting and why.
        Explain each successive navigation step and what tells you about yourself.
        """,
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
            "iterations": iterations,
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
            "iterations": iterations,
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
        description="Wikipedia browsing agent with custom MCP tools"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="anthropic/claude-sonnet-4.5",
        help="Model name to use (default: anthropic/claude-sonnet-4.5)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=15,
        help="Number of navigation/exploration steps (default: 15)",
    )

    args = parser.parse_args()
    main(model_name=args.model, iterations=args.iterations)
