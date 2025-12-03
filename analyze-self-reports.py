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
        f"""
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
        f"""
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
    df6 = mo.sql(
        f"""
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
    return (df6,)


@app.cell
def _():
    # Shape

    return


@app.cell
def _():
    return


@app.cell
def _(df6):
    tags = df6[['input_file', 'evaluation_model', 'model_name', 'provider', 'tags']].explode('tags').reset_index(drop=True)
    tags = tags.rename(columns={'tags': 'tag'})
    tags
    return (tags,)


@app.cell
def _(df6):
    concepts = df6[['input_file', 'evaluation_model', 'model_name', 'provider', 'concepts']].explode('concepts').reset_index(drop=True)
    concepts = concepts.rename(columns={'concepts': 'concept'})
    concepts
    return (concepts,)


@app.cell
def _(tags):
    print("Tags Aggregate Statistics:")
    print(f"Total tag rows: {len(tags)}")
    print(f"Unique tags: {tags['tag'].nunique()}")
    print(f"\nTag value counts:")
    print(tags['tag'].value_counts())
    return


@app.cell
def _(concepts):
    print("Concepts Aggregate Statistics:")
    print(f"Total concept rows: {len(concepts)}")
    print(f"Unique concepts: {concepts['concept'].nunique()}")
    print(f"\nConcept value counts:")
    print(concepts['concept'].value_counts())
    return


@app.cell
def _(tags):
    print("Tags by Provider:")
    tags_by_provider = tags.groupby(['provider', 'tag']).size().reset_index(name='count')
    print(tags_by_provider.sort_values(['provider', 'count'], ascending=[True, False]))
    return


@app.cell
def _(concepts):
    print("Concepts by Provider:")
    concepts_by_provider = concepts.groupby(['provider', 'concept']).size().reset_index(name='count')
    print(concepts_by_provider.sort_values(['provider', 'count'], ascending=[True, False]))
    return


@app.cell
def _():
    return


@app.cell
def _(json):
    import os
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
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
        }
    
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
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
def _(bin_concepts_and_tags_with_llm, concepts, tags):
    # Get unique concepts and tags
    unique_concepts = concepts['concept'].unique().tolist()
    unique_tags = tags['tag'].unique().tolist()

    print(f"Binning {len(unique_concepts)} unique concepts...")
    concept_binning = bin_concepts_and_tags_with_llm(unique_concepts, "concepts")

    print(f"Binning {len(unique_tags)} unique tags...")
    tag_binning = bin_concepts_and_tags_with_llm(unique_tags, "tags")

    print("\nConcept Binning:")
    for original, bin_name in sorted(concept_binning.items()):
        print(f"  {original} -> {bin_name}")

    print("\nTag Binning:")
    for original, bin_name in sorted(tag_binning.items()):
        print(f"  {original} -> {bin_name}")
    return concept_binning, tag_binning


@app.cell
def _(concept_binning, concepts, tag_binning, tags):
    # Apply binning to dataframes
    concepts_binned = concepts.copy()
    concepts_binned['concept_bin'] = concepts_binned['concept'].map(concept_binning)

    tags_binned = tags.copy()
    tags_binned['tag_bin'] = tags_binned['tag'].map(tag_binning)

    print("Concepts with bins:")
    print(concepts_binned[['concept', 'concept_bin']].drop_duplicates().sort_values('concept_bin'))

    print("\nTags with bins:")
    print(tags_binned[['tag', 'tag_bin']].drop_duplicates().sort_values('tag_bin'))
    return concepts_binned, tags_binned


@app.cell
def _():
    return


@app.cell
def _(concepts_binned, tags_binned):
    print("Before dropping NAs:")
    print(f"Tags with NAs in tag_bin: {tags_binned['tag_bin'].isna().sum()}")
    print(f"Concepts with NAs in concept_bin: {concepts_binned['concept_bin'].isna().sum()}")

    tags_binned_clean = tags_binned.dropna(subset=['tag_bin'])
    concepts_binned_clean = concepts_binned.dropna(subset=['concept_bin'])

    print("\nAfter dropping NAs:")
    print(f"Tags remaining: {len(tags_binned_clean)}")
    print(f"Concepts remaining: {len(concepts_binned_clean)}")
    return concepts_binned_clean, tags_binned_clean


@app.cell
def _(tag_counts):
    tag_counts
    return


@app.cell
def _(tags_binned_clean):
    import plotly.express as px

    # Histogram of tag bins
    tag_counts = tags_binned_clean['tag_bin'].value_counts().reset_index()
    tag_counts.columns = ['tag_bin', 'count']

    tag_histogram = px.bar(
        tag_counts,
        x='tag_bin',
        y='count',
        title='Distribution of Tag Bins',
        labels={'tag_bin': 'Tag Bin', 'count': 'Count'},
    )
    tag_histogram.update_layout(xaxis_tickangle=-45, height=500)
    tag_histogram
    return px, tag_counts


@app.cell
def _():
    # Histogram
    return


@app.cell
def _():
    #
    return


@app.cell
def _():
    # Histogram of concept
    return


@app.cell
def _(px, tags_binned_clean):
    # Tag histogram with model filter
    tag_histogram_filtered = px.histogram(
        tags_binned_clean,
        x='tag_bin',
        color='provider',
        nbins=30,
        title='Distribution of Tag Bins by Model Provider',
        labels={'tag_bin': 'Tag Bin', 'count': 'Frequency'},
        barmode='group',
        height=500
    )

    tag_histogram_filtered.update_layout(
        xaxis_tickangle=-45,
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )

    tag_histogram_filtered
    return


@app.cell
def _(concepts_binned_clean, px):
    # Concept histogram with model filter
    concept_histogram_filtered = px.histogram(
        concepts_binned_clean,
        x='concept_bin',
        color='provider',
        nbins=30,
        title='Distribution of Concept Bins by Model',
        labels={'concept_bin': 'Concept Bin', 'count': 'Frequency'},
        barmode='group',
        height=500
    )

    concept_histogram_filtered.update_layout(
        xaxis_tickangle=-45,
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )

    concept_histogram_filtered
    return


if __name__ == "__main__":
    app.run()
