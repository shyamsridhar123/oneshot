"""Analyst Agent - Data analysis and engagement benchmarking using MAF.

Uses Data-Driven Benchmarking reasoning to provide engagement predictions,
optimal posting schedules, and performance comparisons.
"""

import logging
import time

from app.agents.prompts import ANALYST_PROMPT
from app.agents.factory import create_agent, get_agent_tools
from app.agents.middleware import build_agent_trace_data
from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


async def run_analyst(task: str, context: dict) -> tuple[str, int, dict]:
    """Run the Analyst agent via MAF with data-driven benchmarking tools.

    Returns:
        Tuple of (analysis results, tokens used, trace data dict)
    """
    previous = context.get("previous_results", {})
    data_context = ""

    if "researcher" in previous:
        data_context += f"\nResearch Data:\n{previous['researcher'][:1000]}"
    if "memory" in previous:
        data_context += f"\nHistorical Data:\n{previous['memory'][:1000]}"

    platforms = context.get("platforms", ["linkedin", "twitter", "instagram"])
    platforms_str = ", ".join(platforms)

    prompt = f"""Task: {task}

Target Platforms: {platforms_str}
{data_context}

Original Request: {context.get('message', '')}

Use available tools to calculate engagement metrics and recommend posting schedules.
Provide quantitative analysis, metrics, and data-driven insights."""

    start_time = time.time()

    # Try MAF agent path
    try:
        tools = get_agent_tools("analyst", include_mcp=False)
        agent = create_agent("analyst", ANALYST_PROMPT, tools=tools)
        response = await agent.run(prompt)
        text = response.text or ""
        tokens = response.usage_details.total_token_count if response.usage_details else 0
        duration_ms = int((time.time() - start_time) * 1000)
        trace = build_agent_trace_data("analyst", text, tokens or 0, duration_ms, response)
        return text, tokens or 0, trace
    except Exception as e:
        logger.warning("MAF agent path failed for analyst, falling back to direct LLM: %s", e)

    # Fallback: direct LLM call
    llm = get_llm_service()
    response = await llm.complete_with_usage(
        prompt=prompt,
        system_prompt=ANALYST_PROMPT,
        temperature=0.3,
    )
    duration_ms = int((time.time() - start_time) * 1000)
    trace = build_agent_trace_data("analyst", response.content, response.tokens_used, duration_ms)

    return response.content, response.tokens_used, trace
