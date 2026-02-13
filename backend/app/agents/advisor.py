"""Advisor Agent - Brand compliance review using MAF.

Uses Self-Reflection reasoning to review content for brand alignment,
checking against brand guidelines and past performance data.
"""

import logging

from app.agents.prompts import ADVISOR_PROMPT
from app.agents.factory import create_agent, get_agent_tools
from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


async def run_advisor(task: str, context: dict) -> tuple[str, int]:
    """Run the Advisor agent via MAF with Self-Reflection reasoning.

    Creates a MAF ChatAgent with memory tools (brand guidelines, past posts)
    so the advisor can ground compliance reviews in actual brand data.

    Args:
        task: The communication task
        context: Context including content to summarize/communicate

    Returns:
        Tuple of (client-ready communication, tokens used)
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

    # Try MAF agent path
    try:
        tools = get_agent_tools("advisor", include_mcp=False)
        agent = create_agent("advisor", ADVISOR_PROMPT, tools=tools)
        response = await agent.run(prompt)
        text = response.text or ""
        tokens = response.usage_details.total_token_count if response.usage_details else 0
        return text, tokens or 0
    except Exception as e:
        logger.warning("MAF agent path failed for advisor, falling back to direct LLM: %s", e)

    # Fallback: direct LLM call
    llm = get_llm_service()
    response = await llm.complete_with_usage(
        prompt=prompt,
        system_prompt=ADVISOR_PROMPT,
        temperature=0.6,
    )

    return response.content, response.tokens_used
