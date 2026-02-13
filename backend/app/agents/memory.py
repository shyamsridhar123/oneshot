"""Memory Agent - Knowledge retrieval and RAG using MAF.

Uses Retrieval-Augmented Grounding to fetch brand guidelines, past posts,
and knowledge base items, then synthesizes them for downstream agents.
"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.prompts import MEMORY_PROMPT
from app.agents.factory import create_agent, get_agent_tools
from app.services.llm_service import get_llm_service
from app.services.knowledge_service import get_knowledge_service
from app.models.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def run_memory(task: str, context: dict, db: Optional[AsyncSession] = None) -> tuple[str, int]:
    """Run the Memory agent via MAF with retrieval-augmented grounding.

    Creates a MAF ChatAgent with brand data tools (guidelines, past posts,
    content calendar, knowledge base) and supplements with semantic search
    over the knowledge DB.

    Args:
        task: The retrieval task
        context: Context including query details
        db: Optional database session (uses AsyncSessionLocal if not provided)

    Returns:
        Tuple of (retrieved knowledge and context, tokens used)
    """
    knowledge_service = get_knowledge_service()

    message = context.get("message", task)
    entities = context.get("entities", [])

    # Build search query
    search_query = f"{task} {message} {' '.join(entities)}"

    # Perform semantic search - use provided session or create one
    async def _do_search(session: AsyncSession):
        knowledge_results = await knowledge_service.search(
            query=search_query,
            db=session,
            limit=5,
        )
        engagement_results = await knowledge_service.find_similar_engagements(
            query=search_query,
            db=session,
            limit=3,
        )
        return knowledge_results, engagement_results

    if db is not None:
        knowledge_results, engagement_results = await _do_search(db)
    else:
        async with AsyncSessionLocal() as session:
            knowledge_results, engagement_results = await _do_search(session)

    # Format results
    kb_text = _format_knowledge_results(knowledge_results)
    eng_text = _format_engagement_results(engagement_results)

    prompt = f"""Task: {task}

## Relevant Frameworks & Expertise:
{kb_text if kb_text else "No matching frameworks found."}

## Similar Past Engagements:
{eng_text if eng_text else "No similar engagements found."}

Original Query: {message}

Use available tools to retrieve brand guidelines, past post performance, and content calendar.
Analyze the retrieved information and provide:
1. The most relevant past engagements and their outcomes
2. Applicable frameworks and methodologies
3. Key insights that can inform the current request"""

    # Try MAF agent path
    try:
        tools = get_agent_tools("memory", include_mcp=False)
        agent = create_agent("memory", MEMORY_PROMPT, tools=tools)
        response = await agent.run(prompt)
        text = response.text or ""
        tokens = response.usage_details.total_token_count if response.usage_details else 0
        return text, tokens or 0
    except Exception as e:
        logger.warning("MAF agent path failed for memory, falling back to direct LLM: %s", e)

    # Fallback: direct LLM call
    llm = get_llm_service()
    response = await llm.complete_with_usage(
        prompt=prompt,
        system_prompt=MEMORY_PROMPT,
        temperature=0.4,
    )

    return response.content, response.tokens_used


def _format_knowledge_results(results: list[dict]) -> str:
    """Format knowledge search results."""
    if not results:
        return ""
    
    lines = []
    for r in results:
        score = r.get("score", 0)
        if score > 0.5:  # Only include relevant results
            lines.append(f"### {r['title']} (relevance: {score:.0%})")
            lines.append(f"Category: {r['category']}")
            if r.get("industry"):
                lines.append(f"Industry: {r['industry']}")
            lines.append(f"\n{r['content'][:500]}..." if len(r['content']) > 500 else f"\n{r['content']}")
            lines.append("")
    
    return "\n".join(lines)


def _format_engagement_results(results: list[dict]) -> str:
    """Format engagement search results."""
    if not results:
        return ""
    
    lines = []
    for r in results:
        score = r.get("score", 0)
        if score > 0.5:  # Only include relevant results
            lines.append(f"### {r['client_name']} - {r['engagement_type']} (relevance: {score:.0%})")
            lines.append(f"Industry: {r['client_industry']}")
            lines.append(f"Description: {r['description'][:300]}..." if len(r['description']) > 300 else f"Description: {r['description']}")
            lines.append(f"Outcomes: {r['outcomes']}")
            if r.get("frameworks_used"):
                lines.append(f"Frameworks Used: {', '.join(r['frameworks_used'])}")
            lines.append("")
    
    return "\n".join(lines)
