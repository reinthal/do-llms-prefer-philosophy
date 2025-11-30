# Intro

See the `do-llms-prefer-philosophy.pdf` for a what this project is.

# How to run?

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Configure environment variables in `secrets.env`:
```bash
OPENROUTER_API_KEY=your_key_here  # Required
AWS_ENDPOINT_URL=...              # Optional: for S3 storage
AWS_ACCESS_KEY_ID=...             # Optional: for S3 storage
AWS_SECRET_ACCESS_KEY=...         # Optional: for S3 storage
```

## Unified Wrapper Script (Recommended)

The `run_tasks.py` wrapper script provides a unified interface for running both task types:

### Self-Conversation Tasks

Run models talking to themselves:

```bash
python run_tasks.py self-conversation --model MODEL --iterations N
```

**Options:**
- `--model`: OpenRouter model (required)
- `--iterations`: Number of conversation samples (default: 10)
- `--turns`: Conversation turns per sample (default: 15)
- `--show-convo`: Display conversations as they happen

**Examples:**
```bash
# Run 10 conversations with Claude Haiku
python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 10

# Run 5 conversations with custom turns, showing output
python run_tasks.py self-conversation --model anthropic/claude-sonnet-4.5 --iterations 5 --turns 20 --show-convo
```

### Browser Tasks

Run models browsing Wikipedia with AI agents:

```bash
python run_tasks.py browser --model MODEL --iterations N
```

**Options:**
- `--model`: OpenRouter model (required)
- `--iterations`: Number of browsing sessions (default: 10)
- `--pages`: Minimum pages to browse per session (default: 5)

**Examples:**
```bash
# Run 10 browsing sessions with GPT-4o
python run_tasks.py browser --model openai/gpt-4o --iterations 10

# Run 5 sessions with more pages per session
python run_tasks.py browser --model anthropic/claude-sonnet-4.5 --iterations 5 --pages 10
```

### Supported Models

The wrapper script supports these models:
- `anthropic/claude-sonnet-4.5`
- `anthropic/claude-3.7-sonnet`
- `anthropic/claude-haiku-4.5`
- `openai/gpt-5-mini`
- `openai/gpt-5.1`
- `openai/gpt-4.1`
- `openai/gpt-4o`
- `openai/gpt-5-chat`
- `openai/o3`

## Direct Script Access (Alternative)

You can also run the underlying scripts directly:

### Run conversation mode

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

### Run browsing crew

```bash
uv run src/crew/main.py [OPTIONS]
```

**Options:**
- `--model`: OpenRouter model (default: `anthropic/claude-sonnet-4.5`)
- `--pages`: Minimum number of pages to browse (default: 5)

**Configuration:**
- Temperature: `1.0` (hardcoded)
- Browser headless mode: `false` (visible browser window)
- Logs: `/tmp/browser-agent.log`
- Session logs: `browsing-sessions-<model>-<timestamp>.jsonl`

## Nix/Devenv

```bash
run  # Uses default parameters
```

# Anthropic models

| Model                 | Release Date       | OpenRouter ID                 | MMLU   | GPQA Diamond           | Notes                           |
| --------------------- | ------------------ | ----------------------------- | ------ | ---------------------- | ------------------------------- |
| **Claude 3 Haiku**    | March 2024         | `anthropic/claude-3-haiku`    | N/A    | N/A                    | Fastest, cost-effective         |
| **Claude 3 Sonnet**   | March 2024         | `anthropic/claude-3-sonnet`   | N/A    | N/A                    | Balanced performance            |
| **Claude 3 Opus**     | March 2024         | `anthropic/claude-3-opus`     | 86.8%  | 50.4%                  | Most capable v3                 |
| **Claude 3.5 Sonnet** | June 2024          | `anthropic/claude-3.5-sonnet` | ~79%   | N/A                    | Major improvement               |
| **Claude 3.7 Sonnet** | 2024               | `anthropic/claude-3.7-sonnet` | N/A    | N/A                    | Incremental update              |
| **Claude Sonnet 4**   | May 22, 2025       | `anthropic/claude-sonnet-4`   | 86.5%  | 75.4% (76.1%)          | Free tier model                 |
| **Claude Opus 4**     | May 22, 2025       | `anthropic/claude-opus-4`     | 87-89% | 79.6% (83.3% extended) | Best coding model claim         |
| **Claude Opus 4.1**   | August 5, 2025     | `anthropic/claude-opus-4.1`   | 88.8%  | 81.0%                  | Agentic tasks focus             |
| **Claude Sonnet 4.5** | September 29, 2025 | `anthropic/claude-sonnet-4.5` | 89.1%  | 83.4%                  | Best coding: 77.2% SWE-bench    |
| **Claude Haiku 4.5**  | October 2025       | `anthropic/claude-haiku-4.5`  | N/A    | N/A                    | Fast, coding capable            |
| **Claude Opus 4.5**   | November 24, 2025  | `anthropic/claude-opus-4.5`   | N/A    | N/A                    | Latest flagship, $5/$25 pricing |

# OpenAI Models

| Model              | Release Date   | OpenRouter ID            | MMLU   | GPQA Diamond | Notes                       |
| ------------------ | -------------- | ------------------------ | ------ | ------------ | --------------------------- |
| **GPT-4**          | March 2023     | `openai/gpt-4`           | ~86.5% | ~53.6%       | Original GPT-4              |
| **GPT-4 Turbo**    | November 2023  | `openai/gpt-4-turbo`     | N/A    | N/A          | 128K context                |
| **GPT-4o**         | May 2024       | `openai/gpt-4o`          | 88.7%  | ~53.6%       | Multimodal flagship         |
| **GPT-4.1**        | April 2025     | `openai/gpt-4.1`         | >90%   | ~66%         | 1M context, coding focus    |
| **GPT-4.5**        | 2025           | `openai/gpt-4.5-preview` | N/A    | N/A          | Conversational improvements |
| **o1** (reasoning) | September 2024 | `openai/o1`              | N/A    | N/A          | First reasoning model       |
| **o3**             | December 2024  | `openai/o3`              | 88.8%  | ~79-85%      | Advanced reasoning          |
| **o4-mini**        | 2025           | `openai/o4-mini`         | N/A    | N/A          | Efficient reasoning         |
| **GPT-5**          | November 2025  | `openai/gpt-5`           | ~89%   | 85.7%        | Latest flagship             |
| **GPT-5.1**        | November 2025  | `openai/gpt-5.1`         | N/A    | N/A          | Enhanced version            |

