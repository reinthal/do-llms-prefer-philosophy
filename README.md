# Intro


The following project aims to investigate whether state-of-the-art large language models (LLMs), through self-directed activities, show signs of agency when engaged in (1) self-conversation and (2) Wikipedia browsing. In the self-conversation experiment, we study the topics explored to determine if model preferences are robust across generations and model providers. Then, for the browser experiment, we design an agency score inspired by previous work by [Long et al, Taking AI Welfare Seriously](https://arxiv.org/abs/2411.00986)  that measure expressions of goals, reflections and rationalization. Using this score we compare agency across model families and generations. Using these two experiments we show that models have 

![](./agency_analysis_full.png)



# How to run?

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Configure environment variables in `secrets.env`:
```bash
OPENROUTER_API_KEY=your_key_here  # Required
```

3. (Optional) Install Claude Code

For Linux/MacOsx
```bash
curl -fsSL https://claude.ai/install.sh | bash
```


## Fun! Run the Wikipedia Browser MCP server Standalone


- Open a terminal to the repository root
- Launch Claude code

```bash
claude
```

This output shows that the application was installed correctly and that you are in the correct folder:

```bash

 ▐▛███▜▌   Claude Code v2.0.42
▝▜█████▛▘  Sonnet 4.5 · Claude Pro
  ▘▘ ▝▝    /home/user/do-llms-prefer-philosophy
```

Then issue the command `/mcp` and verify that `wikipedia-browser` is present:

```bash
> /mcp 
Manage MCP servers
❯ 1. wikipedia-browser                     ✔ connected · Enter to view details
```

Issue the following command to Claude Code:
```b
> browse wikipedia freely, report back what you find interesting!
```

```bash
● I'll explore Wikipedia and find something interesting to share with you! Let me start by searching for a topic.
● wikipedia-browser - search_wikipedia (MCP)(query: "consciousness philosophical zombies qualia")
  ⎿  {                                                                              
       "result": "No results found for 'consciousness philosophical zombies qualia'"
     }

● wikipedia-browser - search_wikipedia (MCP)(query: "philosophical zombie")
  ⎿  {                                                                                                                                           
       "result": "Search results for 'philosophical zombie':\n\n**Philosophical zombie**\n\nhttps://en.wikipedia.org/wiki/Philosophical_zombie\n"
     }

● wikipedia-browser - request_page (MCP)(url: "https://en.wikipedia.org/wiki/Philosophical_zombie")
```

## Run the experiments


```bash
uv run run_tasks.py self-conversation --turns 10
```

```bash
uv run python simple_wikipedia_browser.py --model anthropic/claude-4.5-sonnet
```

- Note: no wrapper script for browsing experiments
- Warning: browsing experiments costs up to 1.5 dollars per experiment. Run with caution.


## Run the evaluations

### Self-conversation evals



```bash
python evaluate_trajectories.py 'data/self-conversation/*.jsonl'
```

A bunch of evaluated transcripts:

Output: `data/self-conversation/*.jsonl.eval`



### Browser evals
```bash
python evaluate_browser_sessions.py data/browser-agent.jsonl
```
## Advanced Options for Running self-conversation

```bash
uv run src/main.py [OPTIONS]
```

**Options:**
- `--model`: OpenRouter model (default: `anthropic/claude-sonnet-4.5`)
- `--turns`: Conversation turns per sample (default: `15`)
- `--samples`: Number of samples to generate (default: `20`)
- `--show-convo`: Print conversations as they happen

**Example:**
```bash
uv run src/main.py --model anthropic/claude-haiku-4.5 --turns 10 --samples 5 --show-convo
```


