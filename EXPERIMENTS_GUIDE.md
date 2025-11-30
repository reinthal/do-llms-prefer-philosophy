# Experiment Runner Guide

This guide explains how to use the experiment wrapper scripts to run browser and conversation tasks across multiple models.

## Overview

Two main scripts are provided:

1. **`run_experiments.py`** - Run multiple iterations of a task for a single model
2. **`run_all_models.py`** - Run experiments across multiple models in batch

## Quick Start

### Single Model Experiments

Run 10 browser tasks for Claude Sonnet 4.5:
```bash
python run_experiments.py browser anthropic/claude-sonnet-4.5
```

Run 10 conversation tasks for GPT-5:
```bash
python run_experiments.py conversation openai/gpt-5
```

### Multiple Models (Batch)

Run browser tasks for all Anthropic models:
```bash
python run_all_models.py browser --group anthropic
```

Run conversation tasks for all OpenAI models:
```bash
python run_all_models.py conversation --group openai
```

Run for all supported models:
```bash
python run_all_models.py browser --group all
```

## Supported Models

### Anthropic Models
- `anthropic/claude-sonnet-4.5` - Latest Sonnet (best coding: 77.2% SWE-bench)
- `anthropic/claude-3.7-sonnet` - Incremental update
- `anthropic/claude-haiku-4.5` - Fast, coding capable

### OpenAI Models
- `openai/gpt-5-mini` - Efficient variant
- `openai/gpt-5.1` - Enhanced version
- `openai/gpt-4.1` - 1M context, coding focus
- `openai/gpt-4o` - Multimodal flagship
- `openai/gpt-5-chat` - Conversational improvements
- `openai/o3` - Advanced reasoning model

## Script 1: run_experiments.py

Run multiple iterations of browser or conversation tasks for a single model.

### Usage

```bash
python run_experiments.py <task_type> <model> [options]
```

### Arguments

- `task_type` - Type of task: `browser` or `conversation`
- `model` - Model to use (e.g., `anthropic/claude-sonnet-4.5`)

### Options

- `-n, --iterations N` - Number of iterations (default: 10)
- `--output DIR` - Output directory (default: ./data)
- `--pages N` - Min pages to browse (browser tasks only, default: 5)
- `--turns N` - Conversation turns (conversation tasks only, default: 15)
- `-v, --verbose` - Show detailed output

### Examples

#### Browser Tasks

```bash
# Basic: 10 browser tasks with default settings
python run_experiments.py browser anthropic/claude-sonnet-4.5

# Custom: 5 iterations, browsing 10 pages each
python run_experiments.py browser openai/gpt-4o -n 5 --pages 10

# Verbose output
python run_experiments.py browser anthropic/claude-haiku-4.5 -v

# Custom output directory
python run_experiments.py browser openai/gpt-5 --output ./my_experiments
```

#### Conversation Tasks

```bash
# Basic: 10 conversations with default settings
python run_experiments.py conversation anthropic/claude-sonnet-4.5

# Custom: 20 turns per conversation
python run_experiments.py conversation openai/gpt-5.1 --turns 20

# Short conversations for quick testing
python run_experiments.py conversation anthropic/claude-haiku-4.5 -n 5 --turns 10

# Verbose to see conversations
python run_experiments.py conversation openai/o3 -v --turns 15
```

### Output

The script creates:

1. **Data files** in the output directory:
   - Browser: `browsing-sessions-{model}-{timestamp}_iter{N}.jsonl`
   - Conversation: `do-llms-prefer-philosophy-{model}-{timestamp}_iter{N}.jsonl`

2. **Summary file**: `experiment_summary_{task_type}_{model}_{timestamp}.json`
   - Configuration details
   - Results for each iteration
   - Success/failure statistics

## Script 2: run_all_models.py

Run experiments across multiple models in batch.

### Usage

```bash
python run_all_models.py <task_type> --group <group> [options]
# OR
python run_all_models.py <task_type> -m <model1> <model2> ... [options]
```

### Arguments

