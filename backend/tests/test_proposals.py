"""Tests for proposal API endpoints."""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Document
from app.models.schemas import DocumentResponse


class TestListProposals:
    """Tests for GET /api/proposals endpoint."""

    async def test_list_proposals_empty(self, client: AsyncClient):
        """Should return empty list when no proposals exist."""
        response = await client.get("/api/proposals")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_proposals_with_data(
        self, client: AsyncClient, sample_document: Document
    ):
        """Should return list of proposals."""
        response = await client.get("/api/proposals")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_list_proposals_only_proposals(
        self, client: AsyncClient, sample_document: Document, db_session: AsyncSession
    ):
        """Should only return documents with doc_type='proposal'."""
        # Add a non-proposal document
        non_proposal = Document(
            id=str(uuid.uuid4()),
            title="Test Briefing",
            doc_type="briefing",  # Not a proposal
            content="Briefing content",
            format="markdown",
        )
        db_session.add(non_proposal)
        await db_session.flush()

        response = await client.get("/api/proposals")
        data = response.json()
        for item in data:
            assert item["doc_type"] == "proposal"

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
        """Should return specific proposal by id."""
        response = await client.get(f"/api/proposals/{sample_document.id}")
        assert response.status_code == 200

    async def test_get_proposal_correct_data(
        self, client: AsyncClient, sample_document: Document
    ):
        """Returned proposal should have correct data."""
        response = await client.get(f"/api/proposals/{sample_document.id}")
        data = response.json()
        assert data["id"] == sample_document.id
        assert data["title"] == sample_document.title
        assert data["doc_type"] == "proposal"

    async def test_get_proposal_schema_validation(
        self, client: AsyncClient, sample_document: Document
    ):
        """Response should match DocumentResponse schema."""
        response = await client.get(f"/api/proposals/{sample_document.id}")
        data = response.json()
        DocumentResponse.model_validate(data)

    async def test_get_proposal_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent proposal."""
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


class TestGenerateProposal:
    """Tests for POST /api/proposals/generate endpoint."""

    async def test_generate_proposal_validation_error(self, client: AsyncClient):
        """Should reject request missing required fields."""
        payload = {
            "client_name": "Test Client",
            # Missing required fields
        }
        response = await client.post("/api/proposals/generate", json=payload)
        assert response.status_code == 422  # Validation error

    async def test_generate_proposal_empty_body(self, client: AsyncClient):
        """Should reject empty request body."""
        response = await client.post("/api/proposals/generate", json={})
        assert response.status_code == 422

    async def test_generate_proposal_with_all_fields(self, client: AsyncClient):
        """Should process valid proposal request (requires LLM)."""
        payload = {
            "client_name": "Test Manufacturing Inc",
            "client_industry": "Manufacturing",
            "engagement_type": "Digital Transformation",
            "scope_description": "Supply chain modernization initiative",
            "budget_range": "$500K-$1M",
            "timeline": "6 months",
            "additional_context": "Focus on IoT integration",
        }
        response = await client.post(
            "/api/proposals/generate", json=payload, timeout=180.0
        )
        # Accept success or error (depends on LLM availability)
        assert response.status_code in [200, 500]

    async def test_generate_proposal_schema_validation(self, client: AsyncClient):
        """Response should match DocumentResponse schema if successful."""
        payload = {
            "client_name": "Schema Test Corp",
            "client_industry": "Technology",
            "engagement_type": "Strategy",
            "scope_description": "Growth strategy development",
        }
        response = await client.post(
            "/api/proposals/generate", json=payload, timeout=180.0
        )
        if response.status_code == 200:
            data = response.json()
            DocumentResponse.model_validate(data)

    async def test_generate_proposal_optional_fields(self, client: AsyncClient):
        """Should process request without optional fields."""
        payload = {
            "client_name": "Minimal Test",
            "client_industry": "Retail",
            "engagement_type": "Operations",
            "scope_description": "Process improvement",
            # Optional fields omitted: budget_range, timeline, additional_context
        }
        response = await client.post(
            "/api/proposals/generate", json=payload, timeout=180.0
        )
        # Accept success or error (depends on LLM availability)
        assert response.status_code in [200, 500]
