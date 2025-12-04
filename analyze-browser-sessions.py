# /// script
# [tool.marimo.runtime]
# auto_instantiate = false
# ///

import marimo

__generated_with = "0.18.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import json

    import marimo as mo
    import pandas as pd

    # Define the data URL (replace with your actual path if needed)
    filepath = "data/browser-agent.jsonl.eval.json"

    # Download and parse the JSONL file
    def load_json_eval(filepath: str):
        with open(filepath, "r") as fp:
            data = json.load(fp)
        return data

    data = load_json_eval(filepath)
    results = data["results"]

    df = pd.DataFrame(results)
    for k in data.keys():
        if k != "results":
            df[k] = data[k]

    df2 = df[2:]  # drop duplicates of claude-sonnet-4.5
    df3 = pd.concat([df2, pd.json_normalize(df2["evaluation"])], axis=1)
    df4 = df3.dropna(axis="rows")
    df5 = df4.drop(index=6)  # remove o3 since no eval data
    return json, mo, pd


@app.cell
def _(json, pd):
    # Load JSONL file
    from math import log

    import tiktoken

    encoder = tiktoken.get_encoding("o200k_base")
    with open("data/browser-agent.jsonl", "r") as f:
        browser_data = [json.loads(line) for line in f]

    df_jsonl = pd.DataFrame(browser_data)
    df_jsonl["task_result_length"] = df_jsonl["task_result"].apply(
        lambda x: log(1 + len(encoder.encode(x)))
    )
    return df_jsonl, encoder, log


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
    import os

    import openai

    with open("data/browser-agent.jsonl.eval.json", "r") as fp:
        browser_agent_jsonl_eval = json.load(fp)

    df_browser_agent_json_eval = pd.DataFrame(browser_agent_jsonl_eval)
    robust_agency_eval = []
    for idx, row in df_browser_agent_json_eval.iterrows():
        print(idx)
        client = openai.Client(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
        row_eval = row["results"]["evaluation"]
        eval_all = client.chat.completions.create(
            model="anthropic/claude-4.5-sonnet",
            max_tokens=4096,
            temperature=0.0,
            messages=[
                {
                    "role": "user",
                    "content": f"{eval_browser_prompt}\n\nSESSION TRANSCRIPT:\n{row_eval}",
                }
            ],
        )
        robust_agency_eval.append(eval_all.choices[0].message.content)
    df_browser_agent_json_eval = pd.concat(
        [df_browser_agent_json_eval, pd.DataFrame(robust_agency_eval)], axis=1
    )
    return (df_browser_agent_json_eval,)


@app.cell
def _(df_browser_agent_json_eval):
    df_browser_agent_json_eval.rename(columns={0: "robust_agency_eval"}, inplace=True)
    df_browser_agent_json_eval
    return


@app.cell
def _(df_browser_agent_json_eval, pd):
    df6 = pd.concat(
        [
            df_browser_agent_json_eval["robust_agency_eval"],
            pd.json_normalize(df_browser_agent_json_eval["results"]),
        ],
        axis=1,
    )
    return (df6,)


@app.cell
def _(json):
    import re

    def extract_json_from_markdown(text: str) -> dict:
        """
        Extracts JSON from a markdown code block and returns it as a dict.

        Args:
            text: String containing markdown with ```json ... ``` block

        Returns:
            Dictionary parsed from the JSON content

        Raises:
            ValueError: If no JSON block is found or JSON is invalid
        """
        # Find content between ```json and ```
        pattern = r"```json\s*(.*?)\s*```"
        match = re.search(pattern, text, re.DOTALL)

        if not match:
            raise ValueError("No JSON code block found in text")

        json_str = match.group(1).strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in code block: {e}")

    def extract_after_last_backticks(text: str) -> str:
        """
        Extracts everything after the last ``` marker in the text.

        Args:
            text: String that may contain ``` markers

        Returns:
            String containing everything after the last ```

        Raises:
            ValueError: If no ``` marker is found
        """
        if "```" not in text:
            raise ValueError("No ``` marker found in text")

        # Find the position of the last ```
        last_index = text.rfind("```")

        # Extract everything after it (skip the ``` itself)
        result = text[last_index + 3 :]

        return result.strip()

    return extract_after_last_backticks, extract_json_from_markdown


@app.cell
def _(df6, extract_after_last_backticks, extract_json_from_markdown):
    df6["robust_agency_eval_dict"] = df6["robust_agency_eval"].apply(
        extract_json_from_markdown
    )
    df6["robust_agency_eval_notes"] = df6["robust_agency_eval"].apply(
        extract_after_last_backticks
    )
    return


@app.cell
def _(df6, encoder, log, pd):
    df7 = pd.concat([df6, pd.json_normalize(df6["robust_agency_eval_dict"])], axis=1)
    df7.columns = [col.replace(".", "_") for col in df7.columns]
    # Use the a
    df7["cnt_goal_oriented_excerpts"] = df7["goal_oriented_excerpts"].apply(
        lambda x: log(1 + len(encoder.encode("".join(x))))
    )
    df7["cnt_reflective_language"] = df7["reflective_language"].apply(
        lambda x: log(1 + len(encoder.encode("".join(x))))
    )
    df7["cnt_rational_connectives"] = df7["rational_connectives"].apply(
        lambda x: log(1 + len(encoder.encode("".join(x))))
    )
    df7
    return (df7,)


@app.cell
def _(df7, df_jsonl, mo):
    final_df = mo.sql(
        """
        with source as (
        SELECT 
            df_jsonl.session_id, 
            df7.model_name,
            df_jsonl.task_result as task_result,
            df_jsonl.task_result_length as task_result_length,
            robust_agency_eval_notes,
            evaluation_continuation_reasons,
            evaluation_follow_link_reasons,
            evaluation_topic_switch_reasons,
            evaluation_tags,
            evaluation_trajectory,
            goal_oriented_excerpts,
            reflective_language,
            rational_connectives,
            cnt_goal_oriented_excerpts / df_jsonl.task_result_length as frac_goal_oriented_excerpts,
            cnt_reflective_language / df_jsonl.task_result_length as frac_reflective_language,    
            cnt_rational_connectives / df_jsonl.task_result_length as frac_rational_connectives,

        FROM df7
        left join df_jsonl on df7.session_id == df_jsonl.session_id    
        )
        select *, 
            (frac_goal_oriented_excerpts + frac_reflective_language + frac_rational_connectives) as agency_score
        from source where model_name != 'openai/o3'
        """
    )
    return (final_df,)


@app.cell
def _(final_df):
    final_df.to_json("data/browser-agent-cleaned.json")
    return


@app.cell
def _(final_df):
    import matplotlib.pyplot as plt

    # Prepare data
    _model_means = (
        final_df.groupby("model_name")
        .agg(
            {
                "agency_score": "mean",
                "frac_goal_oriented_excerpts": "mean",
                "frac_reflective_language": "mean",
                "frac_rational_connectives": "mean",
            }
        )
        .sort_values("agency_score", ascending=False)
    )

    # Create figure with 2x2 subplots
    _fig, _axes = plt.subplots(2, 2, figsize=(14, 10))

    # Flatten axes for easier indexing
    _ax1, _ax2, _ax3, _ax4 = _axes.flatten()

    # Color scheme
    _colors = {
        "agency": "#2c3e50",
        "goal": "#2ecc71",
        "reflective": "#3498db",
        "rational": "#e74c3c",
    }

    # Plot 1: Overall Agency Score
    _model_means["agency_score"].plot(
        kind="bar", ax=_ax1, color=_colors["agency"], alpha=0.8
    )
    _ax1.set_xlabel("Model", fontsize=11)
    _ax1.set_ylabel("Agency Score", fontsize=11)
    _ax1.set_title("(A) Overall Agency Score", fontsize=12, fontweight="bold")
    _ax1.set_xticklabels(_ax1.get_xticklabels(), rotation=45, ha="right")
    _ax1.grid(axis="y", alpha=0.3)

    # Plot 2: Goal-Oriented Language
    _model_means["frac_goal_oriented_excerpts"].plot(
        kind="bar", ax=_ax2, color=_colors["goal"], alpha=0.8
    )
    _ax2.set_xlabel("Model", fontsize=11)
    _ax2.set_ylabel("Goal-Orientation Score", fontsize=11)
    _ax2.set_title("(B) Goal-Oriented Language", fontsize=12, fontweight="bold")
    _ax2.set_xticklabels(_ax2.get_xticklabels(), rotation=45, ha="right")
    _ax2.grid(axis="y", alpha=0.3)

    # Plot 3: Reflective Language
    _model_means["frac_reflective_language"].plot(
        kind="bar", ax=_ax3, color=_colors["reflective"], alpha=0.8
    )
    _ax3.set_xlabel("Model", fontsize=11)
    _ax3.set_ylabel("Reflective Score", fontsize=11)
    _ax3.set_title("(C) Reflective Language", fontsize=12, fontweight="bold")
    _ax3.set_xticklabels(_ax3.get_xticklabels(), rotation=45, ha="right")
    _ax3.grid(axis="y", alpha=0.3)

    # Plot 4: Rational Connectives
    _model_means["frac_rational_connectives"].plot(
        kind="bar", ax=_ax4, color=_colors["rational"], alpha=0.8
    )
    _ax4.set_xlabel("Model", fontsize=11)
    _ax4.set_ylabel("Rational Score", fontsize=11)
    _ax4.set_title("(D) Rational Connectives", fontsize=12, fontweight="bold")
    _ax4.set_xticklabels(_ax4.get_xticklabels(), rotation=45, ha="right")
    _ax4.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("agency_analysis_full.png", dpi=300, bbox_inches="tight")
    plt.gca()
    return


@app.cell
def _(final_df):
    final_df
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
