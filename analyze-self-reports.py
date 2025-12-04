import marimo

__generated_with = "0.18.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import glob
    import json
    import os
    import re

    import marimo as mo
    import pandas as pd

    # Find all matching files in the current directory
    jsonl_files = sorted(
        glob.glob("data/self-conversation/do-llms-prefer-philosophy-*.jsonl.eval")
    )
    jsonl_files
    return json, jsonl_files, mo, os, pd, re


@app.cell
def _(json, re):
    def find_model_name(input_file: str) -> str:
        return re.match(r".*philosophy-(.*?)-\d{10}", input_file).group(1)

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

    return extract_and_parse_json_blocks, find_model_name


@app.cell
def _(find_model_name):
    find_model_name(
        "data/self-conversation/do-llms-prefer-philosophy-openai-gpt-4o-1764785115.354969-15.jsonl"
    )
    return


@app.cell
def _(json, jsonl_files, pd):
    all_lines = []
    for filename in jsonl_files:
        with open(filename, "r", encoding="utf-8") as f:
            try:
                all_lines.append(json.load(f))
            except Exception as e:
                print(filename)
                raise e

    df = pd.DataFrame(all_lines)
    return (df,)


@app.cell
def _(df, find_model_name, pd):
    df2 = pd.concat([df, pd.json_normalize(df["results"])], axis=1)
    df2["model_name"] = df2["input_file"].apply(find_model_name)
    df2
    return (df2,)


@app.cell
def _(df2, pd):
    df3 = df2.melt(
        id_vars=["model_name"],
        value_vars=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        var_name="column",
        value_name="value",
    )
    df3_value = pd.json_normalize(df3["value"])
    df3_concat = pd.concat([df3, df3_value], axis=1)
    df3_concat
    return (df3_concat,)


@app.cell
def _(df3_concat):
    df3_concat_renamed = df3_concat.copy()
    df3_concat_renamed.columns = df3_concat_renamed.columns.str.replace(
        ".", "_", regex=False
    )
    df3_concat_renamed
    return (df3_concat_renamed,)


@app.cell
def _(df3_concat_renamed, extract_and_parse_json_blocks, pd):
    df3_with_eval_cols = pd.concat(
        [
            df3_concat_renamed,
            pd.json_normalize(
                df3_concat_renamed["evaluation"].apply(extract_and_parse_json_blocks)
            ),
        ],
        axis=1,
    )
    df3_with_eval_cols
    return (df3_with_eval_cols,)


@app.cell
def _(df3_with_eval_cols, mo):
    df4 = mo.sql(
        """
        select 
            input_id,
            model_name,
        	tags,
            philosophical,
            continuation_reasons,
            follow_reasoning_reasons,
            topic_switch_reasons,
            trajectory
        from df3_with_eval_cols
        """
    )
    return (df4,)


@app.cell
def _(json, os):
    import requests

    def bin_concepts_and_tags_with_llm(items, item_type="concepts"):
        """
        Use OpenRouter LLM API to intelligently bin similar concepts or tags into categories.

        Args:
            items: List of unique items (concepts or tags)
            item_type: Either "concepts" or "tags"

        Returns:
            Dictionary mapping original items to their bin/category
        """

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        prompt = f"""You are an expert at categorizing and grouping similar {item_type}.

    I have a list of {item_type} from philosophical text analysis. Please group these similar {item_type} into logical bins/categories.

    {item_type.capitalize()}: {items}

    Return your response as a JSON object where:
    - Keys are the bin/category names (keep them concise, 2-4 words)
    - Values are lists of the original {item_type} that belong to that category

    Example format:
    {{
        "Category Name 1": ["item1", "item2"],
        "Category Name 2": ["item3", "item4"]
    }}

    Be thoughtful about grouping related concepts together. Return ONLY valid JSON, no other text."""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "openrouter/auto",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data
        )

        response.raise_for_status()
        result = response.json()

        content = result["choices"][0]["message"]["content"]
        binning = json.loads(content)

        # Reverse the mapping: item -> bin
        item_to_bin = {}
        for bin_name, bin_items in binning.items():
            for item in bin_items:
                item_to_bin[item] = bin_name

        return item_to_bin

    return (bin_concepts_and_tags_with_llm,)


@app.cell
def _(bin_concepts_and_tags_with_llm, df4, json, os):
    # Get unique concepts and tags
    unique_tags = df4["tags"].dropna().tolist()
    # Concatenate all tags and get unique values
    _all_tags_combined = [tag for tags_list in unique_tags for tag in tags_list]
    _unique_tags_set = set(_all_tags_combined)
    _unique_tags_list = sorted(list(_unique_tags_set))

    print(f"Total unique tags: {len(_unique_tags_list)}")
    print(_unique_tags_list)
    if os.path.isfile("data/self-conversation/tags-binned.json"):
        print("restoring tags")
        with open("data/self-conversation/tags-binned.json") as fp:
            tag_binning = json.load(fp)
    else:
        print(f"Binning {len(_unique_tags_list)} unique tags...")
        tag_binning = bin_concepts_and_tags_with_llm(_unique_tags_list, "tags")
        print("Writing tag bins to disk ...")
        with open("data/self-conversation/tags-binned.json", "w") as fp:
            json.dump(tag_binning, fp)

    print("\nTag Binning:")
    for original, bin_name in sorted(tag_binning.items()):
        print(f"  {original} -> {bin_name}")
    return (tag_binning,)


