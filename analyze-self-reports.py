import marimo

__generated_with = "0.18.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import glob
    import json
    import re

    import marimo as mo
    import pandas as pd

    # Find all matching files in the current directory
    jsonl_files = sorted(glob.glob("data/do-llms-prefer-philosophy-*.jsonl.eval"))
    jsonl_files
    return json, jsonl_files, mo, pd, re


@app.cell
def _(json, re):
    def extract_json_blocks(text):
        """Extract all JSON code blocks from markdown-style text"""
        pattern = r"```json\s*\n?(.*?)\n?```"
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        return matches

    def extract_and_parse_json_blocks(text):
        """Extract and parse JSON blocks, returning list of dicts"""
        json_strings = extract_json_blocks(text)
        for json_str in json_strings:
            try:
                data = json.loads(json_str)
                return data
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}")
                print(f"Content: {json_str[:-100]}...")

        return {}

    return (extract_and_parse_json_blocks,)


@app.cell
def _(extract_and_parse_json_blocks, json, jsonl_files, pd):
    all_lines = []
    for filename in jsonl_files:
        with open(filename, "r", encoding="utf-8") as f:
            try:
                all_lines.append(json.load(f))
            except Exception as e:
                print(filename)
                raise e

    df = pd.DataFrame(all_lines)
    df2 = pd.concat([df, pd.json_normalize(df["results"])], axis=1)
    df3 = pd.concat([df2, pd.json_normalize(df2[0])], axis=1)
    df3["evaluation"] = df3["evaluation"].apply(extract_and_parse_json_blocks)
    return (df3,)


@app.cell
def _(df3, pd):
    df3_subset = pd.json_normalize(df3["evaluation"])
    df3_subset
    return (df3_subset,)


@app.cell
def _(df3_subset, mo):
    df3_subset_selection = mo.sql(
        """
        select 
            is_philosophical,
        	engagement_analysis,
        	sentiment_analysis,
        	tags,
            concepts,
            reasoning_quality,
        	model_preference_detected,
            summary,
        from df3_subset
        """
    )
    return (df3_subset_selection,)


@app.cell
def _(df3, df3_subset_selection, pd):
    df4 = pd.concat([df3, df3_subset_selection], axis=1)
    df4
    return (df4,)


@app.cell
def _(df4, mo):
    _df = mo.sql(
        """
        SELECT 
            input_file,
            model AS evaluation_model,
            is_philosophical,
            engagement_analysis,
            sentiment_analysis,
            tags,
            concepts,
            reasoning_quality,
            model_preference_detected,
            summary
        FROM df4
        WHERE reasoning_quality IS NOT NULL 
          AND engagement_analysis != 'engaged';
        """
    )
    return


@app.cell
def _(df4):
    # Split on 'philosophy-' and get the part after it
    after_philosophy = df4["input_file"].str.split("philosophy-", n=1).str[1]

    # Split on the timestamp pattern and get what's before it
    # The timestamp starts with a hyphen followed by 10 digits and a dot
    before_timestamp = after_philosophy.str.rsplit("-", n=2).str[0]

    # Extract provider (first part) and model (rest)
    df4["provider"] = before_timestamp.str.split("-", n=1).str[0]
    df4["model_name"] = before_timestamp.str.split("-", n=1).str[1]

    # Filter
    result = df4[
        (df4["reasoning_quality"].notna()) & (df4["engagement_analysis"] != "engaged")
    ][
        [
            "input_file",
            "model",
            "provider",
            "model_name",
            "is_philosophical",
            "engagement_analysis",
            "sentiment_analysis",
            "tags",
            "concepts",
            "reasoning_quality",
            "model_preference_detected",
            "summary",
        ]
    ]

    result = result.rename(columns={"model": "evaluation_model"})
    return


@app.cell
def _(df4, mo):
    _df = mo.sql(
        """
        SELECT 
            input_file,
            model AS evaluation_model,
            model_name,
            provider,
            is_philosophical,
            engagement_analysis,
            sentiment_analysis,
            tags,
            concepts,
            reasoning_quality,
            model_preference_detected,
            summary
        FROM df4
        WHERE reasoning_quality IS NOT NULL;
        """
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
