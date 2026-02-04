"""Analyst Agent - Data analysis and financial modeling."""

from app.agents.prompts import ANALYST_PROMPT
from app.services.llm_service import get_llm_service


async def run_analyst(task: str, context: dict) -> tuple[str, int]:
    """
    Run the Analyst agent for data analysis and modeling.
    
    Args:
        task: The analysis task description
        context: Context including data and previous results
    
    Returns:
        Tuple of (analysis results, tokens used)
    """
    llm = get_llm_service()
    
    # Get any previous research or data
    previous = context.get("previous_results", {})
    data_context = ""
    
    if "researcher" in previous:
        data_context += f"\nResearch Data:\n{previous['researcher'][:1000]}"
    if "memory" in previous:
        data_context += f"\nHistorical Data:\n{previous['memory'][:1000]}"
    
    prompt = f"""Task: {task}

{data_context}

Original Request: {context.get('message', '')}

Provide quantitative analysis, metrics, and data-driven insights."""

    response = await llm.complete_with_usage(
        prompt=prompt,
        system_prompt=ANALYST_PROMPT,
        temperature=0.3,  # Lower temperature for analytical precision
    )
    
    return response.content, response.tokens_used