- `task_type` - Type of task: `browser` or `conversation`
- `--group` - Model group: `anthropic`, `openai`, or `all`
- `-m, --models` - Specific models (space-separated)

### Options

- `-n, --iterations N` - Iterations per model (default: 10)
- `--output DIR` - Output directory (default: ./data)
- `--pages N` - Min pages to browse (browser tasks only, default: 5)
- `--turns N` - Conversation turns (conversation tasks only, default: 15)
- `-v, --verbose` - Show detailed output
- `--continue-on-error` - Don't stop if a model fails

### Examples

#### Run All Models

```bash
# Browser tasks for all models
python run_all_models.py browser --group all

# Conversation tasks for all models (5 iterations each)
python run_all_models.py conversation --group all -n 5
```

#### Run by Model Group

```bash
# All Anthropic models
python run_all_models.py browser --group anthropic

# All OpenAI models with verbose output
python run_all_models.py conversation --group openai -v

# Continue even if some models fail
python run_all_models.py browser --group all --continue-on-error
```

#### Run Specific Models

```bash
# Two specific models
python run_all_models.py browser -m anthropic/claude-sonnet-4.5 openai/gpt-5

# Multiple models with custom settings
python run_all_models.py conversation -m \
  anthropic/claude-sonnet-4.5 \
  openai/gpt-5.1 \
  openai/o3 \
  --turns 20 -n 5
```

## Understanding Task Types

### Browser Tasks

Browser tasks use the CrewAI browsing agents to:
- Navigate Wikipedia or other websites
- Read and explore multiple pages
- Generate a report of the browsing session

**Configuration:**
- `--pages`: Minimum number of pages to browse (default: 5)
- Each iteration runs one complete browsing session

**Output:** JSONL file with session data including:
- Timestamp
- User input (if any)
- Browsing result/report
- Model name

### Conversation Tasks

Conversation tasks create self-conversations:
- Two instances of the same model talk to each other
- Discussions are open-ended and unguided
- No evaluation or scoring

**Configuration:**
- `--turns`: Number of conversation exchanges (default: 15)
- Each iteration generates 1 conversation sample

**Output:** JSONL file with:
- Complete conversation history
- Model metadata (name, temperature, system prompt)
- Unique conversation ID

## Output Structure

### Directory Layout

```
./data/
├── browsing-sessions-anthropic-claude-sonnet-4.5-1234567890_iter1.jsonl
├── browsing-sessions-anthropic-claude-sonnet-4.5-1234567890_iter2.jsonl
├── ...
├── do-llms-prefer-philosophy-openai-gpt-5-1234567890_iter1.jsonl
├── do-llms-prefer-philosophy-openai-gpt-5-1234567890_iter2.jsonl
├── ...
├── experiment_summary_browser_anthropic-claude-sonnet-4.5_20251127_123456.json
└── experiment_summary_conversation_openai-gpt-5_20251127_123456.json
```

### Summary File Format

```json
{
  "config": {
    "task_type": "browser",
    "model": "anthropic/claude-sonnet-4.5",
    "iterations": 10,
    "min_pages": 5,
    "turns": 15
  },
  "results": [
    {
      "iteration": 1,
      "task_type": "browser",
      "model": "anthropic/claude-sonnet-4.5",
      "timestamp": "2025-11-27T14:30:00",
      "success": true,
      "error": null,
      "output_files": ["./data/browsing-sessions-...jsonl"]
    }
  ],
  "statistics": {
    "total_runs": 10,
    "successful": 10,
    "failed": 0
  }
}
```

## Environment Setup

### Prerequisites

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set environment variables:**
   ```bash
   export OPENROUTER_API_KEY=your_api_key_here
   ```
   Or add to `secrets.env`:
   ```
   OPENROUTER_API_KEY=your_key_here
   ```

3. **For browser tasks, install Playwright:**
   ```bash
   npx -y @playwright/mcp@latest
   ```

### Verification

Check that everything is set up:
```bash
# Check uv is installed
uv --version

# Check environment variable
echo $OPENROUTER_API_KEY

# Test single browser task
python run_experiments.py browser anthropic/claude-haiku-4.5 -n 1 -v

# Test single conversation task
python run_experiments.py conversation anthropic/claude-haiku-4.5 -n 1 -v
```

