# Browser Agent Costs - Quick Reference

## Current Session Analysis (1 session, 19 steps)

### Token Usage
- **Input:** 2,024,271 tokens
- **Output:** 1,318 tokens
- **Total:** 2,025,589 tokens

### Costs by Model

| Model | Cost/Session | 10 Sessions | 100 Sessions |
|-------|--------------|-------------|--------------|
| **Claude Haiku 4.5** 💰 | $1.62 | $16.25 | $162.47 |
| **Claude Sonnet 4** | $6.09 | $60.93 | $609.26 |
| **Claude 3.5 Sonnet** | $6.09 | $60.93 | $609.26 |
| **Claude Opus 4** 💎 | $30.46 | $304.63 | $3,046.29 |

### Model Pricing (per 1M tokens)

| Model | Input | Output | Best For |
|-------|-------|--------|----------|
| Claude Haiku 4.5 | $0.80 | $4.00 | Cost-effective browsing |
| Claude Sonnet 4 | $3.00 | $15.00 | Balanced quality/cost |
| Claude 3.5 Sonnet | $3.00 | $15.00 | Alternative to Sonnet 4 |
| Claude Opus 4 | $15.00 | $75.00 | Maximum capability |

## Quick Calculator

```bash
# Default analysis
uv run calculate_browser_costs.py

# Verbose (per-session details)
uv run calculate_browser_costs.py --verbose

# List models and pricing
uv run calculate_browser_costs.py --list-models

# Custom file
uv run calculate_browser_costs.py --file /path/to/sessions.jsonl
```

## Key Insights

1. **Input tokens dominate** (99.9% of total)
2. **Each step adds context** (19 steps → 2M tokens)
3. **Haiku saves 73%** vs Sonnet 4
4. **Opus costs 5x more** than Sonnet 4

## Recommendation

- **Start with Haiku 4.5** for cost efficiency
- **Use Sonnet 4** if Haiku quality is insufficient
- **Reserve Opus 4** for critical research tasks only

## Data Files

- Session data: `/tmp/browser-agent.jsonl`
- Log file: `/tmp/browser-agent.log`
- Cost calculator: `calculate_browser_costs.py`
- Full analysis: `BROWSER_COST_ANALYSIS.md`
