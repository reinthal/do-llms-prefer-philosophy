#!/bin/bash
# Run all models for both task types with 10 iterations each
# Usage: ./run_all.sh

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

    echo "Task 1/2: Self-conversation (10 iterations)" | tee -a "$LOG_FILE"
    python run_tasks.py self-conversation --model "$model" --iterations 10 2>&1 | tee -a "$LOG_FILE"

    echo "" | tee -a "$LOG_FILE"
    echo "Task 2/2: Browser (10 iterations)" | tee -a "$LOG_FILE"
    echo "Note: Browser tasks are interactive - follow the prompts" | tee -a "$LOG_FILE"
    python run_tasks.py browser --model "$model" --iterations 10 2>&1 | tee -a "$LOG_FILE"

    echo "" | tee -a "$LOG_FILE"
    echo "Completed: $model" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
done

echo "========================================" | tee -a "$LOG_FILE"
echo "Batch run completed at $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
