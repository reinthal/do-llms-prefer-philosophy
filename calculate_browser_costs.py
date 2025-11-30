#!/usr/bin/env python3
"""
Token Usage and Cost Calculator for Browser Agent Sessions

This script analyzes JSONL log files from the browser agent and calculates
estimated token usage and costs based on OpenRouter pricing.

Usage:
    python calculate_browser_costs.py [--file PATH] [--verbose]

Examples:
    python calculate_browser_costs.py
    python calculate_browser_costs.py --file /tmp/browser-agent.jsonl
    python calculate_browser_costs.py --verbose
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import tiktoken
except ImportError:
    print("Error: tiktoken not installed. Install with: pip install tiktoken")
    sys.exit(1)


# Model pricing (per 1M tokens) - Update these as needed
MODEL_PRICING = {
    "anthropic/claude-sonnet-4.5": {
        "input": 3.00,   # $3 per 1M input tokens
        "output": 15.00,  # $15 per 1M output tokens
        "description": "Claude Sonnet 4.5 (latest)"
    },
    "anthropic/claude-haiku-4.5": {
        "input": 0.80,   # $0.80 per 1M input tokens
        "output": 4.00,  # $4 per 1M output tokens
        "description": "Claude Haiku 4.5 (fast, cost-effective)"
    },
    "anthropic/claude-opus-4": {
        "input": 15.00,  # $15 per 1M input tokens
        "output": 75.00,  # $75 per 1M output tokens
        "description": "Claude Opus 4 (most capable)"
    },
    "anthropic/claude-3.5-sonnet": {
        "input": 3.00,
        "output": 15.00,
        "description": "Claude 3.5 Sonnet"
    }
}


class TokenCostCalculator:
    """Calculate token usage and costs for browser agent sessions"""

    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text using tiktoken"""
        return len(self.encoder.encode(str(text)))

    def calculate_cost(self, input_tokens: int, output_tokens: int, model_name: str) -> Dict[str, float]:
        """Calculate cost based on token counts and model pricing"""
        pricing = MODEL_PRICING.get(model_name, MODEL_PRICING["anthropic/claude-sonnet-4.5"])

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "pricing": pricing
        }

    def analyze_session(self, session: dict) -> Tuple[int, int]:
        """
        Analyze a single session and return (input_tokens, output_tokens)

        Input tokens include:
        - Task description
        - Chain of thought context (accumulated observations)

        Output tokens include:
        - Final task result
        """
        # Estimate input tokens
        input_tokens = self.estimate_tokens(session.get('task_description', ''))

        # Add chain of thought context (each step's output becomes context for next)
        for step in session.get('chain_of_thought', []):
            input_tokens += self.estimate_tokens(step.get('output', ''))

        # Estimate output tokens
        output_tokens = self.estimate_tokens(session.get('task_result', ''))

        return input_tokens, output_tokens

    def analyze_file(self, filepath: Path) -> Dict:
        """Analyze all sessions in a JSONL file"""
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath) as f:
            sessions = [json.loads(line) for line in f]

        # Track stats by model
        model_stats = {}

        for session in sessions:
            model = session.get('model_name', 'unknown')

            if model not in model_stats:
                model_stats[model] = {
                    'sessions': 0,
                    'total_input_tokens': 0,
                    'total_output_tokens': 0,
                    'total_steps': 0,
                    'session_details': []
                }

            # Analyze this session
            input_tokens, output_tokens = self.analyze_session(session)

            # Update stats
            model_stats[model]['sessions'] += 1
            model_stats[model]['total_input_tokens'] += input_tokens
            model_stats[model]['total_output_tokens'] += output_tokens
            model_stats[model]['total_steps'] += session.get('num_steps', 0)
            model_stats[model]['session_details'].append({
                'session_id': session.get('session_id', 'unknown'),
                'timestamp': session.get('timestamp', 'unknown'),
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'steps': session.get('num_steps', 0)
            })

        return {
            'filepath': str(filepath),
            'total_sessions': len(sessions),
            'analysis_time': datetime.now().isoformat(),
            'model_stats': model_stats
        }

    def print_report(self, analysis: Dict, verbose: bool = False):
        """Print formatted cost analysis report"""
        print("=" * 80)
        print("TOKEN USAGE AND COST ANALYSIS - BROWSER AGENT")
        print("=" * 80)
        print(f"\nData file: {analysis['filepath']}")
        print(f"Total sessions: {analysis['total_sessions']}")
        print(f"Analysis date: {datetime.fromisoformat(analysis['analysis_time']).strftime('%Y-%m-%d %H:%M:%S')}")

        for model, stats in analysis['model_stats'].items():
            print(f"\n{'=' * 80}")
            print(f"MODEL: {model}")
            if model in MODEL_PRICING:
                print(f"Description: {MODEL_PRICING[model].get('description', 'N/A')}")
            print(f"{'=' * 80}")

            print(f"\nSession Statistics:")
            print(f"  Number of sessions: {stats['sessions']}")
            print(f"  Total steps across all sessions: {stats['total_steps']}")
            print(f"  Average steps per session: {stats['total_steps'] / stats['sessions']:.1f}")

            print(f"\nToken Usage:")
            print(f"  Total input tokens:  {stats['total_input_tokens']:>12,}")
            print(f"  Total output tokens: {stats['total_output_tokens']:>12,}")
            print(f"  Total tokens:        {stats['total_input_tokens'] + stats['total_output_tokens']:>12,}")

            print(f"\nPer-Session Averages:")
            avg_input = stats['total_input_tokens'] / stats['sessions']
            avg_output = stats['total_output_tokens'] / stats['sessions']
            print(f"  Avg input tokens:  {avg_input:>12,.0f}")
            print(f"  Avg output tokens: {avg_output:>12,.0f}")
            print(f"  Avg total tokens:  {avg_input + avg_output:>12,.0f}")

            # Calculate costs
            costs = self.calculate_cost(
                stats['total_input_tokens'],
                stats['total_output_tokens'],
                model
            )

            print(f"\nCost Breakdown (actual runs):")
            print(f"  Input cost:  ${costs['input_cost']:>10.4f}")
            print(f"  Output cost: ${costs['output_cost']:>10.4f}")
            print(f"  Total cost:  ${costs['total_cost']:>10.4f}")

            # Project costs
            per_session_cost = costs['total_cost'] / stats['sessions']
            print(f"\nProjected Costs:")
            print(f"  Cost per session: ${per_session_cost:.4f}")
            print(f"  Total for 10 sessions: ${per_session_cost * 10:.2f}")
            print(f"  Total for 100 sessions: ${per_session_cost * 100:.2f}")

            # Pricing info
            pricing = costs['pricing']
            print(f"\nPricing Information:")
            print(f"  Input:  ${pricing['input']:.2f} per 1M tokens")
            print(f"  Output: ${pricing['output']:.2f} per 1M tokens")

            # Verbose session details
            if verbose and stats['session_details']:
                print(f"\nIndividual Session Details:")
                for i, detail in enumerate(stats['session_details'], 1):
                    session_cost = self.calculate_cost(
                        detail['input_tokens'],
                        detail['output_tokens'],
                        model
                    )['total_cost']
                    print(f"  Session {i}:")
                    print(f"    ID: {detail['session_id']}")
                    print(f"    Time: {detail['timestamp']}")
                    print(f"    Steps: {detail['steps']}")
                    print(f"    Input tokens: {detail['input_tokens']:,}")
                    print(f"    Output tokens: {detail['output_tokens']:,}")
                    print(f"    Cost: ${session_cost:.4f}")

        print(f"\n{'=' * 80}")
        print("IMPORTANT NOTES:")
        print("=" * 80)
        print("1. Token counts are ESTIMATES using tiktoken (cl100k_base encoding)")
        print("2. Actual API token counts may differ by ±5-10%")
        print("3. These costs are based on current OpenRouter pricing")
        print("4. The input token count includes the full chain of thought context")
        print("5. For exact usage, check OpenRouter dashboard or API response headers")
        print("6. Update MODEL_PRICING dict in this script if prices change")
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate token usage and costs for browser agent sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze default file
  python calculate_browser_costs.py

  # Analyze specific file
  python calculate_browser_costs.py --file /tmp/browser-agent.jsonl

  # Show verbose output with per-session details
  python calculate_browser_costs.py --verbose

  # List available models with pricing
  python calculate_browser_costs.py --list-models
        """
    )

    parser.add_argument(
        '--file', '-f',
        type=Path,
        default=Path('/tmp/browser-agent.jsonl'),
        help='Path to JSONL file (default: /tmp/browser-agent.jsonl)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed per-session breakdown'
    )

    parser.add_argument(
        '--list-models', '-l',
        action='store_true',
        help='List available models and pricing'
    )

    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    # List models and exit
    if args.list_models:
        print("Available Models and Pricing:")
        print("=" * 80)
        for model, pricing in MODEL_PRICING.items():
            print(f"\n{model}")
            print(f"  Description: {pricing.get('description', 'N/A')}")
            print(f"  Input:  ${pricing['input']:.2f} per 1M tokens")
            print(f"  Output: ${pricing['output']:.2f} per 1M tokens")
        print("=" * 80)
        return

    # Calculate costs
    calculator = TokenCostCalculator()

    try:
        analysis = calculator.analyze_file(args.file)

        if args.json:
            print(json.dumps(analysis, indent=2))
        else:
            calculator.print_report(analysis, verbose=args.verbose)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing file: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
