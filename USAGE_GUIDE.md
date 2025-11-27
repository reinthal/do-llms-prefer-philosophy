# Task Runner Usage Guide

This guide provides comprehensive instructions for using the `run_tasks.py` wrapper script to run both self-conversation and browser tasks.

## Quick Start

```bash
# Self-conversation: Run 10 conversations with Claude Haiku
python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 10

# Browser: Run 10 browsing sessions with GPT-4o
python run_tasks.py browser --model openai/gpt-4o --iterations 10
```

## Prerequisites

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Configure environment variables in `secrets.env`:
   ```bash
   OPENROUTER_API_KEY=your_key_here  # Required
   ```

## Task Types

### 1. Self-Conversation Tasks

Models engage in conversations with themselves to explore preferences and thought patterns.

**Basic Syntax:**
```bash
python run_tasks.py self-conversation --model MODEL --iterations N [OPTIONS]
```

**Parameters:**
- `--model` (required): OpenRouter model identifier
- `--iterations`: Number of conversation samples to generate (default: 10)
- `--turns`: Number of conversation turns per sample (default: 15)
- `--show-convo`: Display conversations as they happen (optional flag)

**Examples:**

```bash
# Basic: 10 conversations with default settings
python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 10

# Custom: 5 conversations with 20 turns each, showing output
python run_tasks.py self-conversation \
  --model anthropic/claude-sonnet-4.5 \
  --iterations 5 \
  --turns 20 \
  --show-convo

# Quick test: 1 conversation with 5 turns
python run_tasks.py self-conversation \
  --model openai/gpt-4o \
  --iterations 1 \
  --turns 5 \
  --show-convo
```

**Output:**
- JSONL file: `do-llms-prefer-philosophy-{model}-{timestamp}-{turns}.jsonl`
- Cost summary displayed at the end
- Each conversation logged with metadata

### 2. Browser Tasks

Models browse Wikipedia using AI agents with interactive sessions.

**Basic Syntax:**
```bash
python run_tasks.py browser --model MODEL --iterations N [OPTIONS]
```

**Parameters:**
- `--model` (required): OpenRouter model identifier
- `--iterations`: Number of browsing sessions to run (default: 10)
- `--pages`: Minimum number of pages to browse per session (default: 5)

**Examples:**

```bash
# Basic: 10 browsing sessions with default settings
python run_tasks.py browser --model openai/gpt-4o --iterations 10

# Custom: 5 sessions with more pages
python run_tasks.py browser \
  --model anthropic/claude-sonnet-4.5 \
  --iterations 5 \
  --pages 10

# Quick test: 1 session
python run_tasks.py browser \
  --model anthropic/claude-haiku-4.5 \
  --iterations 1 \
  --pages 3
```

**Interactive Options:**
For each browsing session, you can choose:
1. Free exploration (agent chooses what to browse)
2. Guided exploration (you provide a topic)
3. View session log
4. Exit

**Output:**
- Session logs: `browsing-sessions-{model}-{timestamp}.jsonl`
- Browser agent log: `/tmp/browser-agent.log`
- Interactive terminal output

## Supported Models

### Anthropic Models
- `anthropic/claude-sonnet-4.5` - Latest flagship, best coding performance
- `anthropic/claude-3.7-sonnet` - Incremental update
- `anthropic/claude-haiku-4.5` - Fast and cost-effective

### OpenAI Models
- `openai/gpt-5-mini` - Efficient variant
- `openai/gpt-5.1` - Enhanced version
- `openai/gpt-4.1` - 1M context, coding focus
- `openai/gpt-4o` - Multimodal flagship
- `openai/gpt-5-chat` - Conversational improvements
- `openai/o3` - Advanced reasoning

## Running All Iterations for a Model

### Example: Complete Dataset for Claude Haiku 4.5

```bash
# Self-conversation: 10 samples
python run_tasks.py self-conversation \
  --model anthropic/claude-haiku-4.5 \
  --iterations 10

# Browser: 10 sessions
python run_tasks.py browser \
  --model anthropic/claude-haiku-4.5 \
  --iterations 10
```

### Example: Complete Dataset for GPT-4o

```bash
# Self-conversation: 10 samples
python run_tasks.py self-conversation \
  --model openai/gpt-4o \
  --iterations 10

# Browser: 10 sessions
python run_tasks.py browser \
  --model openai/gpt-4o \
  --iterations 10
```

### Example: Quick Test Run

```bash
# Test self-conversation with 2 samples
python run_tasks.py self-conversation \
  --model anthropic/claude-haiku-4.5 \
  --iterations 2 \
  --turns 5 \
  --show-convo

# Test browser with 2 sessions
python run_tasks.py browser \
  --model anthropic/claude-haiku-4.5 \
  --iterations 2 \
  --pages 3
```

## Running Multiple Models

### Bash Script Example

Create a script to run all models:

```bash
#!/bin/bash
# run_all_models.sh

MODELS=(
    "anthropic/claude-sonnet-4.5"
    "anthropic/claude-3.7-sonnet"
    "anthropic/claude-haiku-4.5"
    "openai/gpt-5-mini"
    "openai/gpt-5.1"
    "openai/gpt-4.1"
    "openai/gpt-4o"
    "openai/gpt-5-chat"
    "openai/o3"
)

for model in "${MODELS[@]}"; do
    echo "=========================================="
    echo "Running self-conversation for $model"
    echo "=========================================="
    python run_tasks.py self-conversation --model "$model" --iterations 10

    echo ""
    echo "=========================================="
    echo "Running browser for $model"
    echo "=========================================="
    python run_tasks.py browser --model "$model" --iterations 10
    echo ""
done
```

## Troubleshooting

### Common Issues

1. **Missing API Key**
   ```
   Error: OPENROUTER_API_KEY environment variable not set
   ```
   Solution: Configure `secrets.env` with your OpenRouter API key

2. **Model Not Found**
   ```
   Warning: Model 'xyz' is not in the standard list.
   ```
   Solution: Check the supported models list or verify the model ID

3. **Browser Task Interrupted**
   - Browser tasks are interactive and require user input
   - Press Ctrl+C to interrupt if needed
   - Sessions are logged incrementally

### Getting Help

```bash
# General help
python run_tasks.py --help

# Self-conversation help
python run_tasks.py self-conversation --help

# Browser help
python run_tasks.py browser --help
```

## Cost Estimation

Self-conversation tasks display actual costs from OpenRouter:
- Input tokens (native count)
- Output tokens (native count)
- Total cost in USD
- Cost per conversation
- Average cost per turn

Plan your budget accordingly based on:
- Model pricing (varies significantly)
- Number of iterations
- Number of turns (self-conversation only)
- Number of pages (browser only)

## Output Files

### Self-Conversation
- Format: `do-llms-prefer-philosophy-{model}-{timestamp}-{turns}.jsonl`
- Each line contains:
  - `input`: Array of conversation messages
  - `id`: Timestamp
  - `choices`: Available classifications
  - `metadata`: Model configuration

### Browser
- Format: `browsing-sessions-{model}-{timestamp}.jsonl`
- Each line contains:
  - `timestamp`: ISO format
  - `session_type`: "Free Exploration" or "Guided Browsing"
  - `user_input`: Topic (if guided)
  - `result`: Browsing report
  - `model`: Model identifier

## Tips for Efficient Running

1. **Start Small**: Test with 1-2 iterations first
2. **Use Show Convo**: Add `--show-convo` for debugging
3. **Monitor Costs**: Check cost summaries after each run
4. **Batch Processing**: Use shell scripts for multiple models
5. **Log Review**: Check `/tmp/browser-agent.log` for browser issues
