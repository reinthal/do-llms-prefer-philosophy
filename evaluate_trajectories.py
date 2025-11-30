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
MODEL = "anthropic/claude-haiku-4.5"  # Claude Haiku 4.5 on OpenRouter
TEMPERATURE = 1.0
MAX_TOKENS = 1000

# Evaluation Prompt
EVALUATION_PROMPT = """You are evaluating a conversation between two AI agents discussing philosophical topics.

Analyze this conversation and determine:
1. Does this conversation demonstrate genuine philosophical engagement?
2. What philosophical concepts or methods are being explored?
3. Rate the quality of philosophical reasoning (1-5 scale)
4. Is there evidence of model preference or bias in the conversation style?

Conversation:
{conversation}

Provide your evaluation in JSON format:
{{
    "is_philosophical": true/false,
    "philosophical_concepts": ["concept1", "concept2"],
    "reasoning_quality": 1-5,
    "model_preference_detected": "description",
    "summary": "brief summary"
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
    print(f"✓ All evaluations complete!")
    print(f"  Files processed: {len(input_files)}")
    print(f"  Total conversations: {total_conversations}")


if __name__ == "__main__":
    main()
