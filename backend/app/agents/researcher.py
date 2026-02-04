"""Researcher Agent - Web search, news, and company intelligence."""

from app.agents.prompts import RESEARCHER_PROMPT
from app.agents.factory import search_web, search_news, get_company_info
from app.services.llm_service import get_llm_service


async def run_researcher(task: str, context: dict) -> tuple[str, int]:
    """
    Run the Researcher agent to gather information.
    
    Args:
        task: The research task description
        context: Context including message, entities
    
    Returns:
        Tuple of (research findings, tokens used)
    """
    llm = get_llm_service()
    
    # Extract entities to research
    entities = context.get("entities", [])
    message = context.get("message", task)
    
    # Gather information from tools
    research_results = []
    
    # Search web for general info
    web_results = search_web(message)
    research_results.append(f"## Web Search\n{web_results}")
    
    # Search news for recent developments
    news_results = search_news(message)
    research_results.append(f"## Recent News\n{news_results}")
    
    # Get company info if entities mention companies
    for entity in entities:
        if any(word in entity.lower() for word in ["inc", "corp", "company", "llc", "ltd"]) or len(entities) <= 2:
            company_info = get_company_info(entity)
            research_results.append(f"## Company: {entity}\n{company_info}")
            break  # Just get first company for now
    
    # Synthesize research
    all_research = "\n\n".join(research_results)
    
    prompt = f"""Based on the following research results, provide a comprehensive briefing.

Task: {task}

Research Data:
{all_research}

Synthesize these findings into a clear, well-organized research briefing."""

    response = await llm.complete_with_usage(
        prompt=prompt,
        system_prompt=RESEARCHER_PROMPT,
        temperature=0.5,
    )
    
    return response.content, response.tokens_used
