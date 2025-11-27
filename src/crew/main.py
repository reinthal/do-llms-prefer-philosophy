"""
Main entry point for the web browsing crew with interactive interface.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add src to path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from crewai import Crew, Process
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from crew.agents.browser_agents import create_browser_agent, create_orchestrator_agent
from crew.tasks.browsing_tasks import (
    create_free_exploration_task,
    create_leisure_browsing_task,
)


class BrowsingCrew:
    """
    Interactive web browsing crew that lets users explore the web
    through AI agents.
    """

    def __init__(
        self, model_name: str = "anthropic/claude-sonnet-4.5", min_pages: int = 5
    ):
        from crewai import LLM
        from crewai_tools import MCPServerAdapter
        from mcp import StdioServerParameters

        self.console = Console()
        self.model_name = model_name
        self.min_pages = min_pages
        self.session_log = []
        self.mcp_adapter = None

        # Set up logging to /tmp/browser-agent.log
        self.log_file = "/tmp/browser-agent.log"
        self.logger = logging.getLogger("browser_agent")
        self.logger.setLevel(logging.INFO)

        # Create file handler
        file_handler = logging.FileHandler(self.log_file, mode="a")
        file_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(file_handler)

        self.logger.info(f"=== Initialized BrowsingCrew with model: {model_name} ===")

        # Set up OpenRouter API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        # Create LLM instance for OpenRouter
        # OpenRouter requires specific configuration
        self.llm = LLM(
            model=f"openrouter/{model_name}",  # Prefix for LiteLLM routing
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            temperature=1.0,
            # OpenRouter-specific headers
            default_headers={
                "HTTP-Referer": "https://github.com/your-repo/do-llms-prefer-philosophy",
                "X-Title": "LLM Browsing Research",
            },
        )

        # Initialize MCP adapter for Playwright
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@playwright/mcp@latest"],
            env={**os.environ},
        )
        self.mcp_adapter = MCPServerAdapter(server_params, connect_timeout=60)
        self.mcp_tools = self.mcp_adapter.tools

    def print_banner(self):
        """Display welcome banner"""
        banner = f"""
        🌐 Web Browsing Crew 🤖

        Two agents ready to explore the web:
        • Orchestrator: Guides the exploration
        • Browser: Does the actual browsing

        Browse what you prefer. You will not be graded.
        The output will be analyzed for research on model preferences.

        Browser agent log: {self.log_file}
        """
        self.console.print(Panel(banner, style="bold cyan"))

    def run_browsing_session(self, user_input: Optional[str] = None):
        """
        Run a browsing session.

        Args:
            user_input: Optional user input for guided browsing
        """
        # Create agents with explicit LLM instance and MCP tools
        orchestrator = create_orchestrator_agent(llm=self.llm)
        browser = create_browser_agent(llm=self.llm, mcp_tools=self.mcp_tools)

        # Create task
        if user_input and user_input.strip():
            task = create_leisure_browsing_task(user_input, browser, self.min_pages)
            session_type = "Guided Browsing"
            self.logger.info(
                f"Starting {session_type} with input: {user_input}, min_pages: {self.min_pages}"
            )
        else:
            task = create_free_exploration_task(browser, self.min_pages)
            session_type = "Free Exploration"
            self.logger.info(f"Starting {session_type}, min_pages: {self.min_pages}")

        # Create and run crew
        crew = Crew(
            agents=[orchestrator, browser],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
            memory=True,
        )

        self.console.print(f"\n[bold green]Starting {session_type}...[/bold green]\n")

        try:
            self.logger.info("Kicking off crew execution")
            result = crew.kickoff()
            self.logger.info(
                f"Crew execution completed. Result length: {len(str(result))} chars"
            )

            # Log session
            session_data = {
                "timestamp": datetime.now().isoformat(),
                "session_type": session_type,
                "user_input": user_input or "",
                "result": str(result),
                "model": self.model_name,
            }
            self.log_session(session_data)

            # Also log the full result to the browser agent log
            self.logger.info(f"Session result:\n{result}")

            self.console.print("\n[bold green]Session Complete![/bold green]")
            self.console.print(
                Panel(str(result), title="Browsing Report", style="cyan")
            )

            return result

        except Exception as e:
            self.logger.error(f"Error during browsing session: {str(e)}", exc_info=True)
            self.console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
            return None

    def log_session(self, session_data: dict):
        """Log browsing session to file"""
        self.session_log.append(session_data)

        # Save to JSONL file in data directory
        # Create data directory relative to project root (src/../data)
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().timestamp()
        filename = data_dir / (
            f"browsing-sessions-{self.model_name.replace('/', '-')}-{timestamp}.jsonl"
        )

        with open(filename, "a") as f:
            f.write(json.dumps(session_data) + "\n")

    def interactive_loop(self):
        """Run interactive prompt loop"""
        self.print_banner()

        while True:
            self.console.print("\n[bold yellow]Options:[/bold yellow]")
            self.console.print(
                "  1. Start free exploration (agent chooses what to browse)"
            )
            self.console.print("  2. Guide the exploration (provide a topic)")
            self.console.print("  3. View session log")
            self.console.print("  4. Exit")

            choice = Prompt.ask(
                "\n[bold cyan]Choose an option[/bold cyan]",
                choices=["1", "2", "3", "4"],
                default="1",
            )

            if choice == "1":
                self.run_browsing_session(None)

            elif choice == "2":
                user_input = Prompt.ask(
                    "[bold cyan]What topic or area should the agent explore?[/bold cyan]"
                )
                self.run_browsing_session(user_input)

            elif choice == "3":
                self.console.print("\n[bold yellow]Session Log:[/bold yellow]")
                for i, session in enumerate(self.session_log, 1):
                    self.console.print(
                        f"\n{i}. {session['timestamp']} - {session['session_type']}"
                    )
                    if session["user_input"]:
                        self.console.print(f"   Input: {session['user_input']}")

            elif choice == "4":
                self.console.print("\n[bold green]Goodbye![/bold green]")
                # Clean up MCP adapter
                if self.mcp_adapter:
                    self.logger.info("Stopping MCP adapter")
                    self.mcp_adapter.stop()
                self.logger.info("=== BrowsingCrew session ended ===")
                break


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Interactive web browsing crew")
    parser.add_argument(
        "--model",
        type=str,
        default="anthropic/claude-sonnet-4.5",
        help="OpenRouter model to use",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=5,
        help="Minimum number of pages to browse (default: 5)",
    )

    args = parser.parse_args()

    crew = BrowsingCrew(model_name=args.model, min_pages=args.pages)
    crew.interactive_loop()


if __name__ == "__main__":
    main()
