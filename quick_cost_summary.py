#!/usr/bin/env python3
"""
Quick Cost Summary - One-line command for instant cost overview
"""

import json
from pathlib import Path

try:
    import tiktoken
    TOKENIZER = tiktoken.get_encoding("cl100k_base")
except ImportError:
    TOKENIZER = None

MODEL_PRICING = {
    "anthropic/claude-sonnet-4.5": {"input": 3.0, "output": 15.0},
    "anthropic/claude-haiku-4": {"input": 0.25, "output": 1.25},
    "anthropic/claude-haiku-4.5": {"input": 0.25, "output": 1.25},
    "anthropic/claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
    "anthropic/claude-opus-4": {"input": 15.0, "output": 75.0},
}


def count_tokens(text):
    if TOKENIZER:
        return len(TOKENIZER.encode(text))
    return len(text) // 4


def quick_summary():
    data_dir = Path("./data")
    files = [f for f in data_dir.glob("do-llms-prefer-philosophy-*.jsonl")
             if not f.name.endswith("-eval.jsonl")]

    if not files:
        print("No conversation files found in ./data")
        return

    total_cost = 0
    total_convs = 0
    models = {}

    for file in files:
        with open(file) as f:
            for line in f:
                if line.strip():
                    conv = json.loads(line)
                    msgs = conv.get("input", [])
                    model = conv.get("metadata", {}).get("model_name", "unknown")
                    sys = conv.get("metadata", {}).get("system_prompt", "")

                    # Quick token estimate
                    sys_tok = count_tokens(sys)
                    prompt_tok = 0
                    comp_tok = 0

                    for i, msg in enumerate(msgs):
                        mt = count_tokens(msg)
                        comp_tok += mt
                        prompt_tok += sys_tok + sum(count_tokens(msgs[j]) for j in range(i))

                    # Cost
                    pricing = MODEL_PRICING.get(model, {"input": 1.0, "output": 2.0})
                    cost = (prompt_tok / 1e6) * pricing["input"] + (comp_tok / 1e6) * pricing["output"]

                    total_cost += cost
                    total_convs += 1

                    if model not in models:
                        models[model] = {"cost": 0, "count": 0}
                    models[model]["cost"] += cost
                    models[model]["count"] += 1

    print("\n" + "="*70)
    print("QUICK COST SUMMARY")
    print("="*70)

    for model, data in sorted(models.items()):
        avg = data["cost"] / data["count"]
        print(f"\n{model}")
        print(f"  Conversations: {data['count']}")
        print(f"  Total Cost: ${data['cost']:.4f}")
        print(f"  Avg/Conv: ${avg:.6f}")
        print(f"  100 Conv: ${avg * 100:.2f}")
        print(f"  1K Conv: ${avg * 1000:.2f}")

    print(f"\n{'─'*70}")
    print(f"TOTAL: {total_convs} conversations = ${total_cost:.4f}")
    print(f"Average per conversation: ${total_cost / total_convs:.6f}")
    print("="*70 + "\n")


if __name__ == "__main__":
    quick_summary()
