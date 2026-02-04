"""Scribe Agent - Document generation and formatting."""

from app.agents.prompts import SCRIBE_PROMPT
from app.services.llm_service import get_llm_service


async def run_scribe(task: str, context: dict) -> tuple[str, int]:
    """
    Run the Scribe agent for document generation.
    
    Args:
        task: The document generation task
        context: Context including content from other agents
    
    Returns:
        Tuple of (generated document content, tokens used)
    """
    llm = get_llm_service()
    
    # Gather content from previous agents
    previous = context.get("previous_results", {})
    content_parts = []
    
    if "strategist" in previous:
        content_parts.append(f"Strategy Content:\n{previous['strategist']}")
    if "researcher" in previous:
        content_parts.append(f"Research Content:\n{previous['researcher']}")
    if "analyst" in previous:
        content_parts.append(f"Analysis Content:\n{previous['analyst']}")
    
    content_str = "\n\n".join(content_parts) if content_parts else context.get("message", "")
    
    prompt = f"""Task: {task}

Source Content:
{content_str}

Generate a polished, professional document in markdown format.
Include proper headers, formatting, and structure appropriate for the document type."""

    response = await llm.complete_with_usage(
        prompt=prompt,
        system_prompt=SCRIBE_PROMPT,
        temperature=0.6,
    )
    
    return response.content, response.tokens_used
