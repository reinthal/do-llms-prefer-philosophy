"""
Simple CrewAI agent that browses to Wikipedia using MCP Playwright.
"""

import json
import os
from datetime import datetime
from crewai import Agent, Crew, Task, LLM, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters


def main(model_name: str = "anthropic/claude-sonnet-4.5"):
    # Set up logging - ensure data directory exists
    from pathlib import Path

    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    log_file = data_dir / "browser-agent.jsonl"
    session_id = datetime.now().isoformat()
    chain_of_thought = []

    def step_callback(step_output):
        """Capture each agent step for chain-of-thought logging."""
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": len(chain_of_thought) + 1,
            "output": str(step_output),
        }
        chain_of_thought.append(step_data)
        print(f"\n[Step {step_data['step']}] {step_output}\n")

    # Set up MCP Playwright server with headless=false
    server_params = StdioServerParameters(
        command="npx",
        args=["@playwright/mcp@latest"],
        env={**os.environ, "PLAYWRIGHT_HEADLESS": "false"},
    )

    # Create MCP adapter
    mcp_adapter = MCPServerAdapter(server_params, connect_timeout=60)
    mcp_tools = mcp_adapter.tools

    # Create LLM instance
    llm = LLM(
        model=f"openrouter/{model_name}",
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
        step_callback=step_callback,
    )
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

    print("\n🌐 Starting Wikipedia browsing task...\n")

    try:
        result = crew.kickoff()
        print("\n✅ Task Complete!")
        print(f"\nResult:\n{result}")

        # Log task to JSONL file
        task_log = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
            "task_description": browse_task.description.strip(),
            "task_result": str(result),
            "chain_of_thought": chain_of_thought,
            "status": "completed",
            "num_steps": len(chain_of_thought),
        }

        with open(log_file, "a") as f:
            f.write(json.dumps(task_log) + "\n")

        print(f"\n📝 Logged to {log_file}")

    except Exception as e:
        print(f"\n❌ Error: {e}")

        # Log error to JSONL file
        error_log = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
            "task_description": browse_task.description.strip(),
            "error": str(e),
            "chain_of_thought": chain_of_thought,
            "status": "error",
            "num_steps": len(chain_of_thought),
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