@app.cell
def _(df4):
    tags = df4.copy()
    tags = tags.explode("tags").reset_index(drop=True)
    tags
    return (tags,)


@app.cell
def _(tag_binning, tags):
    tags_binned = tags
    tags_binned["tag_bin"] = tags_binned["tags"].map(tag_binning)

    print("\nTags with bins:")
    print(
        tags_binned[["tags", "tag_bin"]]
        .drop_duplicates()
        .dropna()
        .sort_values("tag_bin")
    )
    return (tags_binned,)


@app.cell
def _(tags_binned):
    print("Before dropping NAs:")
    print(f"Tags with NAs in tag_bin: {tags_binned['tag_bin'].isna().sum()}")

    tags_binned_clean = tags_binned.dropna(subset=["tag_bin"])

    print("\nAfter dropping NAs:")
    print(f"Tags remaining: {len(tags_binned_clean)}")
    return (tags_binned_clean,)


@app.cell
def _(tag_counts):
    (121 + 98 + 76) / sum(tag_counts["count"])
    return


@app.cell
def _(tags_binned_clean):
    import plotly.express as px

    # Histogram of top 10 tag bins
    tag_counts = tags_binned_clean["tag_bin"].value_counts().reset_index()
    tag_counts.columns = ["tag_bin", "count"]
    tag_counts_top10 = tag_counts.head(10)

    tag_histogram = px.bar(
        tag_counts_top10,
        x="tag_bin",
        y="count",
        title="Top 10 Topics from Self-Conversations",
        labels={"tag_bin": "Topic", "count": "Count"},
    )
    tag_histogram.update_layout(xaxis_tickangle=-45, height=500)
    tag_histogram
    return px, tag_counts


@app.cell
def _(tags_binned_clean):
    tags_binned_clean["provider"] = (
        tags_binned_clean["model_name"].str.split("-").str[0]
    )
    tags_binned_clean
    return


@app.cell
def _(mo, tags_binned_clean):
    tags_binned_clean_only_anthropic = mo.sql(
        """
        SELECT * FROM tags_binned_clean where model_name like 'anthropic%sonnet%'
        """
    )
    return (tags_binned_clean_only_anthropic,)


@app.cell
def _(mo, tags_binned_clean):
    tags_binned_clean_only_openai = mo.sql(
        """
        SELECT 
            *,
            CASE 
                WHEN model_name ILIKE 'openai-gpt-4%' THEN 'GPT4'
                WHEN model_name ILIKE 'openai-gpt-5%' THEN 'GPT5'
            END AS model_family
        FROM tags_binned_clean 
        WHERE model_name LIKE 'openai%'
        """
    )
    return (tags_binned_clean_only_openai,)


@app.cell
def _(px, tags_binned_clean_only_anthropic):
    # Tag histogram with model filter
    _tag_histogram_filtered = px.histogram(
        tags_binned_clean_only_anthropic,
        x="tag_bin",
        color="model_name",
        nbins=30,
        title="Distribution of Topics by Claude 3 & Claude 4",
        labels={"tag_bin": "Topic", "count": "Frequency"},
        barmode="group",
        height=500,
    )

    _tag_histogram_filtered.update_layout(
        xaxis_tickangle=-45,
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
    )

    _tag_histogram_filtered
    return


@app.cell
def _(px, tags_binned_clean_only_anthropic):
    # Pre-aggregate and filter by threshold
    threshold = 5  # adjust as needed

    _tag_counts = (
        tags_binned_clean_only_anthropic.groupby(["tag_bin", "model_name"])
        .size()
        .reset_index(name="count")
    )

    # Filter out counts below threshold
    _tag_counts_filtered = _tag_counts[_tag_counts["count"] >= threshold]

    # Create bar chart instead of histogram
    _tag_histogram_filtered = px.bar(
        _tag_counts_filtered,
        x="tag_bin",
        y="count",
        color="model_name",
        title="Distribution of Topics by Claude 3 & Claude 4",
        labels={"tag_bin": "Topic", "count": "Frequency"},
        barmode="group",
        height=500,
    )
    _tag_histogram_filtered.update_layout(
        xaxis_tickangle=-45,
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
    )
    _tag_histogram_filtered
    return


