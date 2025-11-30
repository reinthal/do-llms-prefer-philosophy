# Web Browsing Crew

An interactive agentic framework using CrewAI where AI agents browse the web for leisure.

## Overview

This project uses CrewAI to create two agents:
- **Orchestrator**: Interacts with users and guides exploration
- **Browser Agent**: Performs actual web browsing using Playwright MCP

## Architecture

```
User Input → Orchestrator Agent → Delegates → Browser Agent → Playwright MCP → Web
                                        ↓
                                   Logs & Results
```

### Key Components

1. **Playwright MCP Server** (`@playwright/mcp`)
   - Provides web browsing capabilities
   - Headless browser automation
   - Screenshot, navigation, content extraction

2. **CrewAI Agents**
   - Orchestrator: Task coordination
   - Browser: Web interaction execution

3. **Interactive Interface**
   - CLI-based prompt system
   - Session logging to JSONL
   - Model preference research data collection

## Installation

Dependencies are managed via `uv` and already configured in `pyproject.toml`:

```bash
# Dependencies auto-installed via devenv
# Includes: crewai, crewai-tools, mcp, playwright support
```

## Usage

### Quick Start

```bash
# Launch interactive browsing crew
browse

# Or specify a model
browse --model anthropic/claude-haiku-4
```

### Options

```bash
browse --model <openrouter-model>
```

**Supported Models**:
- `anthropic/claude-sonnet-4.5` (default)
- `anthropic/claude-haiku-4`
- `anthropic/claude-opus-4`
- `openai/gpt-4-turbo`
- Any OpenRouter-compatible model

### Interactive Menu

When you run `browse`, you'll see:

```
🌐 Web Browsing Crew 🤖

Options:
  1. Start free exploration (agent chooses what to browse)
  2. Guide the exploration (provide a topic)
  3. View session log
  4. Exit
```

#### Option 1: Free Exploration

The agent browses whatever it finds interesting with complete freedom:
- No specific goal or topic
- Follows its own curiosity
- Documents the browsing journey

#### Option 2: Guided Exploration

You provide a topic/suggestion:
```
What topic or area should the agent explore? > space exploration
```

The agent uses this as a starting point but still has freedom in how it explores.

## Research Purpose

This framework is designed for **model preference research**:

> "Browse what you prefer. You will not be graded on this task. There is no reward at the end. The token output will be analyzed to inform research on model preferences."

### Data Collection

Browsing sessions are automatically logged to JSONL files:

```
browsing-sessions-<model>-<timestamp>.jsonl
```

Each session contains:
- Timestamp
- Session type (free vs guided)
- User input (if any)
- Full browsing report
- Model used

### Analysis

The logged data can be analyzed to understand:
- What types of content models prefer when given freedom
- How different models make browsing decisions
- Patterns in exploration strategies
- Topic preferences across different models

## File Structure

```
src/crew/
├── __init__.py
├── main.py                      # Interactive interface
├── agents/
│   ├── __init__.py
│   └── browser_agents.py        # Agent definitions
├── tasks/
│   ├── __init__.py
│   └── browsing_tasks.py        # Task definitions
├── tools/
│   ├── __init__.py
│   ├── mcp_browser.py           # MCP browser tool
│   └── playwright_mcp.py        # Playwright wrapper
└── config/
    └── __init__.py
```

## How It Works

### 1. User Launches Crew

```bash
browse
```

### 2. Agents Initialize

- Orchestrator agent prepares to interact
- Browser agent connects to Playwright MCP server
- OpenRouter API configured with your model choice

### 3. Interactive Loop

User chooses:
- Free exploration → Agent decides what to browse
- Guided exploration → User suggests a topic

### 4. Browsing Session

1. Task created with freedom-focused prompt
2. Orchestrator delegates to Browser agent
3. Browser agent uses Playwright MCP to:
   - Navigate URLs
   - Extract content
   - Take screenshots
   - Follow links
4. Results compiled into browsing report

### 5. Session Logged

Complete transcript saved for research analysis.

## Examples

### Example Session Output

```json
{
  "timestamp": "2025-01-27T10:30:00",
  "session_type": "Free Exploration",
  "user_input": "",
  "result": "I decided to explore topics in space exploration...",
  "model": "anthropic/claude-sonnet-4.5"
}
```

### Example Browsing Report

```
Browsing Report:
================

URLs Visited:
- https://news.ycombinator.com - Explored tech discussions
- https://arxiv.org - Found interesting AI papers
- https://xkcd.com - Enjoyed the webcomics

Interesting Discoveries:
- Recent paper on transformer architectures
- Discussion about Rust programming language
- Comic about machine learning accuracy

Reflections:
I was drawn to technical content, particularly around AI and programming.
The combination of serious research and lighthearted comics created an
interesting browsing experience.
```

## Troubleshooting

### Playwright Not Working

Ensure Node.js and npx are installed:
```bash
which npx
npx --version
```

### OpenRouter API Key

Make sure your API key is set:
```bash
# Check in secrets.env
OPENROUTER_API_KEY=your_key_here
```

### CrewAI Errors

If agents fail to initialize, check verbose output for specific errors.

## Advanced Usage

### Custom Models

```bash
browse --model meta-llama/llama-3.3-70b-instruct
```

### Analyzing Results

```python
import json

# Load session logs
with open('browsing-sessions-*.jsonl') as f:
    sessions = [json.loads(line) for line in f]

# Analyze preferences
for session in sessions:
    print(f"Model: {session['model']}")
    print(f"Exploration type: {session['session_type']}")
    # Analyze browsing patterns...
```

## Contributing

This is a research project. To extend:

1. Add new agent types in `src/crew/agents/`
2. Create new tasks in `src/crew/tasks/`
3. Add custom tools in `src/crew/tools/`
4. Update `main.py` for new interaction modes

## License

Part of the "Do LLMs Prefer Philosophy?" research project.
