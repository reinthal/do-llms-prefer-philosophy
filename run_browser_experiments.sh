#!/bin/bash
#
# Shell wrapper for running browser experiments
# Usage: ./run_browser_experiments.sh <model> [iterations] [pages]
#

set -euo pipefail

# Default values
MODEL="${1:-anthropic/claude-haiku-4.5}"
ITERATIONS="${2:-10}"
PAGES="${3:-5}"

echo "=========================================="
echo "Running Browser Experiments"
echo "=========================================="
echo "Model: $MODEL"
echo "Iterations: $ITERATIONS"
echo "Pages per session: $PAGES"
echo "=========================================="
echo ""

# Check for API key
if [ -z "${OPENROUTER_API_KEY:-}" ]; then
    echo "Error: OPENROUTER_API_KEY not set"
    echo "Please export it or add to secrets.env"
    exit 1
fi

# Create data directory
mkdir -p ./data

# Run experiments
python run_experiments.py browser "$MODEL" \
    -n "$ITERATIONS" \
    --pages "$PAGES" \
    --output ./data

echo ""
echo "=========================================="
echo "Experiments complete!"
echo "Check ./data for results"
echo "=========================================="
