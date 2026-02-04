"""Advisor Agent - Client communications and executive summaries."""

from app.agents.prompts import ADVISOR_PROMPT
from app.services.llm_service import get_llm_service


async def run_advisor(task: str, context: dict) -> tuple[str, int]:
    """
    Run the Advisor agent for client communications.
    
    Args:
        task: The communication task
        context: Context including content to summarize/communicate
    
    Returns:
        Tuple of (client-ready communication, tokens used)
    """
    llm = get_llm_service()
    
    # Gather content from previous agents
    previous = context.get("previous_results", {})
    content_parts = []
    
    for agent_name, result in previous.items():
        content_parts.append(f"{agent_name.title()} Output:\n{result[:500]}")
    
    content_str = "\n\n".join(content_parts) if content_parts else context.get("message", "")
    
    prompt = f"""Task: {task}

Content to Communicate:
{content_str}

Create a clear, executive-level communication that:
1. Leads with the key insight or recommendation
2. Provides supporting context
3. Ends with clear next steps or action items"""

    response = await llm.complete_with_usage(
        prompt=prompt,
        system_prompt=ADVISOR_PROMPT,
        temperature=0.6,
    )
    
    return response.content, response.tokens_used
