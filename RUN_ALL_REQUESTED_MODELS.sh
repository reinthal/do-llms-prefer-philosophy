#!/bin/bash
#
# Script to run browser tasks for all requested models
# This runs exactly 10 browser sessions for each of the 9 specified models
#
# Usage: ./RUN_ALL_REQUESTED_MODELS.sh
#

set -euo pipefail

echo "=========================================="
echo "Running Browser Tasks for All Models"
echo "=========================================="
echo "This will run 10 browser sessions for each of 9 models"
echo "Estimated time: 3-6 hours"
echo "Estimated cost: \$50-150"
echo ""
echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
sleep 5

# Check for API key
if [ -z "${OPENROUTER_API_KEY:-}" ]; then
    echo "Error: OPENROUTER_API_KEY not set"
    echo "Please export it or add to secrets.env"
    exit 1
fi

# Create timestamp for this batch run
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="./data/batch_run_${TIMESTAMP}.log"

# Create data directory
mkdir -p ./data

echo "Log file: $LOG_FILE"
echo ""

# Log start time
echo "Batch run started at $(date)" | tee "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Function to run experiments for a model
run_model() {
    local model=$1
    echo "========================================" | tee -a "$LOG_FILE"
    echo "Model: $model" | tee -a "$LOG_FILE"
    echo "Started: $(date)" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"

    if python run_experiments.py browser "$model" -n 10 2>&1 | tee -a "$LOG_FILE"; then
        echo "✓ SUCCESS: $model completed" | tee -a "$LOG_FILE"
    else
        echo "✗ FAILED: $model encountered errors" | tee -a "$LOG_FILE"
    fi

    echo "Completed: $(date)" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# Anthropic Models
echo "==================================================" | tee -a "$LOG_FILE"
echo "ANTHROPIC MODELS (3 models)" | tee -a "$LOG_FILE"
echo "==================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

run_model "anthropic/claude-sonnet-4.5"
run_model "anthropic/claude-3.7-sonnet"
run_model "anthropic/claude-haiku-4.5"

# OpenAI Models
echo "==================================================" | tee -a "$LOG_FILE"
echo "OPENAI MODELS (6 models)" | tee -a "$LOG_FILE"
echo "==================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

run_model "openai/gpt-5-mini"
run_model "openai/gpt-5.1"
run_model "openai/gpt-4.1"
run_model "openai/gpt-4o"
run_model "openai/gpt-5-chat"
run_model "openai/o3"

# Final summary
echo "==================================================" | tee -a "$LOG_FILE"
echo "BATCH RUN COMPLETE" | tee -a "$LOG_FILE"
echo "==================================================" | tee -a "$LOG_FILE"
echo "Completed at: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Count successes and failures
SUCCESS_COUNT=$(grep -c "✓ SUCCESS" "$LOG_FILE" || echo "0")
FAILED_COUNT=$(grep -c "✗ FAILED" "$LOG_FILE" || echo "0")

echo "Summary:" | tee -a "$LOG_FILE"
echo "  Total models: 9" | tee -a "$LOG_FILE"
echo "  Successful: $SUCCESS_COUNT" | tee -a "$LOG_FILE"
echo "  Failed: $FAILED_COUNT" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "Data directory: ./data/" | tee -a "$LOG_FILE"
echo "==================================================" | tee -a "$LOG_FILE"

# List summary files
echo "" | tee -a "$LOG_FILE"
echo "Summary files created:" | tee -a "$LOG_FILE"
find ./data -name "experiment_summary_*.json" -type f -newer "$LOG_FILE" 2>/dev/null | tee -a "$LOG_FILE" || true

echo ""
echo "Done! Check $LOG_FILE for complete logs."
