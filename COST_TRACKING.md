# Browser Cost Tracking

The `simple_wikipedia_browser.py` script now includes automatic cost tracking for every LLM API call.

## How It Works

The script uses LiteLLM's `success_callback` mechanism to intercept every API call and log:
- Token usage (prompt, completion, total)
- Cost breakdown (input, output, total)
- Latency
- Model name
- Session ID
- Timestamp

## Cost Log Location

All cost data is logged to: **`/tmp/browser-cost.log`**

Each line is a JSON object representing one API call.

## Example Log Entry

```json
{
  "timestamp": "2025-11-27T14:30:45.123456",
  "session_id": "2025-11-27T14:28:12.654321",
  "model": "anthropic/claude-haiku-4.5",
  "usage": {
    "prompt_tokens": 1234,
    "completion_tokens": 567,
    "total_tokens": 1801
  },
  "cost": {
    "input_cost_usd": 0.000309,
    "output_cost_usd": 0.000709,
    "total_cost_usd": 0.001018
  },
  "latency_seconds": 2.456
}
```

## Viewing Costs

Use the `view_browser_costs.py` utility to analyze costs:

### View All Sessions

```bash
python view_browser_costs.py
```

Output:
```
📊 Browser Cost Analysis
================================================================================

Session: 2025-11-27T14:28:12.654321
  Time: 2025-11-27 14:28:12
  Model: anthropic/claude-haiku-4.5
  API Calls: 15
  Total Tokens: 245,678
  Total Cost: $0.123456
  Avg Cost/Call: $0.008230

================================================================================
📈 Grand Total
  Sessions: 1
  Total API Calls: 15
  Total Tokens: 245,678
  Total Cost: $0.123456
  Avg Cost/Session: $0.123456
  Avg Cost/Call: $0.008230
```

### View Specific Session

```bash
python view_browser_costs.py --session "2025-11-27T14:28:12.654321"
```

### Verbose Mode (Per-Call Breakdown)

```bash
python view_browser_costs.py --verbose
```

### List All Sessions

```bash
python view_browser_costs.py --list
```

### Clear Cost Log

```bash
python view_browser_costs.py --clear
```

## Real-Time Cost Display

During browser task execution, costs are printed after each API call:

```
💰 Cost: $0.001234 | Tokens: 1,801 | Latency: 2.46s
```

At the end of the session:

```
💰 Session Cost Summary:
   Total API Calls: 15
   Total Tokens: 245,678
   Total Cost: $0.123456
   Cost per Step: $0.008230
```

## Model Pricing

Pricing is based on OpenRouter rates (per million tokens):

| Model | Input | Output |
|-------|-------|--------|
| claude-haiku-4.5 | $0.25 | $1.25 |
| claude-sonnet-4.5 | $3.00 | $15.00 |
| claude-3.7-sonnet | $3.00 | $15.00 |
| claude-opus-4 | $15.00 | $75.00 |
| gpt-4o | $2.50 | $10.00 |
| gpt-5-mini | $0.15 | $0.60 |
| o3 | $10.00 | $40.00 |

## Integration with Session Logs

Cost data is also included in the main session log at `./data/browser-agent.jsonl`:

```json
{
  "session_id": "2025-11-27T14:28:12.654321",
  "model_name": "anthropic/claude-haiku-4.5",
  "status": "completed",
  "num_steps": 5,
  "session_cost": {
    "total_api_calls": 15,
    "total_tokens": 245678,
    "total_cost_usd": 0.123456
  }
}
```

## Programmatic Access

You can parse the cost log in your own scripts:

```python
import json

with open("/tmp/browser-cost.log", "r") as f:
    for line in f:
        entry = json.loads(line)
        session_id = entry["session_id"]
        cost = entry["cost"]["total_cost_usd"]
        tokens = entry["usage"]["total_tokens"]
        print(f"Session {session_id}: ${cost:.6f} ({tokens:,} tokens)")
```

## Tips

1. **Monitor costs in real-time** - The cost display updates after each API call
2. **Compare models** - Use the cost log to compare costs between different models
3. **Budget tracking** - Set up alerts when costs exceed thresholds
4. **Optimize prompts** - Analyze token usage patterns to reduce costs

## Troubleshooting

**Q: Cost log is empty**
- Make sure you've run at least one browser task
- Check that `/tmp/browser-cost.log` has write permissions

**Q: Costs seem wrong**
- Verify model pricing in `MODEL_PRICING` dict in `simple_wikipedia_browser.py`
- Check OpenRouter pricing page for latest rates
- Some models may have different pricing tiers

**Q: Missing cost data for some calls**
- The callback only tracks successful API calls
- Failed calls are not logged to the cost file
- Check the main session log for errors
