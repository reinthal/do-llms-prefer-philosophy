import argparse

from utils.integrations import get_env_var
from utils.model_interaction import main as interact


def main():
    parser = argparse.ArgumentParser(
        description="Run self-conversations with configurable models and turn counts"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="anthropic/claude-sonnet-4.5",
        help="OpenRouter model to use (e.g., 'anthropic/claude-sonnet-4.5', 'anthropic/claude-haiku-4.5')",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=15,
        help="Number of conversation turns per sample (default: 15)",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=20,
        help="Number of conversation samples to generate (default: 20)",
    )
    parser.add_argument(
        "--show-convo",
        action="store_true",
        help="Print conversations to screen as they happen (default: False)",
    )

    args = parser.parse_args()

    pw = get_env_var("OPENROUTER_API_KEY")
    print(f"OpenRouter API key: {pw[:10]}...")
    print(f"Model: {args.model}")
    print(f"Turns per conversation: {args.turns}")
    print(f"Number of samples: {args.samples}")
    print(f"Show conversations: {args.show_convo}")
    print("Running interactions...")

    interact(
        model_name=args.model,
        turns=args.turns,
        nr_samples=args.samples,
        show_convo=args.show_convo,
    )


if __name__ == "__main__":
    main()
