"""Knowledge service for semantic search and retrieval."""

import numpy as np
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import KnowledgeItem, Engagement
from app.services.llm_service import get_llm_service


class KnowledgeService:
    """Service for knowledge base operations with semantic search."""

    def __init__(self):
        self.llm = get_llm_service()

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        a_arr = np.array(a)
        b_arr = np.array(b)
        return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)))

    async def search(
        self,
        query: str,
        db: AsyncSession,
        category: Optional[str] = None,
        industry: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Semantic search over knowledge items."""
        # Generate query embedding
        query_embedding = await self.llm.embed(query)

        # Get all items (in production, use a vector DB)
        stmt = select(KnowledgeItem)
        if category:
            stmt = stmt.where(KnowledgeItem.category == category)
        if industry:
            stmt = stmt.where(KnowledgeItem.industry == industry)

        result = await db.execute(stmt)
        items = result.scalars().all()

        # Score by similarity
        scored_items = []
        for item in items:
            if item.embedding:
                score = self._cosine_similarity(query_embedding, item.embedding)
                scored_items.append({
                    "id": item.id,
                    "title": item.title,
                    "content": item.content,
                    "category": item.category,
                    "industry": item.industry,
                    "tags": item.tags or [],
                    "score": score,
                })

        # Sort by score descending
        scored_items.sort(key=lambda x: x["score"], reverse=True)
        return scored_items[:limit]

    async def find_similar_engagements(
        self,
        query: str,
        db: AsyncSession,
        limit: int = 5,
    ) -> list[dict]:
        """Find past engagements similar to the query."""
        query_embedding = await self.llm.embed(query)

        result = await db.execute(select(Engagement))
        engagements = result.scalars().all()

        scored = []
        for eng in engagements:
            if eng.embedding:
                score = self._cosine_similarity(query_embedding, eng.embedding)
                scored.append({
                    "id": eng.id,
                    "client_name": eng.client_name,
                    "client_industry": eng.client_industry,
                    "engagement_type": eng.engagement_type,
                    "description": eng.description,
                    "outcomes": eng.outcomes,
                    "frameworks_used": eng.frameworks_used or [],
                    "score": score,
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    async def add_knowledge_item(
        self,
        db: AsyncSession,
        title: str,
        content: str,
        category: str,
        industry: Optional[str] = None,
        tags: list[str] = None,
    ) -> KnowledgeItem:
        """Add a new knowledge item with embedding."""
        embedding = await self.llm.embed(f"{title}\n{content}")

        item = KnowledgeItem(
            title=title,
            content=content,
            category=category,
            industry=industry,
            tags=tags or [],
            embedding=embedding,
        )
        db.add(item)
        await db.flush()
        return item


# Singleton
_knowledge_service: KnowledgeService | None = None


def get_knowledge_service() -> KnowledgeService:
    """Get or create knowledge service singleton."""
    global _knowledge_service
    if _knowledge_service is None:
        _knowledge_service = KnowledgeService()
    return _knowledge_service
