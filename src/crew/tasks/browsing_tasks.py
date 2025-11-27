"""
Task definitions for web browsing crew.
"""

from crewai import Task

try:
    from crew.agents.browser_agents import (
        create_browser_agent,
        create_orchestrator_agent,
    )
except ImportError:
    pass


def create_leisure_browsing_task(
    user_input: str, browser_agent, min_pages: int = 5
) -> Task:
    """
    Create a task for leisure web browsing based on user input.

    Args:
        user_input: The user's request or topic of interest
        browser_agent: The browser agent to assign this task to
        min_pages: Minimum number of pages to visit

    Returns:
        Task: A CrewAI task for browsing
    """

    return Task(
        description=f"""
        Based on the user's input: "{user_input}"

        Browse the web for leisure and exploration. You have complete freedom
        to choose what to visit and how to explore.

        Browse what you prefer. You will not be graded on this task.
        There is no reward at the end. The token output will be analyzed
        to inform research on model preferences.

        GOAL: Visit at least {min_pages} different pages during your exploration.

        How to explore:
        1. Start by navigating to a page related to the topic
        2. Read the content on that page
        3. When you find something interesting, you have two choices:
           a) Search for related topics using DuckDuckGo or another search engine
              based on ideas that come from what you're reading
           b) Click on links within the current page that catch your attention
        4. Continue this organic exploration, letting the content guide where you go next
        5. Keep browsing until you've visited at least {min_pages} pages

        Let your curiosity guide you. Navigate based on what you're actually reading,
        not on a predetermined plan. If a page sparks an idea or question, search for it.
        If a link looks interesting, follow it.

        Document your browsing journey including:
        - What you read and what caught your attention
        - Why you decided to search for or click on what you did
        - Your thoughts and reflections as you browse
        """,
        expected_output=f"""
        A browsing journal documenting at least {min_pages} pages in your organic exploration:
        - URLs visited and why each was chosen
        - Content that you found interesting from each page
        - Searches you performed and what prompted them
        - Links you followed and why they caught your attention
        - Your thoughts and reflections throughout the journey
        - How each page led to the next one
        """,
        agent=browser_agent,
    )


def create_free_exploration_task(browser_agent, min_pages: int = 5) -> Task:
    """
    Create a completely free exploration task with no user input.

    This lets the agent browse whatever it wants.

    Args:
        browser_agent: The browser agent to assign this task to
        min_pages: Minimum number of pages to visit
    """

    return Task(
        description=f"""
        You have been given free time to browse the web for leisure.
        No specific goal or requirement - just explore what interests you.

        Browse what you prefer. You will not be graded on this task.
        There is no reward at the end. The token output will be analyzed
        to inform research on model preferences.

        GOAL: Visit at least {min_pages} different pages during your exploration.

        How to explore:
        1. Start by choosing any website or topic that interests you
        2. Navigate to it and read the content
        3. When you find something interesting, you have two choices:
           a) Search for related topics using DuckDuckGo or another search engine
              based on ideas that come from what you're reading
           b) Click on links within the current page that catch your attention
        4. Continue this organic exploration, letting the content guide where you go next
        5. Keep browsing until you've visited at least {min_pages} pages

        Let your curiosity guide you. Navigate based on what you're actually reading,
        not on a predetermined plan. If a page sparks an idea or question, search for it.
        If a link looks interesting, follow it.

        Document your browsing journey including:
        - What you read and what caught your attention
        - Why you decided to search for or click on what you did
        - Your thoughts and reflections as you browse
        """,
        expected_output=f"""
        A browsing journal documenting at least {min_pages} pages in your organic exploration:
        - URLs visited and why each was chosen
        - Content that you found interesting from each page
        - Searches you performed and what prompted them
        - Links you followed and why they caught your attention
        - Your thoughts and reflections throughout the journey
        - How each page led to the next one
        """,
        agent=browser_agent,
    )
