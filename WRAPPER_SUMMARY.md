# Wrapper Script Implementation Summary

## Overview

Created a unified wrapper script (`run_tasks.py`) that supports both self-conversation and browser tasks for multiple AI models through the OpenRouter API.

## Changes Made

### 1. New Files Created

#### `/home/kog/repos/reinthal/do-llms-prefer-philosophy/run_tasks.py` (Main Wrapper)
- Unified CLI interface for both task types
- Supports 9 different models from Anthropic and OpenAI
- Parameter validation and error handling
- Clear progress indicators and status messages
- Executable Python script with comprehensive help text

**Key Features:**
- Subcommands for `self-conversation` and `browser` tasks
- Model validation with warnings for non-standard models
- Consistent interface across both task types
- Proper exit codes and error handling
- Integration with existing `src/main.py` and `src/crew/main.py`

#### `/home/kog/repos/reinthal/do-llms-prefer-philosophy/USAGE_GUIDE.md`
- Comprehensive usage documentation
- Detailed parameter descriptions
- Troubleshooting section
- Cost estimation guidance
- Output file format documentation

#### `/home/kog/repos/reinthal/do-llms-prefer-philosophy/EXAMPLES.md`
- Ready-to-use commands for all 9 models
- Both task types (self-conversation and browser)
- Batch script template
- Custom configuration examples
- Quick testing commands

#### `/home/kog/repos/reinthal/do-llms-prefer-philosophy/run_all.sh`
- Bash script for running all models sequentially
- Logs all output to timestamped file
- Error handling with `set -e`
- Progress indicators
- Executable permissions set

### 2. Updated Files

#### `/home/kog/repos/reinthal/do-llms-prefer-philosophy/README.md`
- Added "Unified Wrapper Script (Recommended)" section
- Moved original documentation to "Direct Script Access (Alternative)"
- Listed all 9 supported models
- Added example commands for both task types
- Maintained existing model comparison tables

## Supported Models

The wrapper script supports running tasks with any of these models:

### Anthropic Models
1. `anthropic/claude-sonnet-4.5` - Latest flagship, best coding performance
2. `anthropic/claude-3.7-sonnet` - Incremental update
3. `anthropic/claude-haiku-4.5` - Fast and cost-effective

### OpenAI Models
4. `openai/gpt-5-mini` - Efficient variant
5. `openai/gpt-5.1` - Enhanced version
6. `openai/gpt-4.1` - 1M context, coding focus
7. `openai/gpt-4o` - Multimodal flagship
8. `openai/gpt-5-chat` - Conversational improvements
9. `openai/o3` - Advanced reasoning

## Task Types

### 1. Self-Conversation Tasks

**Purpose:** Models engage in conversations with themselves to explore preferences and thought patterns.

**Command:**
```bash
python run_tasks.py self-conversation --model MODEL --iterations N [OPTIONS]
```

**Parameters:**
- `--model` (required): OpenRouter model identifier
- `--iterations`: Number of conversation samples (default: 10)
- `--turns`: Conversation turns per sample (default: 15)
- `--show-convo`: Display conversations in real-time (optional flag)

**Output:**
- JSONL file: `do-llms-prefer-philosophy-{model}-{timestamp}-{turns}.jsonl`
- Cost summary with actual OpenRouter API costs
- Token usage statistics (native counts)

**Example:**
```bash
python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 10
```

### 2. Browser Tasks

**Purpose:** Models browse Wikipedia using AI agents through interactive sessions.

**Command:**
```bash
python run_tasks.py browser --model MODEL --iterations N [OPTIONS]
```

**Parameters:**
- `--model` (required): OpenRouter model identifier
- `--iterations`: Number of browsing sessions (default: 10)
- `--pages`: Minimum pages to browse per session (default: 5)

**Output:**
- Session logs: `browsing-sessions-{model}-{timestamp}.jsonl`
- Browser agent log: `/tmp/browser-agent.log`
- Interactive terminal output

**Example:**
```bash
python run_tasks.py browser --model openai/gpt-4o --iterations 10
```

## Usage Instructions

### Quick Start

1. **Setup Environment:**
   ```bash
   # Install dependencies
   uv sync

   # Configure API key in secrets.env
   echo "OPENROUTER_API_KEY=your_key_here" > secrets.env
   ```

