# Token Cost Analysis Summary

## Executive Summary

Based on analysis of the current dataset with **Claude Haiku 4.5**:

- **10 conversations** (9 turns each)
- **Total cost**: $0.080509
- **Average cost per conversation**: $0.008051
- **Total tokens**: 182,077 (14,709 prompt + 3,499 completion per conversation)

## Quick Reference

| Scale | Cost |
|-------|------|
| 1 conversation | $0.008051 |
| 10 conversations | $0.0805 |
| 100 conversations | $0.81 |
| 1,000 conversations | $8.05 |
| 10,000 conversations | $80.51 |

## Current Dataset Statistics

### Token Usage (per conversation average)

- **Prompt Tokens**: 14,709 (80.8%)
- **Completion Tokens**: 3,499 (19.2%)
- **Total Tokens**: 18,208

### Message Statistics

- **Average message length**: 389 tokens
- **Max message length**: 776 tokens
- **Min message length**: 7 tokens
- **Average turns**: 9

### Cost Breakdown

- **Input cost**: $0.036772 (45.7% of total)
- **Output cost**: $0.043737 (54.3% of total)
- **Total cost**: $0.080509

## Model Comparison (10 turns per conversation)

Estimated costs for 10-turn conversations across different models:

| Model | 1 Conv | 10 Conv | 100 Conv | 1K Conv |
|-------|--------|---------|----------|---------|
| **Gemini 2.0 Flash** | $0.000 | $0.00 | $0.00 | $0.00 |
| **Claude Haiku 4/4.5** | $0.0059 | $0.06 | $0.59 | $5.89 |
| **Llama 3.3 70B** | $0.0062 | $0.06 | $0.62 | $6.22 |
| **Claude Sonnet 4** | $0.0707 | $0.71 | $7.07 | $70.65 |
| **Claude 3.5 Sonnet** | $0.0707 | $0.71 | $7.07 | $70.65 |
| **GPT-4 Turbo** | $0.2055 | $2.06 | $20.55 | $205.50 |
| **Claude Opus 4** | $0.3533 | $3.53 | $35.33 | $353.25 |
| **GPT-4** | $0.5715 | $5.72 | $57.15 | $571.50 |

### Key Insights

1. **Haiku is 12x cheaper than Sonnet** - Ideal for experiments and testing
2. **Gemini 2.0 Flash is free** - Great for prototyping (quality tradeoffs apply)
3. **Token usage grows quadratically** - Longer conversations have exponential cost growth
4. **Output tokens cost 5x input** - For Claude models (more for others)

## Detailed Conversation Breakdown

From CSV export (`data/cost_analysis.csv`):

| Conv # | Turns | Total Tokens | Total Cost | Avg Msg Length | Max Msg |
|--------|-------|--------------|------------|----------------|---------|
| 1 | 9 | 17,915 | $0.007811 | 370 | 526 |
| 2 | 9 | 15,490 | $0.006848 | 331 | 457 |
| 3 | 9 | 17,104 | $0.007148 | 319 | 583 |
| 4 | 9 | 22,142 | $0.009813 | 475 | 776 |
| 5 | 9 | 13,983 | $0.006148 | 295 | 524 |
| 6 | 9 | 23,055 | $0.010865 | 567 | 707 |
| 7 | 9 | 18,953 | $0.008739 | 445 | 622 |
| 8 | 9 | 20,493 | $0.009217 | 455 | 665 |
| 9 | 9 | 16,558 | $0.007013 | 319 | 529 |
| 10 | 9 | 16,384 | $0.006909 | 313 | 543 |

**Variance**: Conversation #6 cost 77% more than conversation #5 due to longer messages.

## Cost Optimization Recommendations

### For Development/Testing

1. **Use Claude Haiku 4.5** for initial experiments
   - 12x cheaper than Sonnet
   - Still high quality for most tasks
   - ~$0.008 per 9-turn conversation

2. **Use Gemini 2.0 Flash** for rapid prototyping
   - Free tier available
   - Test conversation logic without cost
   - Migrate to Claude/GPT for production

### For Production

1. **Limit conversation turns**
   - 9 turns: ~18K tokens
   - 15 turns: ~30-35K tokens (est.)
   - Each additional turn adds cumulative context

2. **Optimize system prompts**
   - Current system prompt: ~30 tokens
   - Repeated in every API call
   - 9 turns = 270 tokens just from system prompt

3. **Monitor message length**
   - Average: 389 tokens per message
   - Some messages up to 776 tokens
   - Consider max_tokens limit if verbosity is an issue

### Budget Planning

For a research dataset with **1,000 conversations**:

| Configuration | Model | Est. Cost |
|--------------|-------|-----------|
| **Budget** | Haiku 4.5 (9 turns) | $8.05 |
| **Standard** | Haiku 4.5 (15 turns) | ~$15-20 |
| **Premium** | Sonnet 4 (9 turns) | $70.65 |
| **Premium** | Sonnet 4 (15 turns) | ~$120-150 |

## Tools Available

### 1. Quick Cost Summary
```bash
python3 quick_cost_summary.py
```
- Instant overview
- Per-model breakdown
- Scaling projections

### 2. Basic Cost Calculator
```bash
python3 calculate_token_costs.py
```
- Detailed token counts
- Per-file analysis
- Summary across files

### 3. Advanced Cost Analyzer
```bash
python3 analyze_costs.py --compare-models --output-csv results.csv
```
- Model comparison
- CSV export
- Message statistics

## Understanding Token Growth

Token usage in self-conversations grows based on:

```
Turn 1: system_prompt + message_1
Turn 2: system_prompt + message_1 + message_2
Turn 3: system_prompt + message_1 + message_2 + message_3
...
```

This creates **quadratic growth** in prompt tokens:
- Turn 1: ~30 tokens (just system)
- Turn 5: ~2,000 tokens (system + 4 previous messages)
- Turn 9: ~14,700 tokens (system + 8 previous messages)

## Real-World Comparison

Based on actual data from `model_interaction.py`:

The production code fetches actual costs from OpenRouter's `/generation` API, which may differ slightly from these estimates due to:

1. **Model-specific tokenization** - Claude uses a different tokenizer than GPT-4
2. **Actual vs estimated tokens** - API returns exact counts
3. **Native token counts** - OpenRouter provides `native_tokens_*` fields

For production runs, refer to the cost summary printed at the end of `main.py` execution.

## Pricing Sources

- **Claude models**: https://www.anthropic.com/pricing
- **OpenRouter**: https://openrouter.ai/models
- **OpenAI**: https://openai.com/pricing

*Pricing as of January 2025. Verify current rates before large-scale runs.*

## Next Steps

1. **For immediate cost analysis**: Run `python3 quick_cost_summary.py`
2. **For detailed breakdown**: Run `python3 analyze_costs.py --output-csv costs.csv`
3. **For model comparison**: Run `python3 analyze_costs.py --compare-models --turns 15`
4. **For production runs**: Check actual costs in console output from `main.py`

## Files Generated

- `/data/cost_analysis.csv` - Per-conversation detailed breakdown
- `COST_ANALYSIS_README.md` - Comprehensive tool documentation
- `calculate_token_costs.py` - Basic cost calculator
- `analyze_costs.py` - Advanced cost analyzer
- `quick_cost_summary.py` - Quick summary tool

---

**Last Updated**: 2025-11-27
**Dataset**: 10 conversations, Claude Haiku 4.5, 9 turns each
