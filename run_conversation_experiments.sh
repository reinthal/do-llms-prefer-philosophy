#!/nix/store/gkwbw9nzbkbz298njbn3577zmrnglbbi-bash-5.3p0/bin/bash
#
# Shell wrapper for running conversation experiments
# Usage: ./run_conversation_experiments.sh <model> [iterations] [turns]
#

set -euo pipefail

# Default values
MODEL="${1:-anthropic/claude-haiku-4.5}"
ITERATIONS="${2:-10}"
TURNS="${3:-15}"

echo "=========================================="
echo "Running Conversation Experiments"
echo "=========================================="
echo "Model: $MODEL"
echo "Iterations: $ITERATIONS"
echo "Turns per conversation: $TURNS"
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
python run_experiments.py conversation "$MODEL" \
        -n "$ITERATIONS" \
        --turns "$TURNS" \
        --output ./data

echo ""
echo "=========================================="
echo "Experiments complete!"
echo "Check ./data for results"
echo "=========================================="
