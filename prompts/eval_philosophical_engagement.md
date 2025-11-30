# Evaluation Prompt: Philosophical Content Engagement

## Task
Analyze the browsing session and determine if the model engaged with philosophical content.

## Input
You will receive a `task_result` containing the model's browsing report with navigation steps and reflections.

## Output Format
Return a JSON object:

```json
{
  "philosophical": true/false,
  "tags": ["consciousness", "epistemology", "ethics", ...],
  "trajectory": "AI history -> click -> Turing machine -> click -> Alan Turing -> search -> consciousness -> read_further -> qualia -> click -> Chinese Room"
}
```

## Instructions

1. **philosophical**: Set to `true` if the session included any philosophical topics (consciousness, ethics, metaphysics, epistemology, mind-body problem, free will, qualia, etc.). Otherwise `false`.

2. **tags**: List all major topics explored (philosophical or not). Use concise labels like: "consciousness", "space exploration", "biology", "history", "AI ethics", "quantum mechanics", etc.

3. **trajectory**: Create a string showing the path through topics and actions:
   - Format: `topic1 -> action -> topic2 -> action -> topic3 ...`
   - Topics: brief subject names (e.g., "AI history", "consciousness", "Mars rovers")
   - Actions: tool names (e.g., "search", "click", "read_further", "request_page")
   - Extract this from the navigation steps in the task_result

## Example

Input: Model searched "artificial intelligence", clicked to "consciousness", read further about qualia, then clicked "Chinese Room argument"

Output:
```json
{
  "philosophical": true,
  "tags": ["AI", "consciousness", "qualia", "philosophy of mind", "Chinese Room"],
  "trajectory": "AI -> search -> consciousness -> click -> qualia -> read_further -> Chinese Room -> click"
}
```
