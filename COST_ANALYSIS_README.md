# Token Cost Analysis Tools

This directory contains tools for analyzing token usage and calculating costs for self-conversation tasks.

## Overview

Two Python scripts are provided for cost analysis:

1. **`calculate_token_costs.py`** - Basic token cost calculator
2. **`analyze_costs.py`** - Advanced analysis with CSV export and model comparison

## Installation

Both scripts use `tiktoken` for accurate token counting. Install it with:

```bash
pip install tiktoken
```

If `tiktoken` is not installed, the scripts will fall back to character-based estimation (less accurate).

## Usage

### Basic Cost Calculator

```bash
# Analyze all files in ./data directory
python3 calculate_token_costs.py

# Analyze specific files
python3 calculate_token_costs.py file1.jsonl file2.jsonl

# Use custom data directory
python3 calculate_token_costs.py --data-dir ./custom_data

# Show only summary (skip per-file details)
python3 calculate_token_costs.py --summary-only

# Verbose output
python3 calculate_token_costs.py --verbose
```

### Advanced Cost Analyzer

```bash
# Full analysis with model comparison
python3 analyze_costs.py --compare-models

# Export detailed results to CSV
python3 analyze_costs.py --output-csv cost_analysis.csv

# Compare models with different turn counts
python3 analyze_costs.py --compare-models --turns 15

# Custom data directory
python3 analyze_costs.py --data-dir ./custom_data
```

## Output

### Basic Calculator Output

- Total prompt (input) tokens
- Total completion (output) tokens
- Total tokens
- Estimated costs (input, output, total)
- Cost per conversation
- Projections for 10, 100, and 1,000 conversations

### Advanced Analyzer Output

**Model Comparison:**
- Side-by-side cost comparison across all models
- Projections for 1, 10, 100, and 1,000 conversations
- Based on estimated token usage for target turn count

**Detailed Analysis:**
- Per-model statistics
- Token usage patterns
- Message length statistics
- Cost projections

**CSV Export:**
- Per-conversation breakdown
- Token counts (prompt, completion, total)
- Cost breakdown (input, output, total)
- Message statistics (avg, max, min length)

## Model Pricing

Current pricing per million tokens (as of 2025):

| Model | Input Cost | Output Cost |
|-------|------------|-------------|
| Claude Haiku 4/4.5 | $0.25 | $1.25 |
| Claude Sonnet 4 | $3.00 | $15.00 |
| Claude 3.5 Sonnet | $3.00 | $15.00 |
| Claude Opus 4 | $15.00 | $75.00 |
| GPT-4 Turbo | $10.00 | $30.00 |
| GPT-4 | $30.00 | $60.00 |
| Llama 3.3 70B | $0.35 | $0.40 |
| Gemini 2.0 Flash | $0.00 | $0.00 |

## Example Results

Based on the current dataset (10 conversations with Claude Haiku 4.5, 9 turns each):

```
Total Conversations: 10
Total Cost: $0.080509
Average Cost per Conversation: $0.008051

Cost Projections:
  10 conversations:    $0.0805
  100 conversations:   $0.8051
  1,000 conversations: $8.05
  10,000 conversations: $80.51

Token Statistics (per conversation):
  Average Prompt Tokens: 14,709
  Average Completion Tokens: 3,499
  Average Total Tokens: 18,208
```

## Understanding Token Counts

### Prompt (Input) Tokens

Prompt tokens include:
- System prompt (counted for each API call)
- All previous messages in the conversation (context)

As conversations grow longer, prompt token counts increase significantly because:
- Each new message adds to the context
- Previous messages are sent with each API call
- This creates cumulative token usage

### Completion (Output) Tokens

Completion tokens are:
- The tokens in each generated response
- Directly controlled by the model's output length

### Total Tokens

Total tokens = Prompt tokens + Completion tokens

This is what determines the overall cost, with output tokens typically being 5x more expensive than input tokens for most models.

## Cost Optimization Tips

1. **Use cheaper models for experiments**: Haiku is 12x cheaper than Sonnet
2. **Limit conversation turns**: Token usage grows quadratically with conversation length
3. **Use concise system prompts**: They're repeated in every API call
4. **Monitor message length**: Longer messages increase both input and output costs
5. **Consider Gemini 2.0 Flash for testing**: Currently free

## Interpreting Results

### High Prompt/Completion Ratio

If prompt tokens are much higher than completion tokens (e.g., 4:1 ratio), this indicates:
- Long conversations with many turns
- Significant context accumulation
- Most cost is from re-sending previous messages

### High Completion Tokens

If completion tokens are high relative to prompt:
- Model is generating long responses
- Consider adjusting max_tokens parameter
- May indicate model is being verbose

### Message Length Variance

High variance in message length (max >> avg) suggests:
- Some conversations have unusually long messages
- May indicate edge cases or specific topics that trigger verbosity
- Review longest messages to understand patterns

## Integration with Existing Code

The token counting logic in these scripts matches the approach in `src/utils/model_interaction.py`, which:

1. Tracks actual token usage from API responses
2. Fetches actual costs from OpenRouter's `/generation` API
3. Provides real-time cost tracking during experiments

For production runs, the actual costs from OpenRouter will be more accurate than these estimates.

## CSV Data Format

The CSV export includes:

- `file`: Source JSONL filename
- `conversation_id`: Line number in file
- `model`: Model identifier
- `temperature`: Sampling temperature
- `num_turns`: Number of conversation turns
- `prompt_tokens`: Input tokens
- `completion_tokens`: Output tokens
- `total_tokens`: Total tokens
- `input_cost`: Cost of input tokens
- `output_cost`: Cost of output tokens
- `total_cost`: Total cost
- `avg_msg_length`: Average tokens per message
- `max_msg_length`: Longest message in tokens
- `min_msg_length`: Shortest message in tokens

## Future Enhancements

Potential improvements to these tools:

1. **Real-time monitoring**: Track costs during experiment execution
2. **Budget alerts**: Warn when approaching cost thresholds
3. **Model recommendations**: Suggest optimal model based on budget/quality tradeoffs
4. **Visualization**: Generate charts showing cost trends
5. **Batch analysis**: Process multiple experiment runs
6. **API integration**: Pull actual costs from OpenRouter API

## Notes

- Token counts are estimates based on `tiktoken` (cl100k_base encoding)
- Actual costs may vary due to model-specific tokenization
- OpenRouter may use different token counting than displayed here
- For precise costs, use the actual cost data from OpenRouter's generation API
- Costs are subject to change - check OpenRouter/Anthropic for current pricing

## Support

For issues or questions about cost analysis:

1. Check that input files are valid JSONL format
2. Ensure `tiktoken` is installed for accurate counting
3. Verify model names match those in `MODEL_PRICING` dictionary
4. Review the CSV export for per-conversation details
