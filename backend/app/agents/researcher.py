"""Researcher Agent - Trend discovery and competitive analysis using MAF with MCP tools.

Uses ReAct reasoning pattern (Thought -> Action -> Observation) to discover
trending topics, analyze competitor content, and research hashtags.
Optionally uses MCP fetch server for real-time web content retrieval.
"""

import asyncio
import logging
import time

from app.agents.prompts import RESEARCHER_PROMPT
from app.agents.factory import (
    create_agent,
    get_agent_tools,
    search_web,
    search_news,
    search_trends,
    search_competitor_content,
)
from app.agents.middleware import build_agent_trace_data, extract_citations_from_text
from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


def _ensure_mcp_cleanup_filter():
    """Install filter for harmless MCP stdio teardown errors (idempotent)."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    if getattr(loop, "_mcp_filter_installed", False):
        return
    _prev = loop.get_exception_handler()

    def _handler(loop, ctx):
        ag = ctx.get("asyncgen")
        if ag and "stdio_client" in getattr(ag, "__qualname__", ""):
            return
        if _prev:
            _prev(loop, ctx)
        else:
            loop.default_exception_handler(ctx)

    loop.set_exception_handler(_handler)
    loop._mcp_filter_installed = True


async def run_researcher(task: str, context: dict) -> tuple[str, int, dict]:
    """Run the Researcher agent to gather trend and competitive intelligence.

    Returns:
        Tuple of (research findings, tokens used, trace data dict)
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

    start_time = time.time()

    # Try MAF agent path (with tools + MCP)
    try:
        _ensure_mcp_cleanup_filter()
        tools = get_agent_tools("researcher", include_mcp=True)
        agent = create_agent("researcher", RESEARCHER_PROMPT, tools=tools)
        response = await agent.run(prompt)
        text = response.text or ""
        tokens = response.usage_details.total_token_count if response.usage_details else 0
        duration_ms = int((time.time() - start_time) * 1000)
        trace = build_agent_trace_data("researcher", text, tokens or 0, duration_ms, response)
        return text, tokens or 0, trace
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
    duration_ms = int((time.time() - start_time) * 1000)

    # Build trace with fallback tool calls
    fallback_tool_calls = [
        {"tool_name": "search_web", "result_preview": web_results[:300]},
        {"tool_name": "search_news", "result_preview": news_results[:300]},
        {"tool_name": "search_trends", "result_preview": trend_results[:300]},
    ]
    citations = extract_citations_from_text(all_research)
    trace = {
        "result_preview": response.content[:500],
        "citations": citations,
        "tool_calls": fallback_tool_calls,
        "duration_ms": duration_ms,
        "tokens_used": response.tokens_used,
        "agent_name": "researcher",
    }

    return response.content, response.tokens_used, trace