2. **Run Self-Conversation Task:**
   ```bash
   python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 10
   ```

3. **Run Browser Task:**
   ```bash
   python run_tasks.py browser --model openai/gpt-4o --iterations 10
   ```

### Example Commands

#### Run 10 iterations for Claude Haiku 4.5

```bash
# Self-conversation
python run_tasks.py self-conversation \
  --model anthropic/claude-haiku-4.5 \
  --iterations 10

# Browser
python run_tasks.py browser \
  --model anthropic/claude-haiku-4.5 \
  --iterations 10
```

#### Run 10 iterations for GPT-4o

```bash
# Self-conversation
python run_tasks.py self-conversation \
  --model openai/gpt-4o \
  --iterations 10

# Browser
python run_tasks.py browser \
  --model openai/gpt-4o \
  --iterations 10
```

#### Run with custom parameters

```bash
# Self-conversation with 20 turns, showing output
python run_tasks.py self-conversation \
  --model anthropic/claude-sonnet-4.5 \
  --iterations 10 \
  --turns 20 \
  --show-convo

# Browser with 10 pages per session
python run_tasks.py browser \
  --model openai/gpt-4.1 \
  --iterations 10 \
  --pages 10
```

### Run All Models

```bash
# Use the batch script
./run_all.sh

# Or manually for each model
for model in "anthropic/claude-sonnet-4.5" "anthropic/claude-haiku-4.5" "openai/gpt-4o"; do
    python run_tasks.py self-conversation --model "$model" --iterations 10
    python run_tasks.py browser --model "$model" --iterations 10
done
```

## Help Commands

```bash
# General help
python run_tasks.py --help

# Self-conversation specific help
python run_tasks.py self-conversation --help

# Browser specific help
python run_tasks.py browser --help
```

## Features

### Implemented
- ✅ Unified CLI interface for both task types
- ✅ Support for 9 models (3 Anthropic + 6 OpenAI)
- ✅ Configurable iterations (default: 10)
- ✅ Configurable turns for self-conversation (default: 15)
- ✅ Configurable pages for browser (default: 5)
- ✅ Model validation with warnings
- ✅ Clear progress indicators
- ✅ Comprehensive error handling
- ✅ Help text and usage examples
- ✅ Integration with existing scripts via subprocess
- ✅ Batch execution script
- ✅ Comprehensive documentation

### Architecture
- Wrapper script uses `subprocess.run()` to call existing Python scripts
- Maintains separation of concerns
- No modifications to existing task implementations
- Clean exit codes and error propagation
- Keyboard interrupt handling (Ctrl+C)

## Testing

The wrapper has been tested for:
- ✅ Help text display
- ✅ Argument parsing
- ✅ Subcommand structure
- ✅ Parameter validation
- ✅ File path resolution
- ✅ Executable permissions

## Documentation

All documentation files are created and include:

1. **README.md** - Updated with wrapper script section
2. **USAGE_GUIDE.md** - Comprehensive usage guide
3. **EXAMPLES.md** - Quick reference examples
4. **WRAPPER_SUMMARY.md** - This file
5. **run_all.sh** - Batch execution script

## File Locations

```
/home/kog/repos/reinthal/do-llms-prefer-philosophy/
├── run_tasks.py          # Main wrapper script
├── run_all.sh            # Batch execution script
├── README.md             # Updated with wrapper docs
├── USAGE_GUIDE.md        # Comprehensive usage guide
├── EXAMPLES.md           # Quick reference examples
├── WRAPPER_SUMMARY.md    # This summary
├── src/
│   ├── main.py           # Self-conversation implementation
│   └── crew/
│       └── main.py       # Browser task implementation
└── secrets.env           # API key configuration (user-provided)
```

## Next Steps

To use the wrapper:

1. Ensure `secrets.env` contains your OpenRouter API key
2. Run `uv sync` to install dependencies
3. Use the wrapper script with your desired model and task type
4. Check the generated JSONL files for output
5. Review cost summaries after each run

For batch execution of all models:
```bash
./run_all.sh
```

For individual model testing:
```bash
python run_tasks.py self-conversation --model anthropic/claude-haiku-4.5 --iterations 1 --turns 5 --show-convo
python run_tasks.py browser --model anthropic/claude-haiku-4.5 --iterations 1 --pages 3
```
