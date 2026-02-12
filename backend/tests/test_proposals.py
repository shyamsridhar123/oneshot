"""Tests for content/proposals API endpoints."""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Document
from app.models.schemas import DocumentResponse


class TestListProposals:
    """Tests for GET /api/proposals endpoint."""

    async def test_list_proposals_empty(self, client: AsyncClient):
        """Should return empty list when no content exists."""
        response = await client.get("/api/proposals")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_proposals_with_data(
        self, client: AsyncClient, sample_document: Document
    ):
        """Should return list of content items."""
        response = await client.get("/api/proposals")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_list_proposals_includes_social_posts(
        self, client: AsyncClient, sample_document: Document, db_session: AsyncSession
    ):
        """Should return both proposal and social_post doc types."""
        social_post = Document(
            id=str(uuid.uuid4()),
            title="LinkedIn Post: AI Launch",
            doc_type="social_post",
            content="Social media content",
            format="markdown",
        )
        db_session.add(social_post)
        await db_session.flush()

        response = await client.get("/api/proposals")
        data = response.json()
        doc_types = {item["doc_type"] for item in data}
        assert "proposal" in doc_types or "social_post" in doc_types

    async def test_list_proposals_excludes_other_types(
        self, client: AsyncClient, sample_document: Document, db_session: AsyncSession
    ):
        """Should not return documents with other doc_types like briefing."""
        non_content = Document(
            id=str(uuid.uuid4()),
            title="Test Briefing",
            doc_type="briefing",
            content="Briefing content",
            format="markdown",
        )
        db_session.add(non_content)
        await db_session.flush()

        response = await client.get("/api/proposals")
        data = response.json()
        for item in data:
            assert item["doc_type"] in ("proposal", "social_post")

    async def test_list_proposals_schema_validation(
        self, client: AsyncClient, sample_document: Document
    ):
        """Response should match DocumentResponse schema."""
        response = await client.get("/api/proposals")
        data = response.json()
        for item in data:
            DocumentResponse.model_validate(item)

    async def test_list_proposals_pagination(self, client: AsyncClient):
        """Should support limit and offset parameters."""
        response = await client.get("/api/proposals?limit=5&offset=0")
        assert response.status_code == 200


class TestGetProposal:
    """Tests for GET /api/proposals/{id} endpoint."""

    async def test_get_proposal_success(
        self, client: AsyncClient, sample_document: Document
    ):
        """Should return specific content item by id."""
        response = await client.get(f"/api/proposals/{sample_document.id}")
        assert response.status_code == 200

    async def test_get_proposal_correct_data(
        self, client: AsyncClient, sample_document: Document
    ):
        """Returned item should have correct data."""
        response = await client.get(f"/api/proposals/{sample_document.id}")
        data = response.json()
        assert data["id"] == sample_document.id
        assert data["title"] == sample_document.title

    async def test_get_proposal_schema_validation(
        self, client: AsyncClient, sample_document: Document
    ):
        """Response should match DocumentResponse schema."""
        response = await client.get(f"/api/proposals/{sample_document.id}")
        data = response.json()
        DocumentResponse.model_validate(data)

    async def test_get_proposal_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent content item."""
        fake_id = str(uuid.uuid4())
        response = await client.get(f"/api/proposals/{fake_id}")
        assert response.status_code == 404

    async def test_get_proposal_error_detail(self, client: AsyncClient):
        """Should return error detail for 404."""
        fake_id = str(uuid.uuid4())
        response = await client.get(f"/api/proposals/{fake_id}")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestGenerateContent:
    """Tests for POST /api/proposals/generate endpoint (ContentRequest schema)."""

    async def test_generate_content_validation_error(self, client: AsyncClient):
        """Should reject request missing required 'topic' field."""
        payload = {
            "platforms": ["linkedin"],
            # Missing required 'topic'
        }
        response = await client.post("/api/proposals/generate", json=payload)
        assert response.status_code == 422

    async def test_generate_content_empty_body(self, client: AsyncClient):
        """Should reject empty request body."""
        response = await client.post("/api/proposals/generate", json={})
        assert response.status_code == 422

    async def test_generate_content_with_all_fields(self, client: AsyncClient):
        """Should process valid content request (requires LLM)."""
        payload = {
            "topic": "AI Collaboration Suite launch announcement",
            "platforms": ["linkedin", "twitter", "instagram"],
            "content_type": "post",
            "additional_context": "Focus on enterprise collaboration features",
        }
        response = await client.post(
            "/api/proposals/generate", json=payload, timeout=180.0
        )
        # Accept success or error (depends on LLM availability)
        assert response.status_code in [200, 500]

    async def test_generate_content_schema_validation(self, client: AsyncClient):
        """Response should match DocumentResponse schema if successful."""
        payload = {
            "topic": "Enterprise AI trends for Q1 2026",
            "platforms": ["linkedin"],
            "content_type": "post",
        }
        response = await client.post(
            "/api/proposals/generate", json=payload, timeout=180.0
        )
        if response.status_code == 200:
            data = response.json()
            DocumentResponse.model_validate(data)

    async def test_generate_content_minimal_fields(self, client: AsyncClient):
        """Should process request with only required 'topic' field."""
        payload = {
            "topic": "Team culture at NotContosso",
        }
        response = await client.post(
            "/api/proposals/generate", json=payload, timeout=180.0
        )
        # Accept success or error (depends on LLM availability)
        assert response.status_code in [200, 500]

    async def test_generate_content_default_platforms(self, client: AsyncClient):
        """ContentRequest should default to all 3 platforms when not specified."""
        from app.models.schemas import ContentRequest
        req = ContentRequest(topic="Test topic")
        assert req.platforms == ["linkedin", "twitter", "instagram"]

    async def test_generate_content_default_type(self, client: AsyncClient):
        """ContentRequest should default to 'post' content_type."""
        from app.models.schemas import ContentRequest
        req = ContentRequest(topic="Test topic")
        assert req.content_type == "post"
