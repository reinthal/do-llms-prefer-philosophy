# Cost Analysis Quick Reference Card

## Current Dataset Stats (Claude Haiku 4.5)

```
10 conversations × 9 turns = $0.080509
Cost per conversation: $0.008051
Average tokens per conversation: 18,208
```

## Quick Commands

```bash
# Instant summary
python3 quick_cost_summary.py

# Basic analysis
python3 calculate_token_costs.py

# Full analysis with CSV
python3 analyze_costs.py --output-csv costs.csv

# Compare models
python3 analyze_costs.py --compare-models
```

## Cost Projections (Claude Haiku 4.5)

| Scale | Cost |
|-------|------|
| 10 conversations | $0.08 |
| 100 conversations | $0.81 |
| 1,000 conversations | $8.05 |
| 10,000 conversations | $80.51 |

## Model Price Comparison (per conversation, 10 turns)

| Model | Cost | vs Haiku |
|-------|------|----------|
| Gemini 2.0 Flash | FREE | ∞x cheaper |
| **Haiku 4.5** | **$0.0059** | **baseline** |
| Llama 3.3 70B | $0.0062 | 1.05x |
| Sonnet 4 | $0.0707 | 12x more |
| GPT-4 Turbo | $0.2055 | 35x more |
| Opus 4 | $0.3533 | 60x more |
| GPT-4 | $0.5715 | 97x more |

## Budget Planning

### $10 Budget
- **11,800** Haiku conversations (9 turns)
- **1,240** Haiku conversations (15 turns, est.)
- **140** Sonnet conversations (9 turns)
- **50** GPT-4 Turbo conversations

### $100 Budget
- **12,400** Haiku conversations
- **1,415** Sonnet conversations
- **487** GPT-4 Turbo conversations
- **175** GPT-4 conversations

## Key Metrics

### Token Usage Pattern
```
Prompt:     14,709 tokens (81%)  →  Input cost: $0.037 (46%)
Completion:  3,499 tokens (19%)  →  Output cost: $0.044 (54%)
Total:      18,208 tokens        →  Total cost: $0.081
```

### Why Output Costs More
Output tokens are 5x more expensive ($1.25/M vs $0.25/M), so even though they're only 19% of tokens, they're 54% of cost.

## Optimization Tips

1. **Use Haiku for experiments** - 12x cheaper than Sonnet
2. **Limit conversation turns** - Token usage grows quadratically
3. **Shorten system prompts** - Repeated in every API call
4. **Monitor message length** - Some hit 776 tokens

## Files Generated

- `COST_SUMMARY.md` - Comprehensive analysis
- `COST_ANALYSIS_README.md` - Tool documentation
- `data/cost_analysis.csv` - Per-conversation data
- `calculate_token_costs.py` - Basic calculator
- `analyze_costs.py` - Advanced analyzer
- `quick_cost_summary.py` - Quick summary

## Understanding Token Growth

```
Turn 1: system + msg1                     ≈    30 tokens
Turn 2: system + msg1 + msg2              ≈   500 tokens
Turn 3: system + msg1 + msg2 + msg3       ≈ 1,200 tokens
...
Turn 9: system + msg1...msg9              ≈14,700 tokens
```

Each turn includes ALL previous messages as context!

## Production Integration

The actual code in `src/utils/model_interaction.py`:
- Fetches real costs from OpenRouter API
- Tracks actual token usage per request
- Displays cost summary after each run

These analysis tools provide estimates. For exact costs, check the production output.

---

**Quick Start**: Run `python3 quick_cost_summary.py` for instant overview!
