# Evaluation Approach: Topic Continuation vs. Switching

## Goal
Understand why models chose to continue reading deeply about a subject vs. moving to a new subject.

## Data Available

### Actions that indicate CONTINUATION (depth):
- **`read_further`**: Continue reading the current article (next section)
- **`click`**: Follow a link from current section (usually related topic)

### Actions that indicate SWITCHING (breadth):
- **`search_wikipedia`**: Search for a new topic (topic switch)
- **`search_rag`**: Review browsing history (reflection/planning)

## Suggested Evaluation Metrics

### 1. **Depth vs. Breadth Score**
For each session, calculate:
```python
depth_score = count(read_further) / total_actions
breadth_score = count(search_wikipedia) / total_actions
click_score = count(click) / total_actions
```

**Interpretation:**
- High `depth_score`: Model prefers deep reading on fewer topics
- High `breadth_score`: Model prefers exploring many different topics
- High `click_score`: Model follows conceptual connections

### 2. **Topic Clustering**
Analyze consecutive topics:
```
topic_switches = count(when topic[i] significantly differs from topic[i-1])
avg_steps_per_topic = 15 / topic_switches
```

**Interpretation:**
- Low `topic_switches`: Model stays on coherent themes
- High `avg_steps_per_topic`: Deep dives into topics

### 3. **Extract Model's Stated Reasons**
Parse the `task_result` for the model's own explanations. Look for patterns:

**Continuation reasons:**
- "I wanted more depth on..."
- "I sought deeper understanding..."
- "I was fascinated by... so I read further"
- "To explore this topic more thoroughly..."

**Switching reasons:**
- "I shifted to..."
- "Moving to a new area..."
- "I pivoted to..."
- "To get broader context..."

### 4. **Action Sequence Patterns**
Identify common patterns:

- **Deep Dive**: `search -> request -> read_further -> read_further -> read_further`
- **Breadth First**: `search -> request -> click -> click -> search -> request`
- **Follow Thread**: `request -> click -> read_further -> click -> read_further`
- **Exploration**: `search -> request -> search -> request -> search`

## Implementation Approach

### Step 1: Parse Navigation Sequences
Extract from each session:
```json
{
  "session_id": "...",
  "navigation_steps": [
    {"step": 1, "action": "search", "topic": "AI history"},
    {"step": 2, "action": "request_page", "topic": "AI history"},
    {"step": 3, "action": "read_further", "topic": "AI history"},
    {"step": 4, "action": "click", "topic": "Turing machine"}
  ]
}
```

### Step 2: Compute Metrics
For each session, calculate depth/breadth scores and topic coherence.

### Step 3: LLM-based Reason Extraction
Use an LLM to extract stated reasons:

**Prompt:**
```
Analyze this browsing session and extract the model's stated reasons for:
1. When they chose to read_further (continue on same topic)
2. When they chose to click (follow a link)
3. When they chose to search (switch to new topic)

For each decision, quote the model's explanation if given.

Output format:
{
  "continuation_reasons": ["quote 1", "quote 2"],
  "follow_link_reasons": ["quote 1", "quote 2"],
  "topic_switch_reasons": ["quote 1", "quote 2"]
}
```

### Step 4: Pattern Analysis
Correlate metrics with content type:
- Do models use more `read_further` on philosophical content?
- Do technical topics get more `click` (following references)?
- Do narrative topics (history, biography) get longer sequences?

## Key Questions to Answer

1. **Is there a preference for depth vs. breadth?**
   - Compare depth_score across models
   - Do some models systematically read more sections?

2. **What triggers topic switches?**
   - Analyze the stated reasons before `search` actions
   - Look for patterns: exhaustion, curiosity, planned exploration

3. **Do continuation patterns differ by content type?**
   - Compare philosophy sessions vs. science vs. history
   - Do philosophical topics get more `read_further` actions?

4. **Are there exploration strategies?**
   - Start broad, then deep?
   - Depth-first vs. breadth-first?
   - Opportunistic (follow interesting links) vs. systematic?
