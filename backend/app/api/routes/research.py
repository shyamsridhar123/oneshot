"""Research API routes - wired to Researcher agent with MCP tools."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.schemas import ResearchRequest, BriefingRequest
from app.agents.researcher import run_researcher
from app.agents.memory import run_memory
from app.agents.scribe import run_scribe
from app.services.llm_service import get_llm_service
from app.agents.prompts import AGENT_PROMPTS

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query")
async def research_query(
    data: ResearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Execute a research query via the Researcher agent with MCP tools."""
    context = {
        "message": data.query,
        "entities": [],
        "platforms": ["linkedin", "twitter", "instagram"],
        "sources": data.sources,
    }

    try:
        findings, tokens_used = await run_researcher(
            task=f"Research: {data.query}",
            context=context,
        )
        return {
            "query": data.query,
            "research_type": data.research_type,
            "status": "completed",
            "message": findings,
            "tokens_used": tokens_used,
        }
    except Exception as e:
        logger.error("Research query failed: %s", e)
        return {
            "query": data.query,
            "research_type": data.research_type,
            "status": "error",
            "message": f"Research failed: {str(e)}",
        }


@router.post("/briefing")
async def generate_briefing(
    data: BriefingRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate a client briefing via Researcher + Memory + Scribe agents."""
    context = {
        "message": f"Generate a briefing for {data.company_name}",
        "entities": [data.company_name],
        "platforms": ["linkedin", "twitter", "instagram"],
    }
    if data.industry:
        context["message"] += f" in the {data.industry} industry"

    try:
        research_result, r_tokens = await run_researcher(
            task=f"Research {data.company_name} for a client briefing",
            context=context,
        )

        memory_result, m_tokens = await run_memory(
            task=f"Retrieve brand context relevant to {data.company_name}",
            context=context,
        )

        scribe_context = {
            **context,
            "previous_results": {
                "researcher": research_result,
                "memory": memory_result,
            },
        }
        briefing_content, s_tokens = await run_scribe(
            task=f"Write a professional briefing about {data.company_name}",
            context=scribe_context,
        )

        return {
            "company_name": data.company_name,
            "status": "completed",
            "message": briefing_content,
            "tokens_used": r_tokens + m_tokens + s_tokens,
        }
    except Exception as e:
        logger.error("Briefing generation failed: %s", e)
        return {
            "company_name": data.company_name,
            "status": "error",
            "message": f"Briefing generation failed: {str(e)}",
        }
