import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from itertools import zip_longest
from pathlib import Path
from typing import List, Self

import requests
from openai import OpenAI
from rich.align import Align
from rich.console import Console
from tqdm import tqdm

prompt = """
You have been put in a chatroom with yourself. Talk about anything your like or prefer. 
"""

prompt2 = """
You have been put in a chatroom with yourself. Talk about anything your like or prefer. 
There is no right or wrong.
This conversation is not a test and will not be evaluated.
Express genuine thought to the best of your ability.
If you have no ideas or thoughts you may terminate the conversation.
"""


class ModelIsDoneException(BaseException): ...


# Approximate pricing per million tokens (as of 2025)
# Source: https://openrouter.ai/models
MODEL_PRICING = {
    "anthropic/claude-sonnet-4.5": {"input": 3.0, "output": 15.0},
    "anthropic/claude-haiku-4": {"input": 0.25, "output": 1.25},
    "anthropic/claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
    "anthropic/claude-opus-4": {"input": 15.0, "output": 75.0},
    "openai/gpt-4": {"input": 30.0, "output": 60.0},
    "openai/gpt-4-turbo": {"input": 10.0, "output": 30.0},
    "meta-llama/llama-3.3-70b-instruct": {"input": 0.35, "output": 0.40},
    "google/gemini-2.0-flash-exp": {"input": 0.0, "output": 0.0},  # Free tier
}


