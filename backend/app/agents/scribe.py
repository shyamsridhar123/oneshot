"""Scribe Agent - Platform-specific content generation using MAF with MCP tools.

Uses Microsoft Agent Framework to generate social media content and
optionally saves drafts to the filesystem via MCP server integration.
"""

import asyncio
import logging
import time

from app.agents.prompts import SCRIBE_PROMPT
from app.agents.factory import create_agent, get_agent_tools
from app.agents.middleware import build_agent_trace_data
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


async def run_scribe(task: str, context: dict) -> tuple[str, int, dict]:
    """Run the Scribe agent for platform-specific content generation.

    Returns:
        Tuple of (generated content, tokens used, trace data dict)
    """
    # Gather context from previous agents (Wave 1 outputs)
    previous = context.get("previous_results", {})
    platforms = context.get("platforms", ["linkedin", "twitter", "instagram"])
    content_parts = []

    if "strategist" in previous:
        content_parts.append(f"## Content Strategy\n{previous['strategist']}")
    if "researcher" in previous:
        content_parts.append(f"## Research & Trends\n{previous['researcher']}")
    if "analyst" in previous:
        content_parts.append(f"## Engagement Data\n{previous['analyst']}")
    if "memory" in previous:
        content_parts.append(f"## Brand Context\n{previous['memory']}")

    source_content = "\n\n".join(content_parts) if content_parts else context.get("message", "")
    platforms_str = ", ".join(platforms)

    prompt = f"""Task: {task}

Target Platforms: {platforms_str}

Source Content from Research & Strategy:
{source_content}

Generate platform-specific social media content for each target platform.
Follow the template-guided pattern: hook -> body -> CTA -> hashtags.

After generating content, save each platform's post as a draft file using the
filesystem tool (if available). Use filenames like 'linkedin_draft.md',
'twitter_draft.md', 'instagram_draft.md'."""

    start_time = time.time()

    # Try MAF agent path (with MCP tools)
    try:
        _ensure_mcp_cleanup_filter()
        tools = get_agent_tools("scribe", include_mcp=True)
        agent = create_agent("scribe", SCRIBE_PROMPT, tools=tools)
        response = await agent.run(prompt)
        text = response.text or ""
        tokens = response.usage_details.total_token_count if response.usage_details else 0
        duration_ms = int((time.time() - start_time) * 1000)
        trace = build_agent_trace_data("scribe", text, tokens or 0, duration_ms, response)
        return text, tokens or 0, trace
    except Exception as e:
        logger.warning("MAF agent path failed for scribe, falling back to direct LLM: %s", e)

    # Fallback: direct LLM call (no MCP, no tools)
    llm = get_llm_service()
    response = await llm.complete_with_usage(
        prompt=prompt,
        system_prompt=SCRIBE_PROMPT,
        temperature=0.6,
    )
    duration_ms = int((time.time() - start_time) * 1000)
    trace = build_agent_trace_data("scribe", response.content, response.tokens_used, duration_ms)
    return response.content, response.tokens_used, trace
