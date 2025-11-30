#!/usr/bin/env python3
"""
Token Cost Calculator for Self-Conversation Tasks

This script analyzes JSONL conversation files and calculates token usage and costs.
It provides detailed breakdowns per file and per model.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

try:
    import tiktoken
except ImportError:
    print("Warning: tiktoken not installed. Install with: pip install tiktoken")
    print("Using character-based estimation instead (less accurate)")
    tiktoken = None


# Model pricing per million tokens (as of 2025)
# Source: https://openrouter.ai/models and Anthropic pricing
MODEL_PRICING = {
    "anthropic/claude-sonnet-4.5": {"input": 3.0, "output": 15.0},
    "anthropic/claude-haiku-4": {"input": 0.25, "output": 1.25},
    "anthropic/claude-haiku-4.5": {"input": 0.25, "output": 1.25},
    "anthropic/claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
    "anthropic/claude-opus-4": {"input": 15.0, "output": 75.0},
    "openai/gpt-4": {"input": 30.0, "output": 60.0},
    "openai/gpt-4-turbo": {"input": 10.0, "output": 30.0},
    "meta-llama/llama-3.3-70b-instruct": {"input": 0.35, "output": 0.40},
    "google/gemini-2.0-flash-exp": {"input": 0.0, "output": 0.0},
}


def get_tokenizer():
    """Get the appropriate tokenizer"""
    if tiktoken:
        # cl100k_base is used by GPT-4 and is a reasonable approximation for Claude
        return tiktoken.get_encoding("cl100k_base")
    return None


def count_tokens(text: str, tokenizer=None) -> int:
    """Count tokens in a text string"""
    if tokenizer:
        return len(tokenizer.encode(text))
    else:
        # Rough approximation: ~4 characters per token
        return len(text) // 4


def analyze_conversation(conv_data: dict, tokenizer=None) -> dict:
    """
    Analyze a single conversation for token usage.

    This estimates tokens based on the conversation structure:
    - Each message is a completion (output)
    - Previous messages become part of the prompt (input) for subsequent calls
    - System prompt is included in every API call
    """
    messages = conv_data.get("input", [])
    metadata = conv_data.get("metadata", {})
    model_name = metadata.get("model_name", "unknown")
    system_prompt = metadata.get("system_prompt", "")

    # Count tokens in system prompt
    system_tokens = count_tokens(system_prompt, tokenizer)

    # Track cumulative tokens
    prompt_tokens = 0
    completion_tokens = 0

    # Each message is generated as a completion
    # For each generation, all previous messages are in the prompt
    for i, message in enumerate(messages):
        msg_tokens = count_tokens(message, tokenizer)

        # This message is a completion
        completion_tokens += msg_tokens

        # System prompt is included in every API call
        prompt_tokens += system_tokens

        # Previous messages are included in the prompt for this call
        for j in range(i):
            prev_tokens = count_tokens(messages[j], tokenizer)
            prompt_tokens += prev_tokens

    total_tokens = prompt_tokens + completion_tokens

    return {
        "model_name": model_name,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "num_messages": len(messages),
    }


def calculate_cost(prompt_tokens: int, completion_tokens: int, model_name: str) -> Tuple[float, float, float]:
    """Calculate costs based on token usage and model pricing"""
    pricing = MODEL_PRICING.get(model_name, {"input": 1.0, "output": 2.0})

    input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost

    return input_cost, output_cost, total_cost


def analyze_file(file_path: Path, tokenizer=None, verbose: bool = False) -> dict:
    """Analyze a single JSONL file"""
    conversations = []

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    conversations.append(json.loads(line))
                except json.JSONDecodeError as e:
                    if verbose:
                        print(f"Warning: Failed to parse line: {e}")

    if not conversations:
        return None

    # Aggregate stats
    total_stats = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "num_conversations": len(conversations),
    }

    model_name = None
    for conv in conversations:
        stats = analyze_conversation(conv, tokenizer)
        total_stats["prompt_tokens"] += stats["prompt_tokens"]
        total_stats["completion_tokens"] += stats["completion_tokens"]
        total_stats["total_tokens"] += stats["total_tokens"]
        model_name = stats["model_name"]

    total_stats["model_name"] = model_name

    # Calculate costs
    input_cost, output_cost, total_cost = calculate_cost(
        total_stats["prompt_tokens"],
        total_stats["completion_tokens"],
        model_name
    )

    total_stats["input_cost"] = input_cost
    total_stats["output_cost"] = output_cost
    total_stats["total_cost"] = total_cost

    return total_stats


def print_file_stats(file_path: Path, stats: dict):
    """Print statistics for a single file"""
    print(f"\n{'='*80}")
    print(f"File: {file_path.name}")
    print(f"{'='*80}")

    print(f"\nModel: {stats['model_name']}")

    pricing = MODEL_PRICING.get(stats['model_name'], {"input": 1.0, "output": 2.0})
    print(f"Pricing: ${pricing['input']}/M input, ${pricing['output']}/M output")

    print(f"\nConversations: {stats['num_conversations']}")
    print(f"\nToken Usage:")
    print(f"  Prompt (Input) Tokens:      {stats['prompt_tokens']:,}")
    print(f"  Completion (Output) Tokens: {stats['completion_tokens']:,}")
    print(f"  Total Tokens:               {stats['total_tokens']:,}")

    print(f"\nEstimated Costs:")
    print(f"  Input Cost:        ${stats['input_cost']:.6f}")
    print(f"  Output Cost:       ${stats['output_cost']:.6f}")
    print(f"  Total Cost:        ${stats['total_cost']:.6f}")

    cost_per_conv = stats['total_cost'] / stats['num_conversations']
    print(f"\nPer Conversation:")
    print(f"  Cost:              ${cost_per_conv:.6f}")
    print(f"  Tokens:            {stats['total_tokens'] // stats['num_conversations']:,}")

    print(f"\nProjections:")
    print(f"  Cost for 10 conversations:  ${cost_per_conv * 10:.6f}")
    print(f"  Cost for 100 conversations: ${cost_per_conv * 100:.6f}")
    print(f"  Cost for 1000 conversations: ${cost_per_conv * 1000:.4f}")


def print_summary(all_stats: List[Tuple[Path, dict]]):
    """Print overall summary across all files"""
    if not all_stats:
        return

    print(f"\n\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}")

    # Group by model
    model_stats = {}
    for file_path, stats in all_stats:
        model = stats['model_name']
        if model not in model_stats:
            model_stats[model] = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "num_conversations": 0,
                "num_files": 0,
            }

        model_stats[model]["prompt_tokens"] += stats["prompt_tokens"]
        model_stats[model]["completion_tokens"] += stats["completion_tokens"]
        model_stats[model]["total_tokens"] += stats["total_tokens"]
        model_stats[model]["total_cost"] += stats["total_cost"]
        model_stats[model]["num_conversations"] += stats["num_conversations"]
        model_stats[model]["num_files"] += 1

    # Print per-model summary
    for model, stats in model_stats.items():
        print(f"\nModel: {model}")
        print(f"  Files: {stats['num_files']}")
        print(f"  Conversations: {stats['num_conversations']}")
        print(f"  Total Tokens: {stats['total_tokens']:,}")
        print(f"  Total Cost: ${stats['total_cost']:.6f}")
        print(f"  Cost per Conversation: ${stats['total_cost'] / stats['num_conversations']:.6f}")

    # Grand total
    total_cost = sum(s["total_cost"] for s in model_stats.values())
    total_tokens = sum(s["total_tokens"] for s in model_stats.values())
    total_conversations = sum(s["num_conversations"] for s in model_stats.values())

    print(f"\nGrand Total:")
    print(f"  Total Cost: ${total_cost:.6f}")
    print(f"  Total Tokens: {total_tokens:,}")
    print(f"  Total Conversations: {total_conversations}")
    if total_conversations > 0:
        print(f"  Average Cost per Conversation: ${total_cost / total_conversations:.6f}")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate token costs for self-conversation JSONL files"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="JSONL files to analyze (default: all files in ./data directory)"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="./data",
        help="Data directory to search for JSONL files (default: ./data)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only print summary, skip individual file stats"
    )

    args = parser.parse_args()

    # Get tokenizer
    tokenizer = get_tokenizer()
    if not tokenizer and args.verbose:
        print("Using character-based token estimation (less accurate)")

    # Determine files to analyze
    if args.files:
        file_paths = [Path(f) for f in args.files]
    else:
        data_dir = Path(args.data_dir)
        if not data_dir.exists():
            print(f"Error: Data directory '{data_dir}' does not exist")
            sys.exit(1)

        # Find conversation JSONL files (exclude eval files)
        file_paths = [
            f for f in data_dir.glob("do-llms-prefer-philosophy-*.jsonl")
            if not f.name.endswith("-eval.jsonl")
        ]

    if not file_paths:
        print("No JSONL files found to analyze")
        sys.exit(1)

    print(f"Analyzing {len(file_paths)} file(s)...")

    # Analyze each file
    all_stats = []
    for file_path in sorted(file_paths):
        stats = analyze_file(file_path, tokenizer, args.verbose)
        if stats:
            all_stats.append((file_path, stats))
            if not args.summary_only:
                print_file_stats(file_path, stats)

    # Print summary
    if len(all_stats) > 1 or args.summary_only:
        print_summary(all_stats)

    print(f"\n{'='*80}")
    print("Note: Costs are estimates based on published pricing.")
    print("Actual costs may vary based on model-specific tokenization.")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
