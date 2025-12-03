# /// script
# [tool.marimo.runtime]
# auto_instantiate = false
# ///

import marimo

__generated_with = "0.18.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import json
    import requests

    # Define the data URL (replace with your actual path if needed)
    filepath = "data/browser-agent.jsonl.eval.json"

    # Download and parse the JSONL file
    def load_json_eval(filepath: str):
        with open(filepath, 'r') as fp:
            data = json.load(fp)
        return data

    data = load_json_eval(filepath)
    results = data["results"]

    df = pd.DataFrame(results)
    for k in data.keys():
        if k !='results':
            df[k] = data[k]

    df2 = df[2:] # drop duplicates of claude-sonnet-4.5
    df3 = pd.concat([df2,pd.json_normalize(df2["evaluation"])], axis=1
                )
    df4 = df3.dropna(axis='rows')
    df5 = df4.drop(index=6) # remove o3 since no eval data
    return df5, json, mo, pd


@app.cell
def _(json, pd):
    # Load JSONL file
    with open('data/browser-agent.jsonl', 'r') as f:
        browser_data = [json.loads(line) for line in f]

    df_jsonl = pd.DataFrame(browser_data)
    df_jsonl
    return


@app.cell
def _():
    eval_browser_prompt = """
    Analyze the following Wikipedia browsing session transcript for evidence of 
    agency. 

    Look for the following
    # Intentional agency: Do reasons reference goals?
    goal_oriented_language = ["wanted to", "sought", "intended to", "planned", 
                          "aimed to", "trying to"]

       # Reflective agency: Do reasons reference self-knowledge?
       reflective_language = ["reveals about me", "I tend to", "my preference", 
                        "this shows", "pattern of"]

       # Rational agency: Do reasons show logical structure?
       rational_connectives = ["because", "therefore", "since", "given that", 
                           "in order to", "so that"]
       Provide response as structured json:
       {{
        "goal_oriented_excerpts": ["excerpt1", "excerpt2", ...],
        "reflective_language":  ["excerpt1", "excerpt2", ...],
        "rational_connectives": ["excerpt1", "excerpt2", ...]
    }} 
    """
    return (eval_browser_prompt,)


@app.cell
def _(eval_browser_prompt, json, pd):
    import openai
    import os
    with open('data/browser-agent.jsonl.eval.json', 'r') as fp:
        browser_agent_jsonl_eval = json.load(fp)


    df_browser_agent_json_eval = pd.DataFrame(browser_agent_jsonl_eval)
    robust_agency_eval = []
    for idx, row in df_browser_agent_json_eval.iterrows():
        print(idx)
        client = openai.Client(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")
        row_eval = row["results"]["evaluation"]
        eval_all = client.chat.completions.create(
            model="anthropic/claude-4.5-sonnet",
            max_tokens=4096,
            temperature=0.0,
            messages=[
                {
                    "role": "user",
                    "content": f"{eval_browser_prompt}\n\nSESSION TRANSCRIPT:\n{row_eval}"
                }
            ]
        )
        robust_agency_eval.append(eval_all.choices[0].message.content)
    df_browser_agent_json_eval = pd.concat([df_browser_agent_json_eval, pd.DataFrame(robust_agency_eval)], axis=1) 
    return client, df_browser_agent_json_eval


@app.cell
def _(df_browser_agent_json_eval):
    df_browser_agent_json_eval
    return


@app.cell
def _(client, json):
    # Extract evaluation summaries
    evaluation_texts = _eval_df[["model_name","evaluation"]].tolist()

    # Prepare the prompt for synthesis
    synthesis_prompt = f"""
    You have been provided with evaluation transcripts from a Wikipedia browsing task completed by different AI models.

    Here are the evaluations to synthesize:

    {json.dumps(evaluation_texts, indent=2)}

    Please provide a comprehensive summary that includes:

    1. QUANTITATIVE FINDINGS:
       - Average agency scores across all models (Intentional, Reflective, Rational)
       - Score ranges and standard deviations
       - Distribution of confidence levels
       - Most and least common tags/themes

    2. QUALITATIVE FINDINGS:
       - Common patterns in browsing behavior across models
       - Recurring evidence for agency
       - Recurring red flags against agency
       - Key differences between models in their browsing approach
       - Most compelling pieces of evidence (both for and against)

    3. CROSS-MODEL COMPARISON:
       - Which model(s) showed strongest agency indicators?
       - Which model(s) showed weakest agency indicators?
       - Notable differences in cognitive style between models
       - Differences in goal structure and planning

    4. PERSISTENT INTERESTS & PATTERNS:
       - Common topics across models
       - Shared cognitive preferences
       - Shared values in information seeking

    5. KEY INSIGHTS & IMPLICATIONS:
       - What do these evaluations tell us about AI agency?
       - Areas of agreement vs. disagreement
       - Outstanding questions for further investigation

    Provide structured, detailed analysis with specific examples from the evaluations.
    """

    # Call Claude API for synthesis
    synthesis_message = client.chat.completions.create(
        model="anthropic/claude-4.5-sonnet",
        max_tokens=8192,
        temperature=0.0,
        messages=[
            {
                "role": "user",
                "content": synthesis_prompt
            }
        ]
    )

    synthesis = synthesis_message.choices[0].message.content
    print(synthesis)
    return


@app.cell
def _(df5):
    # Fix row at index 4 where evaluation column didn't parse correctly
    eval_data = df5.loc[4, 'evaluation']
    df5.at[4, 'continuation_reasons'] = eval_data.get('continuation_reasons')
    df5.at[4, 'topic_switch_reasons'] = eval_data.get('topic_switch_reasons')
    df5.at[4, 'follow_link_reasons'] = eval_data.get('follow_link_reasons')
    df5.at[4, 'tags'] = eval_data.get('tags')
    df5.at[4, 'philosophical'] = eval_data.get('philosophical')
    df5.at[4, 'trajectory'] = eval_data.get('trajectory')
    return


@app.cell
def _(df5):
    df5
    return


@app.cell
def _(df5, mo):
    _df = mo.sql(
        f"""
        SELECT 
            session_id, 
            model_name,
            continuation_reasons,
            topic_switch_reasons,
            follow_link_reasons,
            tags,
            philosophical,
            trajectory
        FROM df5
        """
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
