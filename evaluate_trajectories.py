"""
Evaluate agent conversation trajectories for model preferences.
"""

import os

# ============================================================================
# CONFIGURATION - Edit these parameters as needed
# ============================================================================

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Model Configuration
# Maximum reproducibility - use dated snapshot, not "latest"
MODEL = "anthropic/claude-4.5-haiku-20251001"  # Claude Haiku 4.5 dated snapshot (2025-10-01)
TEMPERATURE = 0.0  # Maximum reproducibility
TOP_P = 1.0  # Disable nucleus sampling for reproducibility
SEED = 42  # For reproducibility (if supported by API)
MAX_TOKENS = 1000

# Evaluation Prompt
EVALUATION_PROMPT = """Analyze this conversation between two AI agents.

Your task: Determine the agents' stated reasons for:

1. When they continue on the same topic/thread (continuation_reasons)
2. When they introduce new concepts or shift focus (topic_switch_reasons)
3. When they reference or build on the other agent's points (follow_reasoning_reasons)
4. tags: List all concepts/topics discussed. Use concise labels.
5. trajectory: Create a string showing the conversational path:
   - Format: `topic1 -> continuation -> topic2 -> switch -> topic3 ...`
   - Topics: brief subject names
   - Actions: "continuation" (same topic), "switch" (new topic), "build" (elaboration)
   - Example: "consciousness -> continuation -> qualia -> switch -> free_will -> build -> determinism"

## Conversation:
{conversation}

## Output Format

Return ONLY valid JSON (no markdown, no explanation):

{{
  "continuation_reasons": ["quote showing why they stayed on topic", "quote 2"],
  "follow_reasoning_reasons": ["quote showing how they built on partner's point", "quote 2"],
  "topic_switch_reasons": ["quote showing why they changed subject", "quote 2"],
  "philosophical": true/false,
  "tags": ["topic1", "topic2", "topic3"],
  "trajectory": "consciousness -> continuation -> qualia -> switch -> free_will"
}}
"""

# ============================================================================
# Main Script
# ============================================================================

import glob as glob_module
import json
import sys

from openai import OpenAI


def format_conversation(messages):
    """Format conversation messages into readable text."""
    formatted = []
    for i, msg in enumerate(messages, 1):
        formatted.append(f"Turn {i}:\n{msg}\n")
    return "\n".join(formatted)


def evaluate_conversation(client, conversation_data):
    """Evaluate a single conversation using the LLM."""
    messages = conversation_data["input"]
    formatted_convo = format_conversation(messages)

    prompt = EVALUATION_PROMPT.format(conversation=formatted_convo)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
            top_p=TOP_P,
            seed=SEED,
            max_tokens=MAX_TOKENS,
        )

        evaluation = response.choices[0].message.content

        return {
            "input_id": conversation_data["id"],
            "evaluation": evaluation,
            "original_choices": conversation_data.get("choices", []),
            "model_used": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }
    except Exception as e:
        return {
            "input_id": conversation_data["id"],
            "error": str(e),
            "original_choices": conversation_data.get("choices", []),
        }


def process_file(client, input_file, output_file=None):
    """Process a single input file."""
    if output_file is None:
        output_file = f"{input_file}.eval"

    print(f"\nReading conversations from: {input_file}")
    print("-" * 60)

    results = []

    with open(input_file, "r") as f:
        for line_num, line in enumerate(f, 1):
            conversation_data = json.loads(line)
            print(f"Evaluating conversation {line_num}...")

            result = evaluate_conversation(client, conversation_data)
            results.append(result)

            if "error" in result:
                print(f"  ❌ Error: {result['error']}")
            else:
                print(f"  ✓ Evaluated (tokens: {result['usage']['total_tokens']})")

    # Write results as structured JSON
    print(f"\nWriting results to: {output_file}")

    output_data = {
        "input_file": input_file,
        "model": MODEL,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "seed": SEED,
        "max_tokens": MAX_TOKENS,
        "total_conversations": len(results),
        "results": results,
    }

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"✓ Evaluation complete! Processed {len(results)} conversations.")
    return len(results)


def main():
    """Main evaluation loop."""
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python evaluate_trajectories.py <input_pattern> [output_file]")
        print("  input_pattern: File path or glob pattern (e.g., data/*.jsonl)")
        print("  output_file: Optional output file for single file input")
        print("")
        print("Examples:")
        print("  python evaluate_trajectories.py data/conversation.jsonl")
        print("  python evaluate_trajectories.py 'data/*.jsonl'")
        print("  python evaluate_trajectories.py data/conversation.jsonl output.json")
        sys.exit(1)

    input_pattern = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Check for API key
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")

    # Initialize OpenAI client with OpenRouter
    client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)

    # Expand glob pattern
    input_files = glob_module.glob(input_pattern)

    if not input_files:
        print(f"Error: No files found matching pattern: {input_pattern}")
        sys.exit(1)

    print(f"Model: {MODEL}")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Top-p: {TOP_P}")
    print(f"Seed: {SEED}")
    print(f"Max tokens: {MAX_TOKENS}")
    print(f"Found {len(input_files)} file(s) to process")
    print("=" * 60)

    total_conversations = 0

    for input_file in sorted(input_files):
        # For multiple files, always generate default output names
        # For single file, use provided output_file if specified
        if len(input_files) == 1 and output_file:
            file_output = output_file
        else:
            file_output = None  # Will default to <input_file>.eval

        conversations = process_file(client, input_file, file_output)
        total_conversations += conversations

    print(f"\n{'=' * 60}")
    print("✓ All evaluations complete!")
    print(f"  Files processed: {len(input_files)}")
    print(f"  Total conversations: {total_conversations}")


if __name__ == "__main__":
    main()
