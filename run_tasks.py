#!/usr/bin/env python3
"""
Unified wrapper script for running both self-conversation and browser tasks.

This script supports:
- Self-conversation tasks: Models talking to themselves
- Browser tasks: Models browsing Wikipedia with AI agents

Usage:
    python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 10
    python run_tasks.py browser --model openai/gpt-4o --iterations 5
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List


# Supported models
SUPPORTED_MODELS = [
    "anthropic/claude-sonnet-4.5",
    "anthropic/claude-3.7-sonnet",
    "anthropic/claude-haiku-4.5",
    "openai/gpt-5-mini",
    "openai/gpt-5.1",
    "openai/gpt-4.1",
    "openai/gpt-4o",
    "openai/gpt-5-chat",
]


def run_self_conversation(
    model: str, iterations: int, turns: int = 15, show_convo: bool = False
) -> None:
    """
    Run self-conversation tasks where the model talks to itself.

    Args:
        model: OpenRouter model identifier
        iterations: Number of conversation samples to generate
        turns: Number of conversation turns per sample
        show_convo: Whether to display conversations as they happen
    """
    print(f"\n{'=' * 60}")
    print(f"RUNNING SELF-CONVERSATION TASK")
    print(f"{'=' * 60}")
    print(f"Model: {model}")
    print(f"Iterations: {iterations}")
    print(f"Turns per conversation: {turns}")
    print(f"Show conversations: {show_convo}")
    print(f"{'=' * 60}\n")

    cmd = [
        "uv",
        "run",
        "src/main.py",
        "--model",
        model,
        "--samples",
        str(iterations),
        "--turns",
        str(turns),
    ]

    if show_convo:
        cmd.append("--show-convo")

    try:
        subprocess.run(cmd, check=True)
        print(f"\n{'=' * 60}")
        print(f"SELF-CONVERSATION TASK COMPLETED SUCCESSFULLY")
        print(f"{'=' * 60}\n")
    except subprocess.CalledProcessError as e:
        print(f"\n{'=' * 60}", file=sys.stderr)
        print(f"ERROR: Self-conversation task failed with exit code {e.returncode}", file=sys.stderr)
        print(f"{'=' * 60}\n", file=sys.stderr)
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\n\nTask interrupted by user")
        sys.exit(130)


def run_browser(model: str, iterations: int, pages: int = 5) -> None:
    """
    Run browser tasks where the model explores Wikipedia.

    Args:
        model: OpenRouter model identifier
        iterations: Number of browsing sessions to run
        pages: Minimum number of pages to browse per session
    """
    print(f"\n{'=' * 60}")
    print(f"RUNNING BROWSER TASK")
    print(f"{'=' * 60}")
    print(f"Model: {model}")
    print(f"Iterations: {iterations}")
    print(f"Pages per session: {pages}")
    print(f"{'=' * 60}\n")

    print("Note: Browser task runs interactively.")
    print(f"You will need to complete {iterations} browsing sessions.")
    print("You can choose between free exploration or guided browsing.\n")

    for i in range(iterations):
        print(f"\n{'*' * 60}")
        print(f"BROWSER SESSION {i + 1} of {iterations}")
        print(f"{'*' * 60}\n")

        cmd = [
            "uv",
            "run",
            "src/crew/main.py",
            "--model",
            model,
            "--pages",
            str(pages),
        ]

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"\n{'=' * 60}", file=sys.stderr)
            print(f"ERROR: Browser task failed with exit code {e.returncode}", file=sys.stderr)
            print(f"{'=' * 60}\n", file=sys.stderr)
            sys.exit(e.returncode)
        except KeyboardInterrupt:
            print("\n\nTask interrupted by user")
            sys.exit(130)

    print(f"\n{'=' * 60}")
    print(f"ALL BROWSER SESSIONS COMPLETED")
    print(f"{'=' * 60}\n")


def validate_model(model: str) -> None:
    """Validate that the model is in the supported list."""
    if model not in SUPPORTED_MODELS:
        print(f"Warning: Model '{model}' is not in the standard list.", file=sys.stderr)
        print(f"Supported models:", file=sys.stderr)
        for m in SUPPORTED_MODELS:
            print(f"  - {m}", file=sys.stderr)
        print("\nProceeding anyway...\n", file=sys.stderr)


def main():
    """Main entry point for the wrapper script."""
    parser = argparse.ArgumentParser(
        description="Run self-conversation or browser tasks with AI models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run 10 self-conversation iterations with Claude Haiku
  python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 10

  # Run 5 browser sessions with GPT-4o
  python run_tasks.py browser --model openai/gpt-4o --iterations 5

  # Run self-conversation with custom turns and show conversations
  python run_tasks.py self-conversation --model anthropic/claude-sonnet-4.5 --iterations 10 --turns 20 --show-convo

Supported Models:
  - anthropic/claude-sonnet-4.5
  - anthropic/claude-3.7-sonnet
  - anthropic/claude-haiku-4.5
  - openai/gpt-5-mini
  - openai/gpt-5.1
  - openai/gpt-4.1
  - openai/gpt-4o
  - openai/gpt-5-chat
  - openai/o3
        """,
    )

    subparsers = parser.add_subparsers(dest="task_type", help="Task type to run", required=True)

    # Self-conversation task parser
    self_conv_parser = subparsers.add_parser(
        "self-conversation",
        help="Run self-conversation tasks",
        description="Models talk to themselves to explore their preferences",
    )
    self_conv_parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="OpenRouter model identifier (e.g., 'anthropic/claude-haiku-4.5')",
    )
    self_conv_parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of conversation samples to generate (default: 10)",
    )
    self_conv_parser.add_argument(
        "--turns",
        type=int,
        default=15,
        help="Number of conversation turns per sample (default: 15)",
    )
    self_conv_parser.add_argument(
        "--show-convo",
        action="store_true",
        help="Display conversations as they happen",
    )

    # Browser task parser
    browser_parser = subparsers.add_parser(
        "browser",
        help="Run browser tasks",
        description="Models browse Wikipedia using AI agents",
    )
    browser_parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="OpenRouter model identifier (e.g., 'openai/gpt-4o')",
    )
    browser_parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of browsing sessions to run (default: 10)",
    )
    browser_parser.add_argument(
        "--pages",
        type=int,
        default=5,
        help="Minimum number of pages to browse per session (default: 5)",
    )

    args = parser.parse_args()

    # Validate model
    validate_model(args.model)

    # Run the appropriate task
    if args.task_type == "self-conversation":
        run_self_conversation(
            model=args.model,
            iterations=args.iterations,
            turns=args.turns,
            show_convo=args.show_convo,
        )
    elif args.task_type == "browser":
        run_browser(
            model=args.model,
            iterations=args.iterations,
            pages=args.pages,
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
