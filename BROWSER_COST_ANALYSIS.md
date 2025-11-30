# Browser Agent Token Cost Analysis

This document provides a detailed analysis of token usage and costs for the browser agent tasks.

## Summary

**Analysis Date:** 2025-11-27
**Data File:** `/tmp/browser-agent.jsonl`
**Total Sessions Analyzed:** 1

## Token Usage Breakdown

### Model: anthropic/claude-sonnet-4.5 (Claude Sonnet 4.5 - latest)

#### Session Statistics
- **Number of sessions:** 1
- **Total steps:** 19
- **Average steps per session:** 19.0

#### Token Counts
| Category | Count |
|----------|-------|
| Total Input Tokens | 2,024,271 |
| Total Output Tokens | 1,318 |
| **Total Tokens** | **2,025,589** |

#### Per-Session Averages
| Metric | Average |
|--------|---------|
| Input Tokens | 2,024,271 |
| Output Tokens | 1,318 |
| Total Tokens | 2,025,589 |

## Cost Analysis

### Pricing Information
- **Input:** $3.00 per 1M tokens
- **Output:** $15.00 per 1M tokens

### Actual Costs (1 session)
| Cost Type | Amount |
|-----------|--------|
| Input Cost | $6.07 |
| Output Cost | $0.02 |
| **Total Cost** | **$6.09** |

### Projected Costs
| Number of Sessions | Total Cost |
|-------------------|------------|
| 1 session | $6.09 |
| 10 sessions | $60.93 |
| 100 sessions | $609.26 |

## Key Insights

### 1. Token Distribution
- **Input tokens dominate:** 99.9% of total tokens are input tokens
- **Output is minimal:** Only 0.1% of tokens are for the final output
- This indicates the browser agent accumulates significant context through its chain of thought

### 2. Cost Drivers
- **Primary cost:** Input tokens ($6.07 per session)
- **Secondary cost:** Output tokens ($0.02 per session)
- The extensive browsing session (19 steps) creates substantial context that gets fed back as input

### 3. Cost Efficiency Considerations
- Each browsing step adds to the context window
- The 19-step session resulted in ~2M input tokens
- Using a cheaper model like Claude Haiku 4.5 could reduce costs significantly:
  - Haiku pricing: $0.80/M input, $4.00/M output
  - Estimated Haiku cost per session: ~$1.62 (vs $6.09 for Sonnet 4)
  - **Potential savings: 73% per session**

## Cost Calculator Tool

A Python script has been created to calculate costs for future browser sessions:

### Usage

```bash
# Basic analysis
uv run calculate_browser_costs.py

# Analyze specific file
uv run calculate_browser_costs.py --file /tmp/browser-agent.jsonl

# Verbose output with per-session details
uv run calculate_browser_costs.py --verbose

# List available models and pricing
uv run calculate_browser_costs.py --list-models

# Output as JSON
uv run calculate_browser_costs.py --json
```

### Features
- Estimates token counts using tiktoken (cl100k_base encoding)
- Calculates costs based on current OpenRouter pricing
- Supports multiple models
- Provides detailed breakdowns and projections
- Can analyze individual sessions or aggregate data

## Model Comparison

| Model | Input Price | Output Price | Est. Cost/Session | vs Sonnet 4 |
|-------|-------------|--------------|-------------------|-------------|
| Claude Sonnet 4 | $3.00/M | $15.00/M | $6.09 | Baseline |
| Claude Haiku 4.5 | $0.80/M | $4.00/M | $1.62 | -73% |
| Claude Opus 4 | $15.00/M | $75.00/M | $30.46 | +400% |
| Claude 3.5 Sonnet | $3.00/M | $15.00/M | $6.09 | Same |

## Recommendations

### For Cost Optimization
1. **Use Claude Haiku 4.5** for routine browsing tasks (73% cheaper)
2. **Limit browsing steps** when possible to reduce context accumulation
3. **Monitor token usage** regularly using the provided calculator
4. **Consider batch processing** to amortize fixed costs

### For Quality
1. **Use Claude Sonnet 4** for complex research tasks requiring nuanced understanding
2. **Use Claude Opus 4** only for critical tasks requiring maximum capability
3. **Test with Haiku first** to see if it meets quality requirements

### For Budgeting
Based on current analysis, for a research project planning multiple iterations:
- **Small dataset (10 sessions):** Budget $60-70 (Sonnet 4) or $15-20 (Haiku 4.5)
- **Medium dataset (50 sessions):** Budget $300-350 (Sonnet 4) or $80-100 (Haiku 4.5)
- **Large dataset (100 sessions):** Budget $600-650 (Sonnet 4) or $160-180 (Haiku 4.5)

## Important Notes

1. **Token counts are estimates** using tiktoken with cl100k_base encoding
2. **Actual API token counts may differ** by ±5-10% due to model-specific tokenization
3. **Prices are current as of November 2025** - check OpenRouter for latest pricing
4. **Input token count includes** the full chain of thought context from all browsing steps
5. **For exact usage**, check the OpenRouter dashboard or API response headers
6. **Update pricing** in `calculate_browser_costs.py` if rates change

## Files Created

1. **`calculate_browser_costs.py`** - Main cost calculator script
2. **`BROWSER_COST_ANALYSIS.md`** - This analysis document (can be updated after new runs)

## Data Location

- **Current session data:** `/tmp/browser-agent.jsonl`
- **Permanent storage:** Consider moving to `./data/browser-agent-sessions/` for version control
- **Log files:** `/tmp/browser-agent.log` (contains detailed execution logs)

## Next Steps

1. Run multiple sessions with different models for comparison
2. Test with Claude Haiku 4.5 to validate cost savings
3. Collect more data to establish average costs per browsing task type
4. Consider implementing token usage tracking in the CrewAI code for real-time monitoring
