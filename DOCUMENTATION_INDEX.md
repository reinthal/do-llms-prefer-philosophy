# Documentation Index

Complete guide to running tasks with the unified wrapper script.

## Quick Navigation

- **New User?** Start with → [`QUICKSTART.md`](QUICKSTART.md)
- **Need Examples?** See → [`EXAMPLES.md`](EXAMPLES.md)
- **Want Details?** Read → [`USAGE_GUIDE.md`](USAGE_GUIDE.md)
- **Implementation Details?** Check → [`WRAPPER_SUMMARY.md`](WRAPPER_SUMMARY.md)

## Documentation Files

### 1. QUICKSTART.md
**Best for:** First-time users who want to run tasks immediately

**Contents:**
- Prerequisites and setup
- Your first task (with examples)
- Testing before full runs
- Understanding output
- Cost estimates
- Recommended workflow

**Start here if:** You want to get running in under 5 minutes

---

### 2. EXAMPLES.md
**Best for:** Finding ready-to-use commands

**Contents:**
- Commands for all 9 supported models
- Self-conversation examples
- Browser task examples
- Batch execution scripts
- Custom configurations
- Parallel execution

**Use this when:** You need a specific command to copy and paste

---

### 3. USAGE_GUIDE.md
**Best for:** Understanding all features and options

**Contents:**
- Comprehensive task descriptions
- All parameters explained
- Troubleshooting guide
- Output file formats
- Cost planning
- Advanced usage tips

**Use this when:** You want to understand all available options

---

### 4. WRAPPER_SUMMARY.md
**Best for:** Understanding the implementation

**Contents:**
- Overview of changes made
- Architecture decisions
- Supported models list
- File locations
- Testing information
- Next steps

**Use this when:** You want to understand how it works under the hood

---

### 5. README.md
**Best for:** Project overview and model information

**Contents:**
- Project introduction
- Setup instructions
- Wrapper script documentation
- Direct script access (alternative methods)
- Model comparison tables (Anthropic & OpenAI)
- Nix/Devenv instructions

**Use this when:** You need project context or model information

---

## Scripts

### run_tasks.py (Main Wrapper)
**Purpose:** Unified CLI for running both task types

**Usage:**
```bash
# Self-conversation
python run_tasks.py self-conversation --model MODEL --iterations N

# Browser
python run_tasks.py browser --model MODEL --iterations N
```

**Features:**
- Supports 9 models (3 Anthropic + 6 OpenAI)
- Parameter validation
- Clear error messages
- Comprehensive help text

---

### run_all.sh (Batch Execution)
**Purpose:** Run all models for both task types

**Usage:**
```bash
./run_all.sh
```

**What it does:**
- Runs all 9 models sequentially
- Both task types (self-conversation + browser)
- 10 iterations each
- Logs everything to timestamped file
- Total: 180 task executions

---

## Supported Models

### Anthropic (3 models)
1. `anthropic/claude-sonnet-4.5` - Latest flagship
2. `anthropic/claude-3.7-sonnet` - Incremental update
3. `anthropic/claude-haiku-4.5` - Fast & cost-effective

### OpenAI (6 models)
4. `openai/gpt-5-mini` - Efficient variant
5. `openai/gpt-5.1` - Enhanced version
6. `openai/gpt-4.1` - 1M context
7. `openai/gpt-4o` - Multimodal flagship
8. `openai/gpt-5-chat` - Conversational
9. `openai/o3` - Advanced reasoning

---

## Task Types

### Self-Conversation
Models talk to themselves to explore preferences.

**Command:**
```bash
python run_tasks.py self-conversation --model MODEL --iterations 10
```

**Output:** JSONL file with conversation data + cost summary

---

### Browser
Models browse Wikipedia using AI agents.

**Command:**
```bash
python run_tasks.py browser --model MODEL --iterations 10
```

**Output:** JSONL session logs + browser agent log

---

## Quick Reference

### Common Commands

```bash
# Help
python run_tasks.py --help
python run_tasks.py self-conversation --help
python run_tasks.py browser --help

# Test runs (fast)
python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 1 --turns 5 --show-convo
python run_tasks.py browser --model anthropic/claude-haiku-4.5 --iterations 1 --pages 3

# Production runs (10 iterations)
python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 10
python run_tasks.py browser --model openai/gpt-4o --iterations 10

# Batch run (all models)
./run_all.sh
```

### File Outputs

```
# Self-conversation
do-llms-prefer-philosophy-{model}-{timestamp}-{turns}.jsonl

# Browser
browsing-sessions-{model}-{timestamp}.jsonl
/tmp/browser-agent.log
```

### Prerequisites

```bash
# Install dependencies
uv sync

# Configure API key
echo "OPENROUTER_API_KEY=your_key" > secrets.env
```

---

## Learning Path

### Beginner
1. Read [`QUICKSTART.md`](QUICKSTART.md)
2. Run test commands
3. Check output files
4. Run full dataset for one model

### Intermediate
1. Browse [`EXAMPLES.md`](EXAMPLES.md) for specific models
2. Customize parameters (turns, pages, iterations)
3. Run multiple models manually
4. Review [`USAGE_GUIDE.md`](USAGE_GUIDE.md) for advanced options

### Advanced
1. Use [`run_all.sh`](run_all.sh) for batch execution
2. Create custom batch scripts
3. Analyze output with `evaluate_trajectories.py`
4. Review [`WRAPPER_SUMMARY.md`](WRAPPER_SUMMARY.md) for architecture

---

## Troubleshooting

### Issue: API Key Error
**Solution:** Configure `secrets.env` with `OPENROUTER_API_KEY=your_key`

### Issue: Model Not Found
**Solution:** Check model ID format (e.g., `anthropic/claude-haiku-4.5`)

### Issue: Task Interrupted
**Solution:** Press Ctrl+C to stop. Sessions are logged incrementally.

### More Help
See the Troubleshooting section in [`USAGE_GUIDE.md`](USAGE_GUIDE.md)

---

## Additional Resources

- **Project PDF:** `do-llms-prefer-philosophy.pdf` (project overview)
- **Direct Scripts:** `src/main.py` (self-conversation), `src/crew/main.py` (browser)
- **Evaluation:** `evaluate_trajectories.py` (analyze results)

---

## Getting Started Now

**Fastest path to running tasks:**

1. Install & configure:
   ```bash
   uv sync
   echo "OPENROUTER_API_KEY=your_key" > secrets.env
   ```

2. Test run:
   ```bash
   python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 1 --turns 5 --show-convo
   ```

3. Full run:
   ```bash
   python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 10
   python run_tasks.py browser --model anthropic/claude-haiku-4.5 --iterations 10
   ```

4. All models:
   ```bash
   ./run_all.sh
   ```

**Total time from zero to running: < 5 minutes**

---

## Questions?

- Check help: `python run_tasks.py --help`
- Read guides: Start with [`QUICKSTART.md`](QUICKSTART.md)
- Review examples: See [`EXAMPLES.md`](EXAMPLES.md)
