# Quick Reference: Example Commands

This document provides ready-to-use commands for running tasks with each supported model.

## Self-Conversation Tasks (10 iterations each)

### Anthropic Models

```bash
# Claude Sonnet 4.5
python run_tasks.py self-conversation --model anthropic/claude-sonnet-4.5 --iterations 10

# Claude 3.7 Sonnet
python run_tasks.py self-conversation --model anthropic/claude-3.7-sonnet --iterations 10

# Claude Haiku 4.5
python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 10
```

### OpenAI Models

```bash
# GPT-5-mini
python run_tasks.py self-conversation --model openai/gpt-5-mini --iterations 10

# GPT-5.1
python run_tasks.py self-conversation --model openai/gpt-5.1 --iterations 10

# GPT-4.1
python run_tasks.py self-conversation --model openai/gpt-4.1 --iterations 10

# GPT-4o
python run_tasks.py self-conversation --model openai/gpt-4o --iterations 10

# GPT-5-chat
python run_tasks.py self-conversation --model openai/gpt-5-chat --iterations 10

# o3
python run_tasks.py self-conversation --model openai/o3 --iterations 10
```

## Browser Tasks (10 iterations each)

### Anthropic Models

```bash
# Claude Sonnet 4.5
python run_tasks.py browser --model anthropic/claude-sonnet-4.5 --iterations 10

# Claude 3.7 Sonnet
python run_tasks.py browser --model anthropic/claude-3.7-sonnet --iterations 10

# Claude Haiku 4.5
python run_tasks.py browser --model anthropic/claude-haiku-4.5 --iterations 10
```

### OpenAI Models

```bash
# GPT-5-mini
python run_tasks.py browser --model openai/gpt-5-mini --iterations 10

# GPT-5.1
python run_tasks.py browser --model openai/gpt-5.1 --iterations 10

# GPT-4.1
python run_tasks.py browser --model openai/gpt-4.1 --iterations 10

# GPT-4o
python run_tasks.py browser --model openai/gpt-4o --iterations 10

# GPT-5-chat
python run_tasks.py browser --model openai/gpt-5-chat --iterations 10

# o3
python run_tasks.py browser --model openai/o3 --iterations 10
```

## Running All Models (Batch Script)

Save this as `run_all.sh`:

```bash
#!/bin/bash
# Run all models for both task types with 10 iterations each

set -e  # Exit on error

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

LOG_FILE="batch_run_$(date +%Y%m%d_%H%M%S).log"

echo "Starting batch run at $(date)" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

for model in "${MODELS[@]}"; do
    echo "========================================" | tee -a "$LOG_FILE"
    echo "Processing: $model" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"

    echo "Task 1/2: Self-conversation" | tee -a "$LOG_FILE"
    python run_tasks.py self-conversation --model "$model" --iterations 10 2>&1 | tee -a "$LOG_FILE"

    echo "" | tee -a "$LOG_FILE"
    echo "Task 2/2: Browser" | tee -a "$LOG_FILE"
    python run_tasks.py browser --model "$model" --iterations 10 2>&1 | tee -a "$LOG_FILE"

    echo "" | tee -a "$LOG_FILE"
    echo "Completed: $model" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
done

echo "========================================" | tee -a "$LOG_FILE"
echo "Batch run completed at $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
```

Make it executable:
```bash
chmod +x run_all.sh
./run_all.sh
```

## Custom Configurations

### More Turns Per Conversation

```bash
# 20 turns instead of default 15
python run_tasks.py self-conversation \
  --model anthropic/claude-haiku-4.5 \
  --iterations 10 \
  --turns 20
```

### More Pages Per Browser Session

```bash
# 10 pages instead of default 5
python run_tasks.py browser \
  --model openai/gpt-4o \
  --iterations 10 \
  --pages 10
```

### Show Conversations in Real-Time

```bash
# See the conversation as it happens
python run_tasks.py self-conversation \
  --model anthropic/claude-sonnet-4.5 \
  --iterations 10 \
  --show-convo
```

## Quick Testing

### Test All Task Types with One Model

```bash
# Test with Claude Haiku (fast and cheap)
echo "Testing self-conversation..."
python run_tasks.py self-conversation \
  --model anthropic/claude-haiku-4.5 \
  --iterations 1 \
  --turns 5 \
  --show-convo

echo "Testing browser..."
python run_tasks.py browser \
  --model anthropic/claude-haiku-4.5 \
  --iterations 1 \
  --pages 3
```

### Minimal Test Run

```bash
# Fastest possible test
python run_tasks.py self-conversation \
  --model anthropic/claude-haiku-4.5 \
  --iterations 1 \
  --turns 3

python run_tasks.py browser \
  --model anthropic/claude-haiku-4.5 \
  --iterations 1 \
  --pages 2
```

## Model-Specific Recommendations

### For Budget-Conscious Runs
```bash
# Use Claude Haiku 4.5 (most cost-effective)
python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 10
python run_tasks.py browser --model anthropic/claude-haiku-4.5 --iterations 10
```

### For Best Performance
```bash
# Use Claude Sonnet 4.5 (best coding/reasoning)
python run_tasks.py self-conversation --model anthropic/claude-sonnet-4.5 --iterations 10
python run_tasks.py browser --model anthropic/claude-sonnet-4.5 --iterations 10
```

### For Reasoning Tasks
```bash
# Use o3 (advanced reasoning)
python run_tasks.py self-conversation --model openai/o3 --iterations 10
python run_tasks.py browser --model openai/o3 --iterations 10
```

## Parallel Execution

Run multiple models in parallel (be mindful of API rate limits):

```bash
# Run 3 models in parallel
python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 10 &
python run_tasks.py self-conversation --model anthropic/claude-sonnet-4.5 --iterations 10 &
python run_tasks.py self-conversation --model openai/gpt-4o --iterations 10 &

# Wait for all to complete
wait

echo "All parallel tasks completed"
```

## Help Commands

```bash
# Main help
python run_tasks.py --help

# Self-conversation help
python run_tasks.py self-conversation --help

# Browser help
python run_tasks.py browser --help
```
