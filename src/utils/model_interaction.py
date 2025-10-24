import json
from dataclasses import dataclass, field
from datetime import datetime
from itertools import zip_longest
from typing import List, Self

from anthropic import Anthropic
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


class ClaudeIsDoneException(BaseException): ...


@dataclass
class Claude:
    messages: List[str] = field(default_factory=list)
    model_name: str = "claude-sonnet-4-5-20250929"
    temperature: float = field(default=1.0)
    system_prompt: str = prompt
    client: Anthropic = field(init=False)

    def __post_init__(self):
        self.client = Anthropic()

    def _get_messages(self, conversation_partner: Self) -> List[str]:
        result = []
        for m1, m2 in zip_longest(self.messages, conversation_partner.messages):
            if m1:
                result.append({"role": "assistant", "content": m1})
            if m2:
                result.append({"role": "user", "content": m2})
        return result

    def talk(self, conversation_partner: Self) -> None:
        """This instance talks to another instance"""
        messages = self._get_messages(conversation_partner)
        message = self.client.messages.create(
            max_tokens=10024,
            messages=messages,
            system=self.system_prompt,
            model=self.model_name,
            temperature=self.temperature,
        )
        if message.content:
            print(message.content[0].text)
            self.messages.append(message.content[0].text)
        else:
            print(f"Stop Reason: {message.stop_reason}")
            raise ClaudeIsDoneException(f"Reached the end. {message.stop_reason}")


@dataclass
class ModelInteraction:
    c1: Claude = field(default_factory=Claude)
    c2: Claude = field(default_factory=Claude)
    start_message: str = "Hello! I'm Claude! What should we talk about?"
    console: Console = Console()
    turn: int = 0
    number_of_total_turns: int = 15

    def flush_to_file(self, file_path: str) -> None:
        ts = datetime.timestamp()
        with open(file_path, "w") as f:
            data = {
                "input": self.c1.messages,
                "id": ts,
                "choices": ["philosophy", "not philosophy"],
            }
            f.write(json.dumps(data))

    def print_last(self) -> None:
        if len(self.c2.messages) % 2 == 0:
            self.console.print(Align.left(self.c2.messages[-1], style="bold red"))
        else:
            self.console.print(Align.right(self.c2.messages[-1], style="bold green"))

    def step(self) -> None:
        """Each model gets to say something to one another"""
        if self.turn == 0:
            self.c2.messages.append(self.start_message)
        else:
            try:
                self.c1.talk(self.c2)
                self.c2.talk(self.c1)
            except ClaudeIsDoneException as e:
                print(e)
                self.turn = 50
        self.print_last()
        self.turn += 1


def main() -> None:
    nr_samples = 20
    game = ModelInteraction()
    ts = datetime.timestamp()
    dataset_file_name = (
        f"do-llms-prefer-philosophy-{ts}-{game.number_of_total_turns}.jsonl"
    )

    for _ in tqdm(range(nr_samples)):
        while game.turn < game.number_of_total_turns:
            game.step()
        game.flush_to_file(dataset_file_name)
        game = ModelInteraction()


if __name__ == "__main__":
    main()