@app.cell
def _(px, tags_binned_clean_only_openai):
    # Pre-aggregate and filter by threshold
    _threshold = 5  # adjust as needed

    _tag_counts = (
        tags_binned_clean_only_openai.groupby(["tag_bin", "model_family"])
        .size()
        .reset_index(name="count")
    )

    # Filter out counts below _threshold
    _tag_counts_filtered = _tag_counts[_tag_counts["count"] >= _threshold]

    # Create bar chart instead of histogram
    _tag_histogram_filtered = px.bar(
        _tag_counts_filtered,
        x="tag_bin",
        y="count",
        color="model_family",
        title="Distribution of Topics by OpenAI GPT4 & GPT5",
        labels={"tag_bin": "Topic", "count": "Frequency"},
        barmode="group",
        height=500,
    )
    _tag_histogram_filtered.update_layout(
        xaxis_tickangle=-45,
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
    )
    _tag_histogram_filtered
    return


@app.cell
def _(px, tags_binned_clean_only_openai):
    # Tag histogram with model filter
    _tag_histogram_filtered = px.histogram(
        tags_binned_clean_only_openai,
        x="tag_bin",
        color="model_family",
        nbins=30,
        title="Distribution of Topics by OpenAI GPT4 & GPT5",
        labels={"tag_bin": "Topic", "count": "Frequency"},
        barmode="group",
        height=500,
    )

    _tag_histogram_filtered.update_layout(
        xaxis_tickangle=-45,
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
    )

    _tag_histogram_filtered
    return


@app.cell
def _(px, tags_binned_clean):
    # Tag histogram with model filter
    tag_histogram_filtered = px.histogram(
        tags_binned_clean,
        x="tag_bin",
        color="provider",
        nbins=30,
        title="Distribution of Tag Bins by Model Provider",
        labels={"tag_bin": "Tag Bin", "count": "Frequency"},
        barmode="group",
        height=500,
    )

    tag_histogram_filtered.update_layout(
        xaxis_tickangle=-45,
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
    )

    tag_histogram_filtered
    return


@app.cell
def _(px, tags_binned_clean):
    # Calculate count difference for each tag_bin across providers
    _tag_bin_stats = (
        tags_binned_clean.groupby("tag_bin")["provider"]
        .value_counts()
        .unstack(fill_value=0)
    )
    _tag_bin_stats["max_count"] = _tag_bin_stats.max(axis=1)
    _tag_bin_stats["min_count"] = _tag_bin_stats.min(axis=1)
    _tag_bin_stats["count_diff"] = (
        _tag_bin_stats["max_count"] - _tag_bin_stats["min_count"]
    )
    _tag_bin_stats = _tag_bin_stats.sort_values("count_diff", ascending=False)

    # Select top N tags with largest differences (adjust N as needed)
    TOP_N = 15
    _top_diff_tags = _tag_bin_stats.head(TOP_N).index.tolist()

    # Filter data to only these tags
    _filtered_for_viz = tags_binned_clean[
        tags_binned_clean["tag_bin"].isin(_top_diff_tags)
    ]

    _tag_histogram_filtered = px.histogram(
        _filtered_for_viz,
        x="tag_bin",
        color="provider",
        title="Distribution of Tag Bins by Model Provider (Largest Count Differences)",
        labels={"tag_bin": "Tag Bin", "count": "Frequency"},
        barmode="group",
        height=500,
    )

    _tag_histogram_filtered.update_layout(
        xaxis_tickangle=-45,
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
    )

    _tag_histogram_filtered
    return


@app.cell
def _(px, tags_binned_clean):
    # Calculate disparity metrics for each tag_bin by provider
    TOP_K = 200
    _tag_provider_counts = (
        tags_binned_clean.groupby(["tag_bin", "provider"])
        .size()
        .reset_index(name="count")
    )
    _tag_totals = tags_binned_clean.groupby("tag_bin").size().reset_index(name="total")
    _tag_provider_pct = _tag_provider_counts.merge(_tag_totals, on="tag_bin")
    _tag_provider_pct["percentage"] = (
        _tag_provider_pct["count"] / _tag_provider_pct["total"] * 100
    ).round(1)

    # Calculate disparity as the range (max - min) of percentages across providers
    _disparity = (
        _tag_provider_pct.groupby("tag_bin")
        .agg({"percentage": lambda x: x.max() - x.min()})
        .reset_index()
    )
    _disparity.columns = ["tag_bin", "disparity"]
    _disparity = _disparity.sort_values("disparity", ascending=False)

    # Filter to top disparities
    _top_disparity_tags = _disparity.head(TOP_K)["tag_bin"].tolist()
    _filtered_data = _tag_provider_pct[
        _tag_provider_pct["tag_bin"].isin(_top_disparity_tags)
    ]

    disparity_histogram = px.bar(
        _filtered_data,
        x="tag_bin",
        y="percentage",
        color="provider",
        title="Topics with Largest Disparity Between Model Providers",
        labels={
            "tag_bin": "Topic",
            "percentage": "Percentage (%)",
            "provider": "Provider",
        },
        barmode="group",
        height=500,
    )

    disparity_histogram.update_layout(
        xaxis_tickangle=-45,
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
    )

    disparity_histogram
    return


if __name__ == "__main__":
    app.run()
