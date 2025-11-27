# Quick Start Guide

Get started running tasks in under 5 minutes.

## Prerequisites

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set up API key:**
   ```bash
   echo "OPENROUTER_API_KEY=your_key_here" > secrets.env
   ```

## Running Your First Task

### Self-Conversation (Fastest)

```bash
# Run 10 conversations with Claude Haiku (fast & cheap)
python run_tasks.py self-conversation \
  --model anthropic/claude-haiku-4.5 \
  --iterations 10
```

**What happens:**
- 10 conversations will be generated
- Each conversation has 15 turns (configurable with `--turns`)
- Output saved to `do-llms-prefer-philosophy-*.jsonl`
- Cost summary displayed at the end

**Time estimate:** ~5-10 minutes for 10 iterations

### Browser Task (Interactive)

```bash
# Run 10 browsing sessions with GPT-4o
python run_tasks.py browser \
  --model openai/gpt-4o \
  --iterations 10
```

**What happens:**
- You'll complete 10 interactive browsing sessions
- Each session: choose free exploration or provide a topic
- Agent browses Wikipedia (minimum 5 pages per session)
- Session logs saved to `browsing-sessions-*.jsonl`

**Time estimate:** ~15-30 minutes for 10 iterations (depends on interaction)

## Testing Before Full Run

Always test with a small run first:

```bash
# Test self-conversation (1 iteration, 5 turns, show output)
python run_tasks.py self-conversation \
  --model anthropic/claude-haiku-4.5 \
  --iterations 1 \
  --turns 5 \
  --show-convo

# Test browser (1 iteration, 3 pages)
python run_tasks.py browser \
  --model anthropic/claude-haiku-4.5 \
  --iterations 1 \
  --pages 3
```

**Time estimate:** ~1-2 minutes total

## Common Commands

### Run All Models (Both Task Types)

```bash
# Use the batch script
./run_all.sh

# This runs 9 models × 2 task types × 10 iterations each
# Total: 180 task executions
# Estimated time: Several hours
```

### Run Specific Model with Custom Settings

```bash
# Self-conversation: 20 iterations, 20 turns each
python run_tasks.py self-conversation \
  --model anthropic/claude-sonnet-4.5 \
  --iterations 20 \
  --turns 20

# Browser: 15 iterations, 10 pages each
python run_tasks.py browser \
  --model openai/gpt-4.1 \
  --iterations 15 \
  --pages 10
```

## Understanding Output

### Self-Conversation Output

**File:** `do-llms-prefer-philosophy-{model}-{timestamp}-{turns}.jsonl`

Each line contains:
```json
{
  "input": ["message1", "message2", ...],
  "id": 1234567890.123,
  "choices": ["philosophy", "not philosophy"],
  "metadata": {
    "model_name": "anthropic/claude-haiku-4.5",
    "temperature": 1.0,
    "system_prompt": "..."
  }
}
```

**Terminal Output:**
```
Generating 10 conversations with 15 turns each
Using model: anthropic/claude-haiku-4.5
...
============================================================
COST SUMMARY (Actual OpenRouter Costs)
============================================================
Total Input Tokens:    50,000 (native count)
Total Output Tokens:   75,000 (native count)
Total Cost:            $0.125000
============================================================
```

### Browser Output

**File:** `browsing-sessions-{model}-{timestamp}.jsonl`

Each line contains:
```json
{
  "timestamp": "2025-11-27T20:30:00",
  "session_type": "Free Exploration",
  "user_input": "",
  "result": "Browsing report...",
  "model": "openai/gpt-4o"
}
```

**Additional Logs:**
- `/tmp/browser-agent.log` - Detailed browser agent activity

## Getting Help

```bash
# Main help
python run_tasks.py --help

# Task-specific help
python run_tasks.py self-conversation --help
python run_tasks.py browser --help
```

## Next Steps

1. **Review the full guide:** See `USAGE_GUIDE.md` for detailed documentation
2. **See all examples:** Check `EXAMPLES.md` for model-specific commands
3. **Run full dataset:** Use `./run_all.sh` to run all models
4. **Analyze results:** Use `evaluate_trajectories.py` to analyze output

## Troubleshooting

### API Key Not Found
```
Error: OPENROUTER_API_KEY environment variable not set
```
**Solution:** Create or update `secrets.env` with your API key

### Model Not Recognized
```
Warning: Model 'xyz' is not in the standard list.
```
**Solution:** Check model ID matches OpenRouter format (e.g., `anthropic/claude-haiku-4.5`)

### Task Interrupted
Press `Ctrl+C` to interrupt any running task. Sessions are logged incrementally.

## Cost Estimates

**Self-Conversation (10 iterations, 15 turns each):**
- Claude Haiku 4.5: ~$0.10-0.20
- Claude Sonnet 4.5: ~$1.50-3.00
- GPT-4o: ~$2.00-4.00

**Browser (10 iterations, 5 pages each):**
- Variable based on pages visited and agent activity
- Generally 2-3x more than self-conversation

**Always start with test runs to estimate costs for your use case.**

## Recommended Workflow

1. **Test with Haiku** (cheap & fast)
   ```bash
   python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 1 --turns 5 --show-convo
   ```

2. **Run small batch** (2-3 iterations)
   ```bash
   python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 3
   ```

3. **Review output** (check JSONL files)

4. **Run full dataset** (10+ iterations)
   ```bash
   python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 10
   python run_tasks.py browser --model anthropic/claude-haiku-4.5 --iterations 10
   ```

5. **Scale to other models**
   ```bash
   ./run_all.sh
   ```