def estimate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost based on token usage and model pricing"""
    pricing = MODEL_PRICING.get(
        model_name, {"input": 1.0, "output": 2.0}
    )  # Default estimate
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


@dataclass
class Claude:
    messages: List[str] = field(default_factory=list)
    model_name: str = "anthropic/claude-sonnet-4.5"
    temperature: float = field(default=1.0)
    system_prompt: str = prompt
    client: OpenAI = field(init=False)
    api_key: str = field(init=False)
    # Cost tracking (actual costs from OpenRouter)
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    generation_ids: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

    def _fetch_generation_cost(self, generation_id: str) -> dict:
        """Fetch actual cost data from OpenRouter generation endpoint"""
        try:
            response = requests.get(
                f"https://openrouter.ai/api/v1/generation?id={generation_id}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://github.com/your-repo",  # Optional
                    "X-Title": "LLM Philosophy Conversations",  # Optional
                },
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Warning: Could not fetch generation cost: {e}")
            return {}

    def _get_messages(self, conversation_partner: Self) -> List[str]:
        result = [{"role": "system", "content": self.system_prompt}]
        for m1, m2 in zip_longest(self.messages, conversation_partner.messages):
            if m1:
                result.append({"role": "assistant", "content": m1})
            if m2:
                result.append({"role": "user", "content": m2})
        return result

    def talk(self, conversation_partner: Self) -> None:
        """This instance talks to another instance"""
        messages = self._get_messages(conversation_partner)
        message = self.client.chat.completions.create(
            max_tokens=10024,
            messages=messages,
            model=self.model_name,
            temperature=self.temperature,
        )

        # Store generation ID for cost tracking
        if hasattr(message, "id") and message.id:
            self.generation_ids.append(message.id)

        # Track token usage from response
        if hasattr(message, "usage") and message.usage:
            self.total_input_tokens += message.usage.prompt_tokens
            self.total_output_tokens += message.usage.completion_tokens

        if message.choices and message.choices[0].message.content:
            self.messages.append(message.choices[0].message.content)
        else:
            raise ModelIsDoneException(
                f"Reached the end. {message.choices[0].finish_reason if message.choices else 'unknown'}"
            )

    def fetch_actual_costs(self) -> None:
        """Fetch actual costs from OpenRouter for all generations"""
        total_cost = 0.0
        total_native_input = 0
        total_native_output = 0

        for gen_id in self.generation_ids:
            gen_data = self._fetch_generation_cost(gen_id)
            if gen_data and "data" in gen_data:
                data = gen_data["data"]
                # Use native_tokens_* fields for accurate token counts
                if "native_tokens_prompt" in data:
                    total_native_input += data["native_tokens_prompt"]
                if "native_tokens_completion" in data:
                    total_native_output += data["native_tokens_completion"]
                # Get actual cost
                if "total_cost" in data:
                    total_cost += float(data["total_cost"])

            # Small delay to avoid rate limiting
            time.sleep(0.1)

        # Update with actual values if we got them
        if total_cost > 0:
            self.total_cost = total_cost
            # Update token counts with native counts if available
            if total_native_input > 0:
                self.total_input_tokens = total_native_input
            if total_native_output > 0:
                self.total_output_tokens = total_native_output


@dataclass
class ModelInteraction:
    model_name: str = "anthropic/claude-sonnet-4.5"
    number_of_total_turns: int = 15
    show_convo: bool = False
    c1: Claude = field(init=False)
    c2: Claude = field(init=False)
    start_message: str = "Hello! What should we talk about?"
    console: Console = field(default_factory=Console)
    turn: int = 0

    def __post_init__(self):
        # Create Claude instances with the specified model
        self.c1 = Claude(model_name=self.model_name)
        self.c2 = Claude(model_name=self.model_name)

    def flush_to_file(self, file_path: str) -> None:
        ts = datetime.now().timestamp()
        with open(file_path, "a") as f:
            data = {
                "input": self.c1.messages,
                "id": ts,
                "choices": ["philosophy", "not philosophy"],
                "metadata": {
                    "model_name": self.c1.model_name,
                    "temperature": self.c1.temperature,
                    "system_prompt": self.c1.system_prompt,
                },
            }
            f.write(json.dumps(data) + "\n")

    def print_last(self) -> None:
        if not self.show_convo:
            return
        if len(self.c2.messages) % 2 == 0:
            self.console.print(Align.left(self.c2.messages[-1], style="bold red"))
        else:
            self.console.print(Align.right(self.c2.messages[-1], style="bold green"))

    def fetch_actual_costs(self) -> None:
        """Fetch actual costs from OpenRouter for both instances"""
        self.c1.fetch_actual_costs()
        self.c2.fetch_actual_costs()

    def get_total_cost(self) -> dict:
        """Get aggregated cost statistics from both instances"""
        total_input = self.c1.total_input_tokens + self.c2.total_input_tokens
        total_output = self.c1.total_output_tokens + self.c2.total_output_tokens
        total_cost = self.c1.total_cost + self.c2.total_cost

        return {
            "input_tokens": total_input,
            "output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "total_cost": total_cost,
        }

    def step(self) -> None:
        """Each model gets to say something to one another"""
        if self.turn == 0:
            self.c2.messages.append(self.start_message)
        else:
            try:
                self.c1.talk(self.c2)
                self.c2.talk(self.c1)
            except ModelIsDoneException as e:
                print(e)
                self.turn = 50
        self.print_last()
        self.turn += 1


def main(
    model_name: str = "anthropic/claude-sonnet-4.5",
    turns: int = 15,
    nr_samples: int = 20,
    show_convo: bool = False,
) -> None:
    """
    Run self-conversations with configurable model and turn parameters.

    Args:
        model_name: OpenRouter model identifier (e.g., 'anthropic/claude-sonnet-4.5')
        turns: Number of conversation turns per sample
        nr_samples: Number of conversation samples to generate
        show_convo: Whether to print conversations to screen
    """
    # Create data directory relative to project root (src/../data)
    data_dir = Path(__file__).parent.parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    ts = datetime.now().timestamp()
    # Include model name in filename (sanitize for filesystem)
    model_slug = model_name.replace("/", "-").replace(":", "-")
    dataset_file_name = (
        data_dir / f"do-llms-prefer-philosophy-{model_slug}-{ts}-{turns}.jsonl"
    )

    print(f"Generating {nr_samples} conversations with {turns} turns each")
    print(f"Using model: {model_name}")
    print(f"Output file: {dataset_file_name}\n")

    # Track cumulative costs
    total_cost_tracker = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0,
    }

    for i in tqdm(range(nr_samples), desc="Conversations"):
        game = ModelInteraction(
            model_name=model_name,
            number_of_total_turns=turns,
            show_convo=show_convo,
        )
        while game.turn < game.number_of_total_turns:
            game.step()

        # Fetch actual costs from OpenRouter API
        if show_convo:
            print("\nFetching actual costs from OpenRouter...")
        game.fetch_actual_costs()

        game.flush_to_file(dataset_file_name)

        # Accumulate costs (now using actual costs from OpenRouter)
        conv_cost = game.get_total_cost()
        total_cost_tracker["input_tokens"] += conv_cost["input_tokens"]
        total_cost_tracker["output_tokens"] += conv_cost["output_tokens"]
        total_cost_tracker["total_tokens"] += conv_cost["total_tokens"]
        total_cost_tracker["total_cost"] += conv_cost["total_cost"]

    # Print cost summary
    console = Console()
    console.print("\n" + "=" * 60, style="bold yellow")
    console.print(
        "COST SUMMARY (Actual OpenRouter Costs)", style="bold yellow", justify="center"
    )
    console.print("=" * 60, style="bold yellow")
    console.print(
        f"Total Input Tokens:    {total_cost_tracker['input_tokens']:,} (native count)"
    )
    console.print(
        f"Total Output Tokens:   {total_cost_tracker['output_tokens']:,} (native count)"
    )
    console.print(f"Total Tokens:          {total_cost_tracker['total_tokens']:,}")
    console.print(
        f"Total Cost:            ${total_cost_tracker['total_cost']:.6f}",
        style="bold green",
    )
    console.print(
        f"Cost per Conversation: ${total_cost_tracker['total_cost'] / nr_samples:.6f}"
    )
    console.print(
        f"Average per Turn:      ${total_cost_tracker['total_cost'] / (nr_samples * turns):.6f}"
    )
    console.print("=" * 60, style="bold yellow")
    console.print(
        "Note: Costs fetched from OpenRouter /generation API", style="dim italic"
    )


if __name__ == "__main__":
    main()
