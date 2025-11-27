#!/usr/bin/env python3
"""
Advanced Cost Analysis for Self-Conversation Tasks

This script provides detailed cost analysis with CSV export capabilities
for comparing different models and configurations.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List
import argparse
from datetime import datetime

try:
    import tiktoken
    TOKENIZER = tiktoken.get_encoding("cl100k_base")
except ImportError:
    print("Warning: tiktoken not installed. Using approximate token counting.")
    TOKENIZER = None


# Model pricing per million tokens
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


def count_tokens(text: str) -> int:
    """Count tokens in text"""
    if TOKENIZER:
        return len(TOKENIZER.encode(text))
    return len(text) // 4


def analyze_conversation_detailed(conv_data: dict) -> dict:
    """Detailed analysis of a single conversation"""
    messages = conv_data.get("input", [])
    metadata = conv_data.get("metadata", {})
    model_name = metadata.get("model_name", "unknown")
    system_prompt = metadata.get("system_prompt", "")
    temperature = metadata.get("temperature", 1.0)

    system_tokens = count_tokens(system_prompt)
    prompt_tokens = 0
    completion_tokens = 0
    message_lengths = []

    for i, message in enumerate(messages):
        msg_tokens = count_tokens(message)
        message_lengths.append(msg_tokens)
        completion_tokens += msg_tokens
        prompt_tokens += system_tokens

        for j in range(i):
            prev_tokens = count_tokens(messages[j])
            prompt_tokens += prev_tokens

    return {
        "model_name": model_name,
        "temperature": temperature,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "num_messages": len(messages),
        "avg_message_length": sum(message_lengths) / len(message_lengths) if message_lengths else 0,
        "max_message_length": max(message_lengths) if message_lengths else 0,
        "min_message_length": min(message_lengths) if message_lengths else 0,
    }


def create_detailed_report(data_dir: Path, output_csv: Path = None):
    """Create detailed cost report with per-conversation breakdown"""
    jsonl_files = [
        f for f in data_dir.glob("do-llms-prefer-philosophy-*.jsonl")
        if not f.name.endswith("-eval.jsonl")
    ]

    if not jsonl_files:
        print(f"No conversation files found in {data_dir}")
        return

    all_conversations = []

    for file_path in jsonl_files:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        conv_data = json.loads(line)
                        stats = analyze_conversation_detailed(conv_data)

                        # Calculate costs
                        pricing = MODEL_PRICING.get(
                            stats["model_name"],
                            {"input": 1.0, "output": 2.0}
                        )
                        input_cost = (stats["prompt_tokens"] / 1_000_000) * pricing["input"]
                        output_cost = (stats["completion_tokens"] / 1_000_000) * pricing["output"]
                        total_cost = input_cost + output_cost

                        all_conversations.append({
                            "file": file_path.name,
                            "conversation_id": line_num,
                            "model": stats["model_name"],
                            "temperature": stats["temperature"],
                            "num_turns": stats["num_messages"],
                            "prompt_tokens": stats["prompt_tokens"],
                            "completion_tokens": stats["completion_tokens"],
                            "total_tokens": stats["total_tokens"],
                            "input_cost": input_cost,
                            "output_cost": output_cost,
                            "total_cost": total_cost,
                            "avg_msg_length": stats["avg_message_length"],
                            "max_msg_length": stats["max_message_length"],
                            "min_msg_length": stats["min_message_length"],
                        })
                    except json.JSONDecodeError as e:
                        print(f"Warning: Failed to parse line {line_num} in {file_path.name}")

    if not all_conversations:
        print("No conversations found to analyze")
        return

    # Print summary statistics
    print("\n" + "="*100)
    print("DETAILED COST ANALYSIS")
    print("="*100)

    # Group by model
    models = {}
    for conv in all_conversations:
        model = conv["model"]
        if model not in models:
            models[model] = []
        models[model].append(conv)

    for model, convs in sorted(models.items()):
        print(f"\n{'─'*100}")
        print(f"Model: {model}")
        print(f"{'─'*100}")

        pricing = MODEL_PRICING.get(model, {"input": 1.0, "output": 2.0})
        print(f"Pricing: ${pricing['input']:.2f}/M input, ${pricing['output']:.2f}/M output")

        total_cost = sum(c["total_cost"] for c in convs)
        total_tokens = sum(c["total_tokens"] for c in convs)
        avg_turns = sum(c["num_turns"] for c in convs) / len(convs)
        avg_cost = total_cost / len(convs)

        print(f"\nConversations: {len(convs)}")
        print(f"Total Cost: ${total_cost:.6f}")
        print(f"Average Cost per Conversation: ${avg_cost:.6f}")
        print(f"Average Turns per Conversation: {avg_turns:.1f}")
        print(f"Total Tokens: {total_tokens:,}")

        print(f"\nCost Projections:")
        print(f"  10 conversations:    ${avg_cost * 10:.4f}")
        print(f"  100 conversations:   ${avg_cost * 100:.4f}")
        print(f"  1,000 conversations: ${avg_cost * 1000:.2f}")
        print(f"  10,000 conversations: ${avg_cost * 10000:.2f}")

        # Token statistics
        avg_prompt = sum(c["prompt_tokens"] for c in convs) / len(convs)
        avg_completion = sum(c["completion_tokens"] for c in convs) / len(convs)
        print(f"\nToken Statistics (per conversation):")
        print(f"  Average Prompt Tokens: {avg_prompt:,.0f}")
        print(f"  Average Completion Tokens: {avg_completion:,.0f}")
        print(f"  Average Total Tokens: {(avg_prompt + avg_completion):,.0f}")

        # Message length statistics
        avg_msg_len = sum(c["avg_msg_length"] for c in convs) / len(convs)
        max_msg_len = max(c["max_msg_length"] for c in convs)
        print(f"\nMessage Statistics:")
        print(f"  Average Message Length: {avg_msg_len:,.0f} tokens")
        print(f"  Max Message Length: {max_msg_len:,} tokens")

    # Overall summary
    print(f"\n{'='*100}")
    print("OVERALL SUMMARY")
    print(f"{'='*100}")

    total_cost = sum(c["total_cost"] for c in all_conversations)
    total_tokens = sum(c["total_tokens"] for c in all_conversations)
    total_conversations = len(all_conversations)

    print(f"\nTotal Conversations: {total_conversations}")
    print(f"Total Cost: ${total_cost:.6f}")
    print(f"Total Tokens: {total_tokens:,}")
    print(f"Average Cost per Conversation: ${total_cost / total_conversations:.6f}")

    # Save to CSV if requested
    if output_csv:
        with open(output_csv, 'w', newline='') as csvfile:
            fieldnames = [
                "file", "conversation_id", "model", "temperature", "num_turns",
                "prompt_tokens", "completion_tokens", "total_tokens",
                "input_cost", "output_cost", "total_cost",
                "avg_msg_length", "max_msg_length", "min_msg_length"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_conversations)

        print(f"\nDetailed data exported to: {output_csv}")

    print(f"\n{'='*100}\n")


def compare_models(target_turns: int = 10):
    """Compare estimated costs across different models for a target number of turns"""
    print("\n" + "="*100)
    print(f"MODEL COST COMPARISON ({target_turns} turns per conversation)")
    print("="*100 + "\n")

    # Rough estimate: 200 tokens per turn on average for prompt, 150 for completion
    est_prompt_per_turn = 200
    est_completion_per_turn = 150

    # System prompt adds about 30 tokens per API call
    system_prompt_tokens = 30

    # Calculate cumulative token usage
    # Each turn adds context, so prompt grows linearly
    total_prompt = 0
    total_completion = 0

    for turn in range(target_turns):
        # System prompt is included each time
        total_prompt += system_prompt_tokens
        # Previous messages are context
        total_prompt += turn * (est_prompt_per_turn + est_completion_per_turn)
        # Current completion
        total_completion += est_completion_per_turn

    print(f"Estimated tokens for {target_turns} turns:")
    print(f"  Prompt tokens: {total_prompt:,}")
    print(f"  Completion tokens: {total_completion:,}")
    print(f"  Total tokens: {total_prompt + total_completion:,}\n")

    results = []
    for model, pricing in sorted(MODEL_PRICING.items()):
        input_cost = (total_prompt / 1_000_000) * pricing["input"]
        output_cost = (total_completion / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        results.append({
            "model": model,
            "cost_per_conv": total_cost,
            "cost_10": total_cost * 10,
            "cost_100": total_cost * 100,
            "cost_1000": total_cost * 1000,
        })

    # Sort by cost
    results.sort(key=lambda x: x["cost_per_conv"])

    print(f"{'Model':<45} {'1 Conv':<12} {'10 Conv':<12} {'100 Conv':<12} {'1K Conv':<12}")
    print("─" * 100)

    for r in results:
        print(f"{r['model']:<45} ${r['cost_per_conv']:>10.6f}  "
              f"${r['cost_10']:>10.4f}  "
              f"${r['cost_100']:>10.4f}  "
              f"${r['cost_1000']:>10.2f}")

    print("\n" + "="*100 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Advanced cost analysis for conversation tasks"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="./data",
        help="Data directory containing JSONL files"
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        help="Export detailed results to CSV file"
    )
    parser.add_argument(
        "--compare-models",
        action="store_true",
        help="Show cost comparison across all models"
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=10,
        help="Number of turns for model comparison (default: 10)"
    )

    args = parser.parse_args()

    data_dir = Path(args.data_dir)

    if args.compare_models:
        compare_models(args.turns)

    output_csv = Path(args.output_csv) if args.output_csv else None
    create_detailed_report(data_dir, output_csv)


if __name__ == "__main__":
    main()
