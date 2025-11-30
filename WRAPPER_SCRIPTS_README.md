# Wrapper Scripts for Running Experiments

This document provides a complete overview of the wrapper scripts created for running browser and conversation tasks across multiple models.

## Created Files

### Python Scripts

1. **`run_experiments.py`** - Main wrapper for running multiple iterations of tasks
   - Run 10 (or custom number) iterations for a single model
   - Supports both browser and conversation tasks
   - Handles output organization and error tracking
   - Generates summary JSON files

2. **`run_all_models.py`** - Batch runner for multiple models
   - Run experiments across model groups (Anthropic, OpenAI, or all)
   - Run specific custom model lists
   - Parallel execution across different models
   - Comprehensive batch reporting

### Shell Scripts

3. **`run_browser_experiments.sh`** - Simple shell wrapper for browser tasks
   - Easy-to-use bash interface
   - Sensible defaults
   - Environment validation

4. **`run_conversation_experiments.sh`** - Simple shell wrapper for conversation tasks
   - Easy-to-use bash interface
   - Sensible defaults
   - Environment validation

### Documentation

5. **`EXPERIMENTS_GUIDE.md`** - Comprehensive guide
   - Detailed usage instructions
   - All options explained
   - Output structure
   - Troubleshooting

6. **`QUICK_START.md`** - Quick reference
   - Common commands at a glance
   - Fast testing commands
   - Essential examples

## Quick Reference

### Python Script Usage

```bash
# Single model, 10 iterations (browser)
python run_experiments.py browser anthropic/claude-sonnet-4.5

# Single model, 10 iterations (conversation)
python run_experiments.py conversation openai/gpt-5

# All Anthropic models (browser)
python run_all_models.py browser --group anthropic

# All OpenAI models (conversation)
python run_all_models.py conversation --group openai

# All models (both browser and conversation) - comprehensive
python run_all_models.py browser --group all
python run_all_models.py conversation --group all
```

### Shell Script Usage

```bash
# Browser experiments (simple)
./run_browser_experiments.sh anthropic/claude-sonnet-4.5

# With custom iterations and pages
./run_browser_experiments.sh openai/gpt-5 20 10

# Conversation experiments (simple)
./run_conversation_experiments.sh anthropic/claude-haiku-4.5

# With custom iterations and turns
./run_conversation_experiments.sh openai/o3 15 20
```

## Supported Models

The scripts support all these models out of the box:

### Anthropic
- `anthropic/claude-sonnet-4.5`
- `anthropic/claude-3.7-sonnet`
- `anthropic/claude-haiku-4.5`

### OpenAI
- `openai/gpt-5-mini`
- `openai/gpt-5.1`
- `openai/gpt-4.1`
- `openai/gpt-4o`
- `openai/gpt-5-chat`
- `openai/o3`

## Key Features

### 1. Automated Iteration Management
- Run 10+ iterations without manual intervention
- Automatic file naming and organization
- Progress tracking and logging

### 2. Error Handling
- Graceful error handling for failed tasks
- Timeout protection (30 minutes per task)
- Continue-on-error mode for batch runs
- Detailed error logging in summary files

### 3. Output Organization
- All outputs go to `./data/` directory
- Timestamped filenames
- Iteration numbers in filenames
- Summary JSON files with complete statistics

### 4. Flexible Configuration
- Custom number of iterations
- Custom pages per browser session
- Custom turns per conversation
- Verbose mode for debugging
- Custom output directories

### 5. Cost Awareness
- Built-in timeout protection
- Ability to test with cheap models first
- Batch processing with error recovery

## Output Structure

```
./data/
├── browsing-sessions-anthropic-claude-sonnet-4.5-1732734567_iter1.jsonl
├── browsing-sessions-anthropic-claude-sonnet-4.5-1732734567_iter2.jsonl
├── ...
├── do-llms-prefer-philosophy-openai-gpt-5-1732734890_iter1.jsonl
├── do-llms-prefer-philosophy-openai-gpt-5-1732734890_iter2.jsonl
├── ...
├── experiment_summary_browser_anthropic-claude-sonnet-4.5_20251127_143000.json
└── experiment_summary_conversation_openai-gpt-5_20251127_150000.json
```

### Summary File Contents

Each summary JSON contains:
- Configuration used (model, task type, iterations, etc.)
- Results for each iteration (success/failure, errors, output files)
- Statistics (total runs, successful, failed)
- Timestamps for all operations

## Common Workflows

### 1. Quick Test
```bash
# Test with cheapest/fastest model
python run_experiments.py browser anthropic/claude-haiku-4.5 -n 1 --pages 3 -v
```

### 2. Single Model Data Collection
```bash
# Standard 10 iterations
python run_experiments.py browser anthropic/claude-sonnet-4.5
```

### 3. Compare Model Groups
```bash
# Anthropic vs OpenAI
python run_all_models.py browser --group anthropic -n 10
python run_all_models.py browser --group openai -n 10
```

### 4. Comprehensive Data Collection
```bash
# All models, both task types
python run_all_models.py browser --group all -n 50
python run_all_models.py conversation --group all -n 50
```