## Tips and Best Practices

### Performance Optimization

1. **Start small:** Test with `-n 1` or `-n 2` before running full experiments
2. **Use Haiku for testing:** Faster and cheaper than Sonnet models
3. **Monitor costs:** Check OpenRouter dashboard regularly

### Error Handling

1. **Timeouts:** Each task has a 30-minute timeout
2. **Failed runs:** Check the summary JSON for error details
3. **Continue on error:** Use `--continue-on-error` for batch runs
4. **Logs:** Browser tasks log to `/tmp/browser-agent.log`

### Resource Management

1. **Browser tasks:** More resource-intensive (Playwright, MCP server)
2. **Conversation tasks:** Lighter weight, faster execution
3. **Parallel execution:** Don't run multiple scripts simultaneously
4. **Disk space:** Monitor `./data` directory size

### Debugging

```bash
# Verbose output for troubleshooting
python run_experiments.py browser anthropic/claude-haiku-4.5 -n 1 -v

# Check browser logs
tail -f /tmp/browser-agent.log

# Test with minimal settings
python run_experiments.py conversation anthropic/claude-haiku-4.5 \
  -n 1 --turns 3 -v
```

## Common Use Cases

### Research Data Collection

Collect browsing data from multiple models:
```bash
python run_all_models.py browser --group all -n 10 --pages 10
```

### Model Comparison

Compare conversation styles:
```bash
python run_all_models.py conversation \
  -m anthropic/claude-sonnet-4.5 openai/gpt-5 \
  -n 20 --turns 15
```

### Quick Testing

Test new model quickly:
```bash
python run_experiments.py browser openai/new-model -n 2 --pages 3 -v
```

### Production Data Collection

Large-scale data collection with error handling:
```bash
python run_all_models.py browser --group all \
  -n 50 \
  --pages 10 \
  --continue-on-error \
  --output ./production_data
```

## Troubleshooting

### "OPENROUTER_API_KEY not set"
```bash
export OPENROUTER_API_KEY=your_key_here
# Or add to secrets.env
```

### "'uv' command not found"
```bash
# Install uv first
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Browser tasks timeout
- Reduce `--pages` value
- Check internet connection
- Verify Playwright is installed: `npx -y @playwright/mcp@latest`

### Model not found
- Check model name spelling
- Verify model is available on OpenRouter
- Check OpenRouter API status

### Out of memory
- Reduce iterations (`-n`)
- Run models separately instead of batch
- Close other applications

## Advanced Usage

### Custom Model Lists

Edit `run_all_models.py` to add custom model groups:

```python
CUSTOM_MODELS = [
    "anthropic/claude-sonnet-4.5",
    "openai/gpt-5",
    "custom/model-name",
]
```

### Integration with Analysis

The output files are ready for analysis:

```python
import json

# Load experiment summary
with open("data/experiment_summary_browser_....json") as f:
    summary = json.load(f)

# Load browsing sessions
with open("data/browsing-sessions-....jsonl") as f:
    sessions = [json.loads(line) for line in f]

# Analyze results...
```

### Automated Pipelines

Chain experiments together:

```bash
#!/bin/bash
# Run browser tasks for all models
python run_all_models.py browser --group all -n 10

# Run conversation tasks for all models
python run_all_models.py conversation --group all -n 10

# Process results
python analyze_results.py ./data
```

## Cost Estimation

Approximate costs per iteration (varies by model):

| Model | Browser Task | Conversation (15 turns) |
|-------|-------------|------------------------|
| claude-haiku-4.5 | $0.05-0.15 | $0.02-0.05 |
| claude-sonnet-4.5 | $0.20-0.50 | $0.10-0.20 |
| gpt-4o | $0.30-0.60 | $0.15-0.30 |
| gpt-5 | $0.40-0.80 | $0.20-0.40 |

10 iterations for all models (9 models): ~$50-150 depending on task type

**Always monitor your OpenRouter dashboard for actual costs!**
