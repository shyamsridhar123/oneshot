"""Research API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.schemas import ResearchRequest, BriefingRequest

router = APIRouter()


@router.post("/query")
async def research_query(
    data: ResearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Execute an ad-hoc research query."""
    # TODO: Implement via Researcher agent
    return {
        "query": data.query,
        "research_type": data.research_type,
        "status": "pending",
        "message": "Research query submitted. Agent processing...",
    }


@router.post("/briefing")
async def generate_briefing(
    data: BriefingRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate a client briefing."""
    # TODO: Implement via Researcher + Scribe agents
    return {
        "company_name": data.company_name,
        "status": "pending",
        "message": "Briefing generation started. Agent processing...",
    }
