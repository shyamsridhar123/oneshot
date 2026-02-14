"""Strategist Agent - Content strategy and platform planning using MAF.

Uses Chain-of-Thought (CoT) reasoning to develop audience-targeted
content strategies, posting schedules, and platform-specific plans.
"""

import logging
import time

from app.agents.prompts import STRATEGIST_PROMPT
from app.agents.factory import create_agent, get_agent_tools
from app.agents.middleware import build_agent_trace_data
from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


async def run_strategist(task: str, context: dict) -> tuple[str, int, dict]:
    """Run the Strategist agent via MAF with Chain-of-Thought reasoning.

    Returns:
        Tuple of (Strategist's response, tokens used, trace data dict)
    """
    # Build prompt with context
    context_parts = []

    if "client_name" in context:
        context_parts.append(f"Client: {context['client_name']}")
    if "client_industry" in context:
        context_parts.append(f"Industry: {context['client_industry']}")
    if "engagement_type" in context:
        context_parts.append(f"Engagement Type: {context['engagement_type']}")
    if "research" in context:
        context_parts.append(f"\nResearch:\n{context['research']}")
    if "similar_engagements" in context:
        context_parts.append(f"\nSimilar Past Work:\n{context['similar_engagements']}")
    if "budget_range" in context and context["budget_range"]:
        context_parts.append(f"Budget Range: {context['budget_range']}")
    if "timeline" in context and context["timeline"]:
        context_parts.append(f"Timeline: {context['timeline']}")

    previous = context.get("previous_results", {})
    if "researcher" in previous:
        context_parts.append(f"\nResearch Findings:\n{previous['researcher'][:1000]}")
    if "memory" in previous:
        context_parts.append(f"\nBrand Context:\n{previous['memory'][:1000]}")

    context_str = "\n".join(context_parts) if context_parts else ""
    platforms = context.get("platforms", ["linkedin", "twitter", "instagram"])
    platforms_str = ", ".join(platforms)

    prompt = f"""Task: {task}

Target Platforms: {platforms_str}
{context_str}

Original Request: {context.get('message', '')}

Use Chain-of-Thought reasoning to develop a content strategy.
Use available tools to check engagement metrics and optimal posting schedules.
Provide strategic guidance or generate the requested proposal/scoping document."""

    start_time = time.time()

    # Try MAF agent path
    try:
        tools = get_agent_tools("strategist", include_mcp=False)
        agent = create_agent("strategist", STRATEGIST_PROMPT, tools=tools)
        response = await agent.run(prompt)
        text = response.text or ""
        tokens = response.usage_details.total_token_count if response.usage_details else 0
        duration_ms = int((time.time() - start_time) * 1000)
        trace = build_agent_trace_data("strategist", text, tokens or 0, duration_ms, response)
        return text, tokens or 0, trace
    except Exception as e:
        logger.warning("MAF agent path failed for strategist, falling back to direct LLM: %s", e)

    # Fallback: direct LLM call
    llm = get_llm_service()
    response = await llm.complete_with_usage(
        prompt=prompt,
        system_prompt=STRATEGIST_PROMPT,
        temperature=0.7,
    )
    duration_ms = int((time.time() - start_time) * 1000)
    trace = build_agent_trace_data("strategist", response.content, response.tokens_used, duration_ms)

    return response.content, response.tokens_used, trace