### 5. Custom Model Comparison
```bash
# Specific models only
python run_all_models.py browser \
  -m anthropic/claude-sonnet-4.5 openai/gpt-5 openai/o3 \
  -n 20
```

## Environment Requirements

### Required
- `uv` package manager installed
- `OPENROUTER_API_KEY` environment variable set
- Python dependencies installed via `uv sync`

### For Browser Tasks
- Node.js and npm installed
- Playwright MCP server: `npx -y @playwright/mcp@latest`

### Verification
```bash
# Check uv
uv --version

# Check API key
echo $OPENROUTER_API_KEY

# Check Python scripts
python run_experiments.py --help
python run_all_models.py --help
```

## Command-Line Options

### run_experiments.py

```
usage: run_experiments.py [-h] [-n N] [--output DIR] [--pages N] [--turns N] [-v]
                          {browser,conversation} model

positional arguments:
  {browser,conversation}  Type of task
  model                   Model name (e.g., anthropic/claude-sonnet-4.5)

options:
  -n, --iterations N      Number of iterations (default: 10)
  --output DIR            Output directory (default: ./data)
  --pages N               Pages per browser session (default: 5)
  --turns N               Turns per conversation (default: 15)
  -v, --verbose           Show detailed output
```

### run_all_models.py

```
usage: run_all_models.py [-h] (--group {anthropic,openai,all} | -m MODEL [MODEL ...])
                         [-n N] [--output DIR] [--pages N] [--turns N] [-v]
                         [--continue-on-error]
                         {browser,conversation}

positional arguments:
  {browser,conversation}  Type of task

options:
  --group GROUP           Model group (anthropic/openai/all)
  -m, --models MODEL ...  Specific models (space-separated)
  -n, --iterations N      Iterations per model (default: 10)
  --output DIR            Output directory (default: ./data)
  --pages N               Pages per browser session (default: 5)
  --turns N               Turns per conversation (default: 15)
  -v, --verbose           Show detailed output
  --continue-on-error     Don't stop on model failure
```

## Error Handling

### Common Issues

1. **"OPENROUTER_API_KEY not set"**
   ```bash
   export OPENROUTER_API_KEY=your_key_here
   ```

2. **"'uv' command not found"**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Timeout errors**
   - Reduce `--pages` or `--turns`
   - Check internet connection
   - Verify API key is valid

4. **Browser task failures**
   - Install Playwright: `npx -y @playwright/mcp@latest`
   - Check `/tmp/browser-agent.log` for details

### Recovery Strategies

1. **Use continue-on-error mode**
   ```bash
   python run_all_models.py browser --group all --continue-on-error
   ```

2. **Run models individually**
   ```bash
   # If batch fails, run one at a time
   python run_experiments.py browser anthropic/claude-sonnet-4.5 -n 10
   python run_experiments.py browser openai/gpt-5 -n 10
   ```

3. **Check summary files**
   - Look at experiment_summary_*.json for error details
   - Retry failed iterations manually

## Performance Tips

1. **Start small**: Test with `-n 1` or `-n 2` first
2. **Use Haiku for testing**: Faster and cheaper
3. **Monitor costs**: Check OpenRouter dashboard
4. **Use timeouts**: Built-in 30-minute timeout per task
5. **Batch wisely**: Use `--continue-on-error` for large batches

## Integration with Existing Code

The wrapper scripts integrate seamlessly with:

- **`src/main.py`** - For conversation tasks
- **`src/crew/main.py`** - For browser tasks
- **`evaluate_trajectories.py`** - For analyzing results

They preserve all existing functionality while adding:
- Iteration management
- Error handling
- Output organization
- Batch processing
- Comprehensive logging

## Next Steps

1. **Test the scripts**
   ```bash
   python run_experiments.py browser anthropic/claude-haiku-4.5 -n 1 -v
   ```

2. **Run a small batch**
   ```bash
   python run_all_models.py browser --group anthropic -n 2
   ```

3. **Review outputs**
   ```bash
   ls -lh ./data/
   cat ./data/experiment_summary_*.json | jq
   ```

4. **Scale up**
   ```bash
   python run_all_models.py browser --group all -n 10
   ```

## Documentation Files

For more detailed information, see:

- **`EXPERIMENTS_GUIDE.md`** - Complete reference guide
- **`QUICK_START.md`** - Quick start commands
- **`README.md`** - Project overview and setup

## Support and Troubleshooting

- Check logs in `/tmp/browser-agent.log` (browser tasks)
- Review summary JSON files for error details
- Use `-v` flag for verbose output
- Start with small test runs before scaling up
- Monitor OpenRouter dashboard for costs and rate limits

## Cost Estimates

Approximate costs (varies by model and task complexity):

- **Haiku**: $0.05-0.15 per browser task, $0.02-0.05 per conversation
- **Sonnet**: $0.20-0.50 per browser task, $0.10-0.20 per conversation
- **GPT models**: $0.30-0.80 per browser task, $0.15-0.40 per conversation

**10 iterations across all 9 models**: Approximately $50-150

Always monitor actual costs on OpenRouter!
