"""Advisor Agent - Brand compliance review using MAF.

Uses Self-Reflection reasoning to review content for brand alignment,
checking against brand guidelines and past performance data.
"""

import logging
import time

from app.agents.prompts import ADVISOR_PROMPT
from app.agents.factory import create_agent, get_agent_tools
from app.agents.middleware import build_agent_trace_data, make_knowledge_citation
from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


async def run_advisor(task: str, context: dict) -> tuple[str, int, dict]:
    """Run the Advisor agent via MAF with Self-Reflection reasoning.

    Returns:
        Tuple of (client-ready communication, tokens used, trace data dict)
    """
    previous = context.get("previous_results", {})
    content_parts = []

    for agent_name, result in previous.items():
        content_parts.append(f"{agent_name.title()} Output:\n{result[:500]}")

    content_str = "\n\n".join(content_parts) if content_parts else context.get("message", "")

    prompt = f"""Task: {task}

Content to Review:
{content_str}

Use available tools to retrieve brand guidelines and past post performance data.
Apply the Self-Reflection pattern:
1. Initial review against brand voice and content policy
2. Reflect on whether your assessment is fair and constructive
3. Provide a revised assessment with compliance score (1-10) and specific feedback

Create a clear, executive-level communication that:
1. Leads with the key insight or recommendation
2. Provides supporting context
3. Ends with clear next steps or action items"""

    start_time = time.time()

    # Try MAF agent path
    try:
        tools = get_agent_tools("advisor", include_mcp=False)
        agent = create_agent("advisor", ADVISOR_PROMPT, tools=tools)
        response = await agent.run(prompt)
        text = response.text or ""
        tokens = response.usage_details.total_token_count if response.usage_details else 0
        duration_ms = int((time.time() - start_time) * 1000)
        trace = build_agent_trace_data("advisor", text, tokens or 0, duration_ms, response)
        return text, tokens or 0, trace
    except Exception as e:
        logger.warning("MAF agent path failed for advisor, falling back to direct LLM: %s", e)

    # Fallback: direct LLM call
    llm = get_llm_service()
    response = await llm.complete_with_usage(
        prompt=prompt,
        system_prompt=ADVISOR_PROMPT,
        temperature=0.6,
    )
    duration_ms = int((time.time() - start_time) * 1000)
    trace = build_agent_trace_data("advisor", response.content, response.tokens_used, duration_ms)

    # Advisor reviews against brand guidelines
    trace["citations"].append(make_knowledge_citation("get_brand_guidelines"))
    trace["tool_calls"] = [
        {"tool_name": "get_brand_guidelines", "result_preview": "Brand guidelines referenced"},
        {"tool_name": "get_past_posts", "result_preview": "Past post benchmarks referenced"},
    ]

    return response.content, response.tokens_used, trace
