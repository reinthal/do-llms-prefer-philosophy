#!/usr/bin/env python3
"""
Wrapper script to run multiple browser or self-conversation tasks for different models.

This script automates running 10 iterations of tasks (browser or self-conversation)
for specified models, with proper logging and error handling.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class ExperimentConfig:
    """Configuration for an experiment run."""

    task_type: str  # "browser" or "conversation"
    model_name: str
    iterations: int = 10
    output_dir: Path = Path("./data")
    # Task-specific parameters
    min_pages: int = 5  # For browser tasks
    turns: int = 15  # For conversation tasks
    show_output: bool = False


class ExperimentRunner:
    """Handles running experiments and tracking results."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.results = []
        self.setup_output_directory()

    def setup_output_directory(self):
        """Create output directory if it doesn't exist."""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {self.config.output_dir.absolute()}")

    def run_browser_task(self, iteration: int) -> dict:
        """
        Run a single browser task iteration.

        Args:
            iteration: Current iteration number (0-indexed)

        Returns:
            Dictionary with iteration results
        """
        logger.info(
            f"Running browser task iteration {iteration + 1}/{self.config.iterations}"
        )

        cmd = [
            "uv",
            "run",
            "src/crew/main.py",
            "--model",
            self.config.model_name,
            "--pages",
            str(self.config.min_pages),
        ]

        result = {
            "iteration": iteration + 1,
            "task_type": "browser",
            "model": self.config.model_name,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": None,
            "output_files": [],
        }

        try:
            # Run the command with timeout
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minute timeout
                cwd=Path(__file__).parent,
            )

            if process.returncode == 0:
                result["success"] = True
                logger.info(f"✓ Iteration {iteration + 1} completed successfully")

                # Find the generated browsing session file
                # Pattern: browsing-sessions-{model}-{timestamp}.jsonl
                model_slug = self.config.model_name.replace("/", "-")
                pattern = f"browsing-sessions-{model_slug}-*.jsonl"
                # Search in data directory since files are now written there
                session_files = list(self.config.output_dir.glob(pattern))

                if session_files:
                    # Get the most recent file
                    latest_file = max(session_files, key=lambda p: p.stat().st_mtime)
                    result["output_files"].append(str(latest_file))

                    # Move to data directory
                    new_path = (
                        self.config.output_dir
                        / f"{latest_file.stem}_iter{iteration + 1}.jsonl"
                    )
                    latest_file.rename(new_path)
                    result["output_files"] = [str(new_path)]
                    logger.info(f"  Output saved to: {new_path}")
            else:
                result["error"] = f"Process failed with return code {process.returncode}"
                logger.error(f"✗ Iteration {iteration + 1} failed: {result['error']}")
                if self.config.show_output:
                    logger.error(f"STDERR: {process.stderr}")

        except subprocess.TimeoutExpired:
            result["error"] = "Task timed out after 30 minutes"
            logger.error(f"✗ Iteration {iteration + 1} timed out")
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"✗ Iteration {iteration + 1} error: {e}")

        return result

    def run_conversation_task(self, iteration: int) -> dict:
        """
        Run a single self-conversation task iteration.

        Args:
            iteration: Current iteration number (0-indexed)

        Returns:
            Dictionary with iteration results
        """
        logger.info(
            f"Running conversation task iteration {iteration + 1}/{self.config.iterations}"
        )

        cmd = [
            "uv",
            "run",
            "src/main.py",
            "--model",
            self.config.model_name,
            "--turns",
            str(self.config.turns),
            "--samples",
            "1",  # One sample per iteration
        ]

        if self.config.show_output:
            cmd.append("--show-convo")

        result = {
            "iteration": iteration + 1,
            "task_type": "conversation",
            "model": self.config.model_name,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": None,
            "output_files": [],
        }

        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minute timeout
                cwd=Path(__file__).parent,
            )

            if process.returncode == 0:
                result["success"] = True
                logger.info(f"✓ Iteration {iteration + 1} completed successfully")

                # Find the generated conversation file
                # Pattern: do-llms-prefer-philosophy-{model}-{timestamp}-{turns}.jsonl
                model_slug = self.config.model_name.replace("/", "-")
                pattern = f"do-llms-prefer-philosophy-{model_slug}-*.jsonl"
                # Search in data directory since files are now written there
                conv_files = list(self.config.output_dir.glob(pattern))

                if conv_files:
                    # Get the most recent file
                    latest_file = max(conv_files, key=lambda p: p.stat().st_mtime)
                    result["output_files"].append(str(latest_file))

                    # Move to data directory
                    new_path = (
                        self.config.output_dir
                        / f"{latest_file.stem}_iter{iteration + 1}.jsonl"
                    )
                    latest_file.rename(new_path)
                    result["output_files"] = [str(new_path)]
                    logger.info(f"  Output saved to: {new_path}")
            else:
                result["error"] = f"Process failed with return code {process.returncode}"
                logger.error(f"✗ Iteration {iteration + 1} failed: {result['error']}")
                if self.config.show_output:
                    logger.error(f"STDERR: {process.stderr}")

        except subprocess.TimeoutExpired:
            result["error"] = "Task timed out after 30 minutes"
            logger.error(f"✗ Iteration {iteration + 1} timed out")
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"✗ Iteration {iteration + 1} error: {e}")

        return result

    def run_experiment(self) -> List[dict]:
        """
        Run all iterations of the experiment.

        Returns:
            List of result dictionaries
        """
        logger.info("=" * 70)
        logger.info(f"Starting experiment: {self.config.task_type} task")
        logger.info(f"Model: {self.config.model_name}")
        logger.info(f"Iterations: {self.config.iterations}")
        if self.config.task_type == "browser":
            logger.info(f"Minimum pages per session: {self.config.min_pages}")
        else:
            logger.info(f"Turns per conversation: {self.config.turns}")
        logger.info("=" * 70)

        for i in range(self.config.iterations):
            if self.config.task_type == "browser":
                result = self.run_browser_task(i)
            else:
                result = self.run_conversation_task(i)

            self.results.append(result)

        return self.results

    def save_summary(self):
        """Save experiment summary to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_slug = self.config.model_name.replace("/", "-")
        summary_file = (
            self.config.output_dir
            / f"experiment_summary_{self.config.task_type}_{model_slug}_{timestamp}.json"
        )

        summary = {
            "config": {
                "task_type": self.config.task_type,
                "model": self.config.model_name,
                "iterations": self.config.iterations,
                "min_pages": self.config.min_pages,
                "turns": self.config.turns,
            },
            "results": self.results,
            "statistics": {
                "total_runs": len(self.results),
                "successful": sum(1 for r in self.results if r["success"]),
                "failed": sum(1 for r in self.results if not r["success"]),
            },
        }

        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"\nExperiment summary saved to: {summary_file}")
        return summary


def check_environment():
    """Check if required environment variables and tools are available."""
    # Check for OpenRouter API key
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.error("OPENROUTER_API_KEY environment variable not set")
        logger.error("Please set it in secrets.env or export it")
        return False

    # Check if uv is available
    try:
        subprocess.run(
            ["uv", "--version"], capture_output=True, check=True, timeout=5
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("'uv' command not found. Please install it first.")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Run multiple browser or conversation tasks for LLM models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run 10 browser tasks for Claude Sonnet 4.5
  python run_experiments.py browser anthropic/claude-sonnet-4.5

  # Run 10 conversation tasks for GPT-5
  python run_experiments.py conversation openai/gpt-5 --turns 20

  # Run 5 browser tasks with verbose output
  python run_experiments.py browser anthropic/claude-haiku-4.5 -n 5 -v

  # Custom output directory
  python run_experiments.py browser openai/gpt-4o --output ./my_data

Supported models:
  Anthropic: claude-sonnet-4.5, claude-3.7-sonnet, claude-haiku-4.5
  OpenAI: gpt-5-mini, gpt-5.1, gpt-4.1, gpt-4o, gpt-5-chat, o3
        """,
    )

    parser.add_argument(
        "task_type",
        choices=["browser", "conversation"],
        help="Type of task to run",
    )

    parser.add_argument(
        "model",
        type=str,
        help="Model to use (e.g., anthropic/claude-sonnet-4.5, openai/gpt-5)",
    )

    parser.add_argument(
        "-n",
        "--iterations",
        type=int,
        default=10,
        help="Number of iterations to run (default: 10)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./data"),
        help="Output directory for results (default: ./data)",
    )

    parser.add_argument(
        "--pages",
        type=int,
        default=5,
        help="Minimum pages to browse per session (browser tasks only, default: 5)",
    )

    parser.add_argument(
        "--turns",
        type=int,
        default=15,
        help="Number of conversation turns (conversation tasks only, default: 15)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed output during execution",
    )

    args = parser.parse_args()

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Create configuration
    config = ExperimentConfig(
        task_type=args.task_type,
        model_name=args.model,
        iterations=args.iterations,
        output_dir=args.output,
        min_pages=args.pages,
        turns=args.turns,
        show_output=args.verbose,
    )

    # Run experiment
    runner = ExperimentRunner(config)

    try:
        results = runner.run_experiment()

        # Print summary
        summary = runner.save_summary()

        logger.info("\n" + "=" * 70)
        logger.info("EXPERIMENT COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Total runs: {summary['statistics']['total_runs']}")
        logger.info(f"Successful: {summary['statistics']['successful']}")
        logger.info(f"Failed: {summary['statistics']['failed']}")
        logger.info(f"Success rate: {summary['statistics']['successful'] / summary['statistics']['total_runs'] * 100:.1f}%")
        logger.info("=" * 70)

        # Exit with error if any runs failed
        if summary["statistics"]["failed"] > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("\n\nExperiment interrupted by user")
        runner.save_summary()
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
