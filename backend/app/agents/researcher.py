"""Researcher Agent - Trend discovery and competitive analysis using MAF with MCP tools.

Uses ReAct reasoning pattern (Thought → Action → Observation) to discover
trending topics, analyze competitor content, and research hashtags.
Optionally uses MCP fetch server for real-time web content retrieval.
"""

import logging

from app.agents.prompts import RESEARCHER_PROMPT
from app.agents.factory import (
    create_agent,
    get_agent_tools,
    search_web,
    search_news,
    search_trends,
    search_competitor_content,
)
from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


async def run_researcher(task: str, context: dict) -> tuple[str, int]:
    """Run the Researcher agent to gather trend and competitive intelligence.

    Creates a MAF ChatAgent with social media research tools and optional
    MCP fetch server for real-time web content grounding.

    Args:
        task: The research task description
        context: Context including message, entities, platforms

    Returns:
        Tuple of (research findings, tokens used)
    """
    entities = context.get("entities", [])
    message = context.get("message", task)
    platforms = context.get("platforms", ["linkedin", "twitter", "instagram"])
    platforms_str = ", ".join(platforms)

    prompt = f"""Task: {task}

Target Platforms: {platforms_str}
Key Entities: {', '.join(entities) if entities else 'None specified'}
Original Request: {message}

Use the ReAct pattern to research this topic:
1. Think about what information is needed
2. Use available tools to search for trends, competitor content, and hashtags
3. Observe the results and determine if more research is needed
4. Synthesize findings into a comprehensive research briefing

If web fetch tools are available, use them to retrieve real-time information."""

    # Try MAF agent path (with tools + MCP)
    try:
        tools = get_agent_tools("researcher", include_mcp=True)
        agent = create_agent("researcher", RESEARCHER_PROMPT, tools=tools)
        response = await agent.run(prompt)
        text = response.text or ""
        tokens = response.usage_details.total_token_count if response.usage_details else 0
        return text, tokens or 0
    except Exception as e:
        logger.warning("MAF agent path failed for researcher, falling back to direct LLM: %s", e)

    # Fallback: direct tool calls + LLM synthesis
    research_results = []

    web_results = search_web(message)
    research_results.append(f"## Web Search\n{web_results}")

    news_results = search_news(message)
    research_results.append(f"## Recent News\n{news_results}")

    trend_results = search_trends(message, platform="all")
    research_results.append(f"## Trending Topics\n{trend_results}")

    for entity in entities[:2]:
        competitor_results = search_competitor_content(entity)
        research_results.append(f"## Competitor: {entity}\n{competitor_results}")

    all_research = "\n\n".join(research_results)

    fallback_prompt = f"""Based on the following research results, provide a comprehensive briefing.

Task: {task}
Target Platforms: {platforms_str}

Research Data:
{all_research}

Synthesize these findings into a clear, well-organized research briefing."""

    llm = get_llm_service()
    response = await llm.complete_with_usage(
        prompt=fallback_prompt,
        system_prompt=RESEARCHER_PROMPT,
        temperature=0.5,
    )
    return response.content, response.tokens_used
