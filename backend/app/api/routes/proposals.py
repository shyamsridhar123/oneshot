"""Proposal API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db, Document
from app.models.schemas import ProposalRequest, ProposalResponse, DocumentResponse

router = APIRouter()


@router.get("", response_model=list[DocumentResponse])
async def list_proposals(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all generated proposals."""
    result = await db.execute(
        select(Document)
        .where(Document.doc_type == "proposal")
        .order_by(Document.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    documents = result.scalars().all()
    
    return [
        DocumentResponse(
            id=doc.id,
            title=doc.title,
            doc_type=doc.doc_type,
            content=doc.content,
            format=doc.format,
            created_at=doc.created_at,
            metadata=doc.metadata_ or {},
        )
        for doc in documents
    ]


@router.get("/{proposal_id}", response_model=DocumentResponse)
async def get_proposal(
    proposal_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific proposal."""
    result = await db.execute(
        select(Document)
        .where(Document.id == proposal_id, Document.doc_type == "proposal")
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    return DocumentResponse(
        id=document.id,
        title=document.title,
        doc_type=document.doc_type,
        content=document.content,
        format=document.format,
        created_at=document.created_at,
        metadata=document.metadata_ or {},
    )


@router.post("/generate", response_model=DocumentResponse)
async def generate_proposal(
    data: ProposalRequest,
    db: AsyncSession = Depends(get_db),
):
    """Trigger proposal generation via agents."""
    # TODO: Implement full agent-driven proposal generation
    # For now, create a placeholder
    from app.agents.orchestrator import generate_proposal as agent_generate
    
    result = await agent_generate(
        client_name=data.client_name,
        client_industry=data.client_industry,
        engagement_type=data.engagement_type,
        scope_description=data.scope_description,
        budget_range=data.budget_range,
        timeline=data.timeline,
        additional_context=data.additional_context,
        db=db,
    )
    
    return DocumentResponse(
        id=result.id,
        title=result.title,
        doc_type=result.doc_type,
        content=result.content,
        format=result.format,
        created_at=result.created_at,
        metadata=result.metadata_ or {},
    )
