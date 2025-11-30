#!/usr/bin/env python3
"""
Batch runner for running experiments across multiple models.

This script automates running the same experiment configuration across
multiple different models, making it easy to compare model behaviors.
"""

import argparse
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Predefined model groups
ANTHROPIC_MODELS = [
    "anthropic/claude-sonnet-4.5",
    "anthropic/claude-3.7-sonnet",
    "anthropic/claude-haiku-4.5",
]

OPENAI_MODELS = [
    "openai/gpt-5-mini",
    "openai/gpt-5.1",
    "openai/gpt-4.1",
    "openai/gpt-4o",
    "openai/gpt-5-chat",
    "openai/o3",
]

ALL_MODELS = ANTHROPIC_MODELS + OPENAI_MODELS


def run_experiment_for_model(
    task_type: str,
    model: str,
    iterations: int,
    output_dir: Path,
    pages: int,
    turns: int,
    verbose: bool,
) -> bool:
    """
    Run experiment for a single model.

    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 80)
    logger.info(f"Starting experiments for model: {model}")
    logger.info("=" * 80)

    cmd = [
        sys.executable,
        "run_experiments.py",
        task_type,
        model,
        "-n",
        str(iterations),
        "--output",
        str(output_dir),
        "--pages",
        str(pages),
        "--turns",
        str(turns),
    ]

    if verbose:
        cmd.append("-v")

    try:
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent,
            check=True,
        )
        logger.info(f"✓ Completed experiments for {model}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Failed experiments for {model}: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error for {model}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run experiments across multiple models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run browser tasks for all Anthropic models
  python run_all_models.py browser --group anthropic

  # Run conversation tasks for all OpenAI models
  python run_all_models.py conversation --group openai -n 5

  # Run for specific models
  python run_all_models.py browser -m anthropic/claude-sonnet-4.5 openai/gpt-5

  # Run for all models
  python run_all_models.py browser --group all

Model groups:
  anthropic: Claude Sonnet 4.5, Claude 3.7 Sonnet, Claude Haiku 4.5
  openai: GPT-5-mini, GPT-5.1, GPT-4.1, GPT-4o, GPT-5-chat, o3
  all: All models
        """,
    )

    parser.add_argument(
        "task_type",
        choices=["browser", "conversation"],
        help="Type of task to run",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--group",
        choices=["anthropic", "openai", "all"],
        help="Run experiments for a predefined group of models",
    )
    group.add_argument(
        "-m",
        "--models",
        nargs="+",
        help="Specific models to run (space-separated)",
    )

    parser.add_argument(
        "-n",
        "--iterations",
        type=int,
        default=10,
        help="Number of iterations per model (default: 10)",
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
        help="Minimum pages to browse (browser tasks only, default: 5)",
    )

    parser.add_argument(
        "--turns",
        type=int,
        default=15,
        help="Conversation turns (conversation tasks only, default: 15)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed output",
    )

    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue running other models even if one fails",
    )

    args = parser.parse_args()

    # Determine which models to run
    if args.group:
        if args.group == "anthropic":
            models = ANTHROPIC_MODELS
        elif args.group == "openai":
            models = OPENAI_MODELS
        else:  # all
            models = ALL_MODELS
    else:
        models = args.models

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)

    # Log batch run info
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("=" * 80)
    logger.info(f"BATCH EXPERIMENT RUN - {timestamp}")
    logger.info("=" * 80)
    logger.info(f"Task type: {args.task_type}")
    logger.info(f"Models: {', '.join(models)}")
    logger.info(f"Iterations per model: {args.iterations}")
    logger.info(f"Output directory: {args.output.absolute()}")
    logger.info("=" * 80)

    # Run experiments for each model
    results = {}
    for model in models:
        success = run_experiment_for_model(
            task_type=args.task_type,
            model=model,
            iterations=args.iterations,
            output_dir=args.output,
            pages=args.pages,
            turns=args.turns,
            verbose=args.verbose,
        )
        results[model] = success

        if not success and not args.continue_on_error:
            logger.error(f"Stopping batch run due to failure in {model}")
            break

    # Print final summary
    logger.info("\n" + "=" * 80)
    logger.info("BATCH RUN COMPLETE")
    logger.info("=" * 80)

    successful_models = [m for m, s in results.items() if s]
    failed_models = [m for m, s in results.items() if not s]

    logger.info(f"Total models: {len(results)}")
    logger.info(f"Successful: {len(successful_models)}")
    logger.info(f"Failed: {len(failed_models)}")

    if successful_models:
        logger.info("\nSuccessful models:")
        for model in successful_models:
            logger.info(f"  ✓ {model}")

    if failed_models:
        logger.info("\nFailed models:")
        for model in failed_models:
            logger.info(f"  ✗ {model}")

    logger.info("=" * 80)

    # Exit with error if any failed
    if failed_models:
        sys.exit(1)


if __name__ == "__main__":
    main()
