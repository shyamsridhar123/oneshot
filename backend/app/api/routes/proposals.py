"""Content API routes — social media content generation and retrieval."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db, Document
from app.models.schemas import ContentRequest, ProposalRequest, ProposalResponse, DocumentResponse

router = APIRouter()


@router.get("", response_model=list[DocumentResponse])
async def list_content(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all generated social media content."""
    result = await db.execute(
        select(Document)
        .where(Document.doc_type.in_(["social_post", "proposal"]))
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


@router.get("/{content_id}", response_model=DocumentResponse)
async def get_content(
    content_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific content item."""
    result = await db.execute(
        select(Document)
        .where(Document.id == content_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Content not found")

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
async def generate_content(
    data: ContentRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate social media content via agents."""
    from app.agents.orchestrator import generate_social_content

    result = await generate_social_content(
        topic=data.topic,
        platforms=data.platforms,
        content_type=data.content_type,
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
