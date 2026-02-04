"""Knowledge base API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db, KnowledgeItem, Engagement
from app.models.schemas import KnowledgeSearchRequest, KnowledgeItemResponse

router = APIRouter()


@router.get("", response_model=list[KnowledgeItemResponse])
async def list_knowledge(
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List all knowledge items with optional filtering."""
    query = select(KnowledgeItem)
    
    if category:
        query = query.where(KnowledgeItem.category == category)
    
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return [
        KnowledgeItemResponse(
            id=item.id,
            title=item.title,
            content=item.content,
            category=item.category,
            industry=item.industry,
            tags=item.tags or [],
            score=None,
        )
        for item in items
    ]


@router.get("/{item_id}", response_model=KnowledgeItemResponse)
async def get_knowledge_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific knowledge item by ID."""
    result = await db.execute(
        select(KnowledgeItem).where(KnowledgeItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    
    return KnowledgeItemResponse(
        id=item.id,
        title=item.title,
        content=item.content,
        category=item.category,
        industry=item.industry,
        tags=item.tags or [],
        score=None,
    )


@router.post("/search", response_model=list[KnowledgeItemResponse])
async def search_knowledge(
    data: KnowledgeSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Semantic search over knowledge base."""
    # TODO: Implement actual semantic search via Memory agent
    # For now, do basic text search
    query = select(KnowledgeItem)
    
    if data.category:
        query = query.where(KnowledgeItem.category == data.category)
    if data.industry:
        query = query.where(KnowledgeItem.industry == data.industry)
    
    result = await db.execute(query.limit(data.limit))
    items = result.scalars().all()
    
    return [
        KnowledgeItemResponse(
            id=item.id,
            title=item.title,
            content=item.content,
            category=item.category,
            industry=item.industry,
            tags=item.tags or [],
            score=1.0,  # Placeholder
        )
        for item in items
    ]


@router.post("/similar")
async def find_similar_engagements(
    query: str,
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
):
    """Find similar past engagements."""
    # TODO: Implement semantic similarity search
    result = await db.execute(
        select(Engagement).limit(limit)
    )
    engagements = result.scalars().all()
    
    return [
        {
            "id": eng.id,
            "client_name": eng.client_name,
            "client_industry": eng.client_industry,
            "engagement_type": eng.engagement_type,
            "description": eng.description,
            "outcomes": eng.outcomes,
            "frameworks_used": eng.frameworks_used or [],
            "score": 0.95,  # Placeholder
        }
        for eng in engagements
    ]
