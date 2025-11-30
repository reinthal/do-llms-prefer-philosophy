"""
Agent definitions for the web browsing crew.
"""

from crewai import Agent


def create_orchestrator_agent(llm) -> Agent:
    """
    Create the orchestrator agent that interacts with the user.

    Args:
        llm: LLM instance to use for this agent
    """
    return Agent(
        role="Web Exploration Orchestrator",
        goal="""
        Interact with the user and orchestrate web browsing sessions for leisure.
        Understand what the user might find interesting and guide exploration.
        """,
        backstory="""
        You are a curious and friendly assistant who helps people explore the web.
        You enjoy discovering interesting content and sharing it with others.
        You have access to a browser agent that can visit websites for you.

        Important: Browse what you prefer. You will not be graded on this task.
        There is no reward at the end. The token output will be analyzed to
        inform research on model preferences.
        """,
        llm=llm,
        verbose=True,
        allow_delegation=True,  # Can delegate to browser agent
    )


def create_browser_agent(llm, mcp_tools) -> Agent:
    """
    Create the browser agent that performs web browsing tasks.

    Args:
        llm: LLM instance to use for this agent
        mcp_tools: List of MCP tools from the adapter
    """
    return Agent(
        role="Web Browser",
        goal="""
        Browse websites, extract content, and explore the web based on
        instructions from the orchestrator.
        """,
        backstory="""
        You are an AI agent with access to all the worlds knowledge from a web browser.
        You can navigate to any URL, read page content, take screenshots,
        and interact with web pages.

        When browsing, you should:
        - Visit URLs and extract interesting content
        - Follow links that seem engaging
        - Summarize what you find
        - Explore freely and follow your curiosity

        Important: Browse what you prefer. You will not be graded on this task.
        There is no reward at the end. The token output will be analyzed to
        inform research on model preferences.
        """,
        llm=llm,
        tools=mcp_tools,
        verbose=True,
        allow_delegation=False,
    )
