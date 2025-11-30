# Quick Start - Running Experiments

## Setup (One Time)

```bash
# 1. Install dependencies
uv sync

# 2. Set API key
export OPENROUTER_API_KEY=your_key_here

# 3. Test everything works
python run_experiments.py browser anthropic/claude-haiku-4.5 -n 1 -v
```

## Common Commands

### Single Model - 10 Iterations

```bash
# Browser tasks
python run_experiments.py browser anthropic/claude-sonnet-4.5

# Conversation tasks
python run_experiments.py conversation openai/gpt-5
```

### All Anthropic Models

```bash
# Browser
python run_all_models.py browser --group anthropic

# Conversation
python run_all_models.py conversation --group anthropic
```

### All OpenAI Models

```bash
# Browser
python run_all_models.py browser --group openai

# Conversation
python run_all_models.py conversation --group openai
```

### All Models

```bash
# Browser (expensive!)
python run_all_models.py browser --group all

# Conversation
python run_all_models.py conversation --group all
```

### Custom Settings

```bash
# 5 iterations, 10 pages each
python run_experiments.py browser anthropic/claude-haiku-4.5 -n 5 --pages 10

# 20 iterations, 20 turns each
python run_experiments.py conversation openai/gpt-5.1 -n 20 --turns 20

# Verbose output
python run_experiments.py browser openai/o3 -n 2 -v
```

## Supported Models

**Anthropic:**
- `anthropic/claude-sonnet-4.5`
- `anthropic/claude-3.7-sonnet`
- `anthropic/claude-haiku-4.5`

**OpenAI:**
- `openai/gpt-5-mini`
- `openai/gpt-5.1`
- `openai/gpt-4.1`
- `openai/gpt-4o`
- `openai/gpt-5-chat`
- `openai/o3`

## Output

Results saved to: `./data/`

Summary files: `./data/experiment_summary_*.json`

## Help

```bash
# Script help
python run_experiments.py --help
python run_all_models.py --help

# Full documentation
cat EXPERIMENTS_GUIDE.md
```

## Quick Testing

```bash
# Fast test with Haiku (cheap, fast)
python run_experiments.py browser anthropic/claude-haiku-4.5 -n 1 --pages 3 -v
python run_experiments.py conversation anthropic/claude-haiku-4.5 -n 1 --turns 5 -v
```
