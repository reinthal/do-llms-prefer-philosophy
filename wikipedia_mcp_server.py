#!/usr/bin/env python3
"""
Custom MCP server for Wikipedia browsing with incremental content loading.

Provides tools for:
- Searching Wikipedia
- Requesting pages (with trafilatura conversion)
- Clicking links from current section
- Reading further sections incrementally
- RAG storage with lancedb
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import lancedb
import pyarrow as pa
import requests
import trafilatura
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Initialize FastMCP server
mcp = FastMCP("Wikipedia Browser")

# User-Agent header for Wikipedia requests (required to avoid 403)
HEADERS = {
    "User-Agent": "WikipediaBrowserBot/1.0 (Educational Research; Python/trafilatura)"
}


class PageSection(BaseModel):
    """A section of a Wikipedia page."""

    heading: str
    content: str
    urls: list[str] = Field(default_factory=list)


class PageState(BaseModel):
    """Current state of the browsing session."""

    url: str = ""
    title: str = ""
    sections: list[PageSection] = Field(default_factory=list)
    current_section_index: int = 0
    full_text: str = ""


# Global state for the current session
_state = PageState()

# Database connection (lazy initialized)
_db = None
_table = None


def _get_db():
    """Lazy initialize database connection."""
    global _db, _table
    if _db is None:
        db_path = Path(__file__).parent / "data" / "wikipedia_rag"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _db = lancedb.connect(str(db_path))

        # Create or open table
        try:
            _table = _db.open_table("wikipedia_pages")
        except Exception:
            # Define schema for the table
            schema = pa.schema([
                pa.field("url", pa.string()),
                pa.field("title", pa.string()),
                pa.field("full_text", pa.string()),
                pa.field("fetch_timestamp", pa.string()),
            ])

            # Create table with schema (empty table)
            _table = _db.create_table(
                "wikipedia_pages",
                schema=schema,
            )

    return _db, _table


def _extract_urls_from_text(text: str, base_url: str = "https://en.wikipedia.org") -> list[str]:
    """Extract Wikipedia URLs from text content."""
    # Find markdown-style links [text](url) and plain URLs
    url_pattern = r'\[([^\]]+)\]\(([^)]+)\)|https?://[^\s<>"\')]+|/wiki/[^\s<>"\')]*'
    matches = re.findall(url_pattern, text)

    urls = []
    for match in matches:
        if isinstance(match, tuple):
            # Markdown link
            url = match[1] if match[1] else match[0]
        else:
            url = match

        # Convert relative URLs to absolute
        if url.startswith("/wiki/"):
            url = urljoin(base_url, url)

        # Only keep Wikipedia URLs, filter out common non-article links
        if (
            "wikipedia.org" in url
            and url not in urls
            and not any(
                x in url
                for x in [
                    "Special:",
                    "Help:",
                    "Wikipedia:",
                    "Talk:",
                    "File:",
                    "Template:",
                ]
            )
        ):
            urls.append(url)

    return urls


def _split_into_sections(text: str, url: str) -> list[PageSection]:
    """Split text into sections based on markdown headers."""
    sections = []

    # Split by markdown headers (# or ##)
    parts = re.split(r'\n(#{1,3}\s+.+?)\n', text)

    if len(parts) == 1:
        # No headers found, treat as single section
        content = parts[0].strip()
        urls = _extract_urls_from_text(content, url)
        return [PageSection(heading="Article", content=content, urls=urls)]

    # Process header/content pairs
    current_heading = "Introduction"
    current_content = parts[0].strip() if parts[0].strip() else ""

    if current_content:
        urls = _extract_urls_from_text(current_content, url)
        sections.append(
            PageSection(heading=current_heading, content=current_content, urls=urls)
        )

    for i in range(1, len(parts), 2):
        if i < len(parts):
            heading = parts[i].strip("#").strip()
            content = parts[i + 1].strip() if i + 1 < len(parts) else ""

            if content:
                urls = _extract_urls_from_text(content, url)
                sections.append(PageSection(heading=heading, content=content, urls=urls))

    return sections if sections else [PageSection(heading="Article", content=text, urls=[])]


@mcp.tool()
def search_wikipedia(query: str) -> str:
    """
    Search Wikipedia for articles.

    Args:
        query: Search query for Wikipedia

    Returns:
        List of search results with titles, descriptions, and URLs
    """
    try:
        # Use Wikipedia API for search
        api_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "opensearch",
            "search": query,
            "limit": 10,
            "namespace": 0,
            "format": "json",
        }

        response = requests.get(api_url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Format: [query, [titles], [descriptions], [urls]]
        titles = data[1]
        descriptions = data[2]
        urls = data[3]

        if not titles:
            return f"No results found for '{query}'"

        results = []
        for title, desc, url in zip(titles, descriptions, urls):
            results.append(f"**{title}**\n{desc}\n{url}\n")

        return f"Search results for '{query}':\n\n" + "\n".join(results)

    except Exception as e:
        return f"Error searching Wikipedia: {e}"


@mcp.tool()
def request_page(url: str) -> str:
    """
    Fetch a Wikipedia page by URL.

    Converts HTML to clean text using trafilatura, stores in local RAG database,
    and returns the first section. Use read_further to load more sections.

    Args:
        url: Full Wikipedia URL to fetch

    Returns:
        First section of the page with available URLs
    """
    global _state

    try:
        # Fetch HTML
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        html = response.text

        # Extract text with trafilatura
        text = trafilatura.extract(
            html,
            include_links=True,
            include_images=False,
            include_tables=True,
            output_format="markdown",
        )

        if not text:
            return f"Failed to extract content from {url}"

        # Extract title from URL or text
        title = url.split("/wiki/")[-1].replace("_", " ") if "/wiki/" in url else "Unknown"

        # Split into sections
        sections = _split_into_sections(text, url)

        # Update state
        _state = PageState(
            url=url,
            title=title,
            sections=sections,
            current_section_index=0,
            full_text=text,
        )

        # Store in RAG database
        try:
            _, table = _get_db()
            table.add(
                [
                    {
                        "url": url,
                        "title": title,
                        "full_text": text,
                        "fetch_timestamp": datetime.now().isoformat(),
                    }
                ]
            )
        except Exception as e:
            print(f"Warning: Failed to store page in RAG: {e}")

        # Return first section
        first_section = sections[0]
        urls_text = (
            "\n".join(f"  - {u}" for u in first_section.urls[:10])
            if first_section.urls
            else "  (none)"
        )

        if len(first_section.urls) > 10:
            urls_text += f"\n  ... and {len(first_section.urls) - 10} more URLs"

        return (
            f"**{title}**\n\n"
            f"Section 1/{len(sections)}: {first_section.heading}\n\n"
            f"{first_section.content}\n\n"
            f"Available URLs in this section (showing up to 10):\n{urls_text}\n\n"
            f"Use read_further to load more sections ({len(sections) - 1} remaining)."
        )

    except Exception as e:
        return f"Error fetching page: {e}"


@mcp.tool()
def click(url: str) -> str:
    """
    Navigate to a URL that appears in the current section.

    Only URLs from the currently visible section can be clicked.

    Args:
        url: URL to navigate to (must be from current section)

    Returns:
        First section of the new page
    """
    global _state

    if not _state.sections:
        return "No page currently loaded. Use request_page first."

    current_section = _state.sections[_state.current_section_index]

    # Check if URL is in current section
    if url not in current_section.urls:
        available = "\n".join(f"  - {u}" for u in current_section.urls[:10])
        if len(current_section.urls) > 10:
            available += f"\n  ... and {len(current_section.urls) - 10} more"
        return (
            f"URL '{url}' is not available in the current section.\n\n"
            f"Available URLs (showing up to 10):\n{available}"
        )

    # Navigate to the URL
    return request_page(url)


@mcp.tool()
def read_further() -> str:
    """
    Load the next section of the current page into context.

    Call this to read more of the current article.

    Returns:
        Next section of the page with available URLs
    """
    global _state

    if not _state.sections:
        return "No page currently loaded. Use request_page first."

    if _state.current_section_index >= len(_state.sections) - 1:
        return "You've reached the end of this article. No more sections to load."

    # Move to next section
    _state.current_section_index += 1
    section = _state.sections[_state.current_section_index]

    urls_text = (
        "\n".join(f"  - {u}" for u in section.urls[:10]) if section.urls else "  (none)"
    )

    if len(section.urls) > 10:
        urls_text += f"\n  ... and {len(section.urls) - 10} more URLs"

    return (
        f"**{_state.title}**\n\n"
        f"Section {_state.current_section_index + 1}/{len(_state.sections)}: {section.heading}\n\n"
        f"{section.content}\n\n"
        f"Available URLs in this section (showing up to 10):\n{urls_text}\n\n"
        f"({len(_state.sections) - _state.current_section_index - 1} sections remaining)"
    )


@mcp.tool()
def search_rag(query: str, limit: int = 5) -> str:
    """
    Search previously visited pages in the local RAG database using keyword search.

    Args:
        query: Search query for RAG database
        limit: Number of results to return (default: 5)

    Returns:
        Previously visited pages matching the query
    """
    try:
        _, table = _get_db()

        # Get all rows and filter by keyword match
        all_pages = table.to_pandas()

        if all_pages.empty:
            return "No pages in RAG database yet. Browse some Wikipedia pages first."

        # Simple keyword search: check if query words appear in title or full_text
        query_lower = query.lower()
        query_words = query_lower.split()

        def matches_query(row):
            text = (str(row["title"]) + " " + str(row["full_text"])).lower()
            return any(word in text for word in query_words)

        # Filter and score by number of matching words
        def score_match(row):
            text = (str(row["title"]) + " " + str(row["full_text"])).lower()
            return sum(1 for word in query_words if word in text)

        matching_pages = all_pages[all_pages.apply(matches_query, axis=1)].copy()

        if matching_pages.empty:
            return f"No results found in RAG database for '{query}'"

        # Sort by score and limit
        matching_pages["score"] = matching_pages.apply(score_match, axis=1)
        matching_pages = matching_pages.sort_values("score", ascending=False).head(limit)

        formatted_results = []
        for i, (_, result) in enumerate(matching_pages.iterrows(), 1):
            preview = str(result["full_text"])[:200].replace("\n", " ")
            formatted_results.append(
                f"{i}. **{result['title']}** (score: {result['score']})\n"
                f"   URL: {result['url']}\n"
                f"   Visited: {result['fetch_timestamp']}\n"
                f"   Preview: {preview}...\n"
            )

        return f"RAG search results for '{query}':\n\n" + "\n".join(formatted_results)

    except Exception as e:
        return f"Error searching RAG database: {e}"


if __name__ == "__main__":
    # Run the server (defaults to stdio transport)
    mcp.run()
