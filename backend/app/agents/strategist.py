"""Strategist Agent - Engagement scoping and proposal strategy."""

from app.agents.prompts import STRATEGIST_PROMPT
from app.services.llm_service import get_llm_service


async def run_strategist(task: str, context: dict) -> tuple[str, int]:
    """
    Run the Strategist agent for engagement scoping and proposal strategy.
    
    Args:
        task: The task description
        context: Context including message, entities, previous results
    
    Returns:
        Tuple of (Strategist's response, tokens used)
    """
    llm = get_llm_service()
    
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
    
    context_str = "\n".join(context_parts) if context_parts else ""
    
    prompt = f"""Task: {task}

{context_str}

Original Request: {context.get('message', '')}

Provide strategic guidance or generate the requested proposal/scoping document."""

    response = await llm.complete_with_usage(
        prompt=prompt,
        system_prompt=STRATEGIST_PROMPT,
        temperature=0.7,
    )
    
    return response.content, response.tokens_used
