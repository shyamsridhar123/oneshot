"""Tests for research API endpoints."""

import pytest
from httpx import AsyncClient


class TestResearchQuery:
    """Tests for POST /api/research/query endpoint."""

    async def test_research_query_success(self, client: AsyncClient):
        """Should accept valid research query."""
        response = await client.post(
            "/api/research/query",
            json={
                "query": "digital transformation trends in manufacturing",
                "research_type": "comprehensive",
            },
        )
        assert response.status_code == 200

    async def test_research_query_response_structure(self, client: AsyncClient):
        """Response should have correct structure."""
        response = await client.post(
            "/api/research/query",
            json={
                "query": "supply chain optimization",
                "research_type": "quick",
            },
        )
        data = response.json()
        assert "query" in data
        assert "research_type" in data
        assert "status" in data

    async def test_research_query_reflects_input(self, client: AsyncClient):
        """Response should reflect input query."""
        query_text = "AI in healthcare"
        response = await client.post(
            "/api/research/query",
            json={"query": query_text, "research_type": "comprehensive"},
        )
        data = response.json()
        assert data["query"] == query_text

    async def test_research_query_validation_empty_query(self, client: AsyncClient):
        """Should reject empty query."""
        response = await client.post(
            "/api/research/query",
            json={"query": "", "research_type": "comprehensive"},
        )
        assert response.status_code == 422

    async def test_research_query_default_type(self, client: AsyncClient):
        """Should use default research type when not specified."""
        response = await client.post(
            "/api/research/query",
            json={"query": "test query"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["research_type"] == "comprehensive"

    async def test_research_query_with_sources(self, client: AsyncClient):
        """Should accept sources parameter."""
        response = await client.post(
            "/api/research/query",
            json={
                "query": "market analysis",
                "research_type": "deep",
                "sources": ["web", "news"],
            },
        )
        assert response.status_code == 200

    async def test_research_query_quick_type(self, client: AsyncClient):
        """Should accept quick research type."""
        response = await client.post(
            "/api/research/query",
            json={"query": "quick test", "research_type": "quick"},
        )
        assert response.status_code == 200

    async def test_research_query_deep_type(self, client: AsyncClient):
        """Should accept deep research type."""
        response = await client.post(
            "/api/research/query",
            json={"query": "deep analysis", "research_type": "deep"},
        )
        assert response.status_code == 200


class TestGenerateBriefing:
    """Tests for POST /api/research/briefing endpoint."""

    async def test_generate_briefing_success(self, client: AsyncClient):
        """Should accept valid briefing request."""
        response = await client.post(
            "/api/research/briefing",
            json={
                "company_name": "Test Corporation",
                "industry": "Technology",
                "focus_areas": ["digital strategy", "innovation"],
            },
        )
        assert response.status_code == 200

    async def test_generate_briefing_response_structure(self, client: AsyncClient):
        """Response should have correct structure."""
        response = await client.post(
            "/api/research/briefing",
            json={"company_name": "Acme Inc"},
        )
        data = response.json()
        assert "company_name" in data
        assert "status" in data

    async def test_generate_briefing_reflects_company(self, client: AsyncClient):
        """Response should reflect input company name."""
        company = "Global Manufacturing Corp"
        response = await client.post(
            "/api/research/briefing",
            json={"company_name": company},
        )
        data = response.json()
        assert data["company_name"] == company

    async def test_generate_briefing_status_completed(self, client: AsyncClient):
        """Response should indicate completed status after synchronous processing."""
        response = await client.post(
            "/api/research/briefing",
            json={"company_name": "Test Corp"},
        )
        data = response.json()
        assert data["status"] == "completed"

    async def test_generate_briefing_validation_missing_company(
        self, client: AsyncClient
    ):
        """Should reject request without company name."""
        response = await client.post(
            "/api/research/briefing",
            json={"industry": "Technology"},  # Missing company_name
        )
        assert response.status_code == 422

    async def test_generate_briefing_with_industry(self, client: AsyncClient):
        """Should accept optional industry parameter."""
        response = await client.post(
            "/api/research/briefing",
            json={
                "company_name": "Healthcare Partners",
                "industry": "Healthcare",
            },
        )
        assert response.status_code == 200

    async def test_generate_briefing_with_focus_areas(self, client: AsyncClient):
        """Should accept optional focus areas."""
        response = await client.post(
            "/api/research/briefing",
            json={
                "company_name": "FinTech Solutions",
                "focus_areas": ["compliance", "digital banking", "payments"],
            },
        )
        assert response.status_code == 200

    async def test_generate_briefing_empty_focus_areas(self, client: AsyncClient):
        """Should accept empty focus areas list."""
        response = await client.post(
            "/api/research/briefing",
            json={
                "company_name": "Simple Corp",
                "focus_areas": [],
            },
        )
        assert response.status_code == 200
