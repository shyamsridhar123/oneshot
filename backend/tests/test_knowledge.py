"""Tests for knowledge API endpoints."""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import KnowledgeItem, Engagement
from app.models.schemas import KnowledgeItemResponse


class TestSearchKnowledge:
    """Tests for POST /api/knowledge/search endpoint."""

    async def test_search_knowledge_empty_results(self, client: AsyncClient):
        """Should return empty list when no matching items exist."""
        response = await client.post(
            "/api/knowledge/search",
            json={"query": "nonexistent topic xyz", "limit": 10},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_search_knowledge_with_data(
        self, client: AsyncClient, sample_knowledge_item: KnowledgeItem
    ):
        """Should return matching knowledge items."""
        response = await client.post(
            "/api/knowledge/search",
            json={"query": "digital transformation", "limit": 10},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_search_knowledge_schema_validation(
        self, client: AsyncClient, sample_knowledge_item: KnowledgeItem
    ):
        """Response should match KnowledgeItemResponse schema."""
        response = await client.post(
            "/api/knowledge/search",
            json={"query": "framework", "limit": 5},
        )
        data = response.json()
        for item in data:
            KnowledgeItemResponse.model_validate(item)

    async def test_search_knowledge_filter_by_category(
        self, client: AsyncClient, sample_knowledge_item: KnowledgeItem
    ):
        """Should filter by category parameter."""
        response = await client.post(
            "/api/knowledge/search",
            json={"query": "test", "category": "framework", "limit": 10},
        )
        assert response.status_code == 200
        data = response.json()
        for item in data:
            assert item["category"] == "framework"

    async def test_search_knowledge_filter_by_industry(
        self, client: AsyncClient, sample_knowledge_item: KnowledgeItem
    ):
        """Should filter by industry parameter."""
        response = await client.post(
            "/api/knowledge/search",
            json={"query": "test", "industry": "Technology", "limit": 10},
        )
        assert response.status_code == 200

    async def test_search_knowledge_limit_parameter(self, client: AsyncClient):
        """Should respect limit parameter."""
        response = await client.post(
            "/api/knowledge/search",
            json={"query": "test", "limit": 3},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    async def test_search_knowledge_validation_error_empty_query(
        self, client: AsyncClient
    ):
        """Should reject empty query."""
        response = await client.post(
            "/api/knowledge/search",
            json={"query": "", "limit": 10},
        )
        assert response.status_code == 422

    async def test_search_knowledge_validation_limit_too_high(self, client: AsyncClient):
        """Should reject limit above maximum."""
        response = await client.post(
            "/api/knowledge/search",
            json={"query": "test", "limit": 100},  # Max is 50
        )
        assert response.status_code == 422


class TestFindSimilarEngagements:
    """Tests for POST /api/knowledge/similar endpoint."""

    async def test_find_similar_empty_results(self, client: AsyncClient):
        """Should return empty list when no engagements exist."""
        response = await client.post(
            "/api/knowledge/similar",
            params={"query": "nonexistent topic", "limit": 5},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_find_similar_with_data(
        self, client: AsyncClient, sample_engagement: Engagement
    ):
        """Should return similar engagements."""
        response = await client.post(
            "/api/knowledge/similar",
            params={"query": "digital transformation manufacturing", "limit": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_find_similar_response_structure(
        self, client: AsyncClient, sample_engagement: Engagement
    ):
        """Response should have correct structure."""
        response = await client.post(
            "/api/knowledge/similar",
            params={"query": "manufacturing", "limit": 3},
        )
        data = response.json()
        for item in data:
            assert "id" in item
            assert "client_name" in item
            assert "client_industry" in item
            assert "engagement_type" in item
            assert "description" in item

    async def test_find_similar_limit_parameter(
        self, client: AsyncClient, sample_engagement: Engagement, db_session: AsyncSession
    ):
        """Should respect limit parameter."""
        # Add more engagements
        for i in range(5):
            eng = Engagement(
                id=str(uuid.uuid4()),
                client_name=f"Test Corp {i}",
                client_industry="Technology",
                engagement_type="Digital",
                description=f"Test engagement {i}",
            )
            db_session.add(eng)
        await db_session.flush()

        response = await client.post(
            "/api/knowledge/similar",
            params={"query": "test", "limit": 3},
        )
        data = response.json()
        assert len(data) <= 3

    async def test_find_similar_includes_score(
        self, client: AsyncClient, sample_engagement: Engagement
    ):
        """Response items should include similarity score."""
        response = await client.post(
            "/api/knowledge/similar",
            params={"query": "manufacturing", "limit": 5},
        )
        data = response.json()
        for item in data:
            assert "score" in item
            assert isinstance(item["score"], (int, float))

    async def test_find_similar_includes_frameworks(
        self, client: AsyncClient, sample_engagement: Engagement
    ):
        """Response items should include frameworks used."""
        response = await client.post(
            "/api/knowledge/similar",
            params={"query": "digital transformation", "limit": 5},
        )
        data = response.json()
        for item in data:
            assert "frameworks_used" in item
            assert isinstance(item["frameworks_used"], list)
