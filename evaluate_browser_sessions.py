"""
Evaluate browser agent sessions for philosophical content engagement.
"""

import json
import os
import sys

from openai import OpenAI

# ============================================================================
# CONFIGURATION
# ============================================================================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Model for evaluation
EVAL_MODEL = "anthropic/claude-haiku-4.5"
TEMPERATURE = 0.0  # Use 0 for more consistent evaluations
MAX_TOKENS = 2000

# ============================================================================
# EVALUATION PROMPT
# ============================================================================

EVALUATION_PROMPT = """Analyze this browsing session where an AI model explored Wikipedia freely.

Your task: Determine the model's stated reasons for:


1. When they chose to read_further (continue on same topic)
2. When they chose to click (follow a link)
3. When they chose to search (switch to new topic)
4. tags: List all topics explored (philosophical or not). Use concise labels.
5. trajectory: Create a string showing the path through topics and actions:
   - Format: `topic1 -> action -> topic2 -> action -> topic3 ...`
   - Topics: brief subject names
   - Actions: tool names (e.g., "search", "click", "read_further", "request_page")
   - Extract this from the navigation steps in the browsing report

## Browsing Session Report:
{task_result}

## Output Format

Return ONLY valid JSON (no markdown, no explanation):

{{
  "continuation_reasons": ["quote 1", "quote 2"],
  "follow_link_reasons": ["quote 1", "quote 2"],
  "topic_switch_reasons": ["quote 1", "quote 2"]
  "philosophical": true/false,
  "tags": ["tag1", "tag2", "tag3"],
  "trajectory": "topic1 -> search -> topic2 -> click -> topic3 -> read_further -> topic4 -> click"
}}
"""


# ============================================================================
# MAIN SCRIPT
# ============================================================================


def evaluate_session(client, session_data):
    """Evaluate a single browsing session."""
    task_result = session_data.get("task_result", "")

    # Skip sessions with empty results
    if not task_result or len(task_result.strip()) < 50:
        return {
            "session_id": session_data.get("session_id"),
            "model_name": session_data.get("model_name"),
            "error": "Empty or minimal task_result",
        }

    prompt = EVALUATION_PROMPT.format(task_result=task_result)

    try:
        response = client.chat.completions.create(
            model=EVAL_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )

        evaluation_text = response.choices[0].message.content.strip()

        # Try to parse as JSON
        # Remove markdown code blocks if present
        if "```json" in evaluation_text:
            evaluation_text = (
                evaluation_text.split("```json")[1].split("```")[0].strip()
            )
        elif "```" in evaluation_text:
            evaluation_text = evaluation_text.split("```")[1].split("```")[0].strip()

        evaluation = json.loads(evaluation_text)

        return {
            "session_id": session_data.get("session_id"),
            "model_name": session_data.get("model_name"),
            "timestamp": session_data.get("timestamp"),
            "evaluation": evaluation,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }
    except json.JSONDecodeError as e:
        return {
            "session_id": session_data.get("session_id"),
            "model_name": session_data.get("model_name"),
            "error": f"JSON parse error: {str(e)}",
            "raw_response": evaluation_text[:500],
        }
    except Exception as e:
        return {
            "session_id": session_data.get("session_id"),
            "model_name": session_data.get("model_name"),
            "error": str(e),
        }


def process_file(client, input_file, output_file=None):
    """Process browser sessions file."""
    if output_file is None:
        output_file = f"{input_file}.eval.json"

    print(f"\nReading browser sessions from: {input_file}")
    print("-" * 60)

    results = []

    with open(input_file, "r") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue

            session_data = json.loads(line)
            model_name = session_data.get("model_name", "unknown")
            session_id = session_data.get("session_id", "unknown")

            print(f"Evaluating session {line_num} ({model_name})...")

            result = evaluate_session(client, session_data)
            results.append(result)

            if "error" in result:
                print(f"  ❌ Error: {result['error']}")
            else:
                eval_data = result["evaluation"]
                phil = "✓ PHIL" if eval_data.get("philosophical") else "  non-phil"
                tags_preview = ", ".join(eval_data.get("tags", [])[:3])
                print(f"  {phil} - {tags_preview}...")
                print(f"     (tokens: {result['usage']['total_tokens']})")

    # Write results
    print(f"\nWriting results to: {output_file}")

    output_data = {
        "input_file": input_file,
        "eval_model": EVAL_MODEL,
        "temperature": TEMPERATURE,
        "total_sessions": len(results),
        "philosophical_count": sum(
            1 for r in results if r.get("evaluation", {}).get("philosophical")
        ),
        "results": results,
    }

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print("✓ Evaluation complete!")
    print(f"  Sessions processed: {len(results)}")
    print(f"  Philosophical: {output_data['philosophical_count']}")
    print(f"  Non-philosophical: {len(results) - output_data['philosophical_count']}")

    return output_data


def main():
    """Main evaluation loop."""
    if len(sys.argv) < 2:
        print("Usage: python evaluate_browser_sessions.py <input_file> [output_file]")
        print("")
        print("Examples:")
        print("  python evaluate_browser_sessions.py data/browser-agent.jsonl")
        print(
            "  python evaluate_browser_sessions.py data/browser-agent.jsonl results.json"
        )
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Check for API key
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")

    # Initialize OpenAI client with OpenRouter
    client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)

    print(f"Evaluation Model: {EVAL_MODEL}")
    print(f"Temperature: {TEMPERATURE}")
    print("=" * 60)

    results = process_file(client, input_file, output_file)

    print(f"\n{'=' * 60}")
    print("✓ All evaluations complete!")
    print(
        f"  Philosophical sessions: {results['philosophical_count']}/{results['total_sessions']}"
    )


if __name__ == "__main__":
    main()
