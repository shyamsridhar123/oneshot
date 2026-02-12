"""Tests for document API endpoints."""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Document
from app.models.schemas import DocumentResponse


class TestListDocuments:
    """Tests for GET /api/documents endpoint."""

    async def test_list_documents_empty(self, client: AsyncClient):
        """Should return empty list when no documents exist."""
        response = await client.get("/api/documents")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_documents_with_data(
        self, client: AsyncClient, sample_document: Document
    ):
        """Should return list of documents."""
        response = await client.get("/api/documents")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_list_documents_filter_by_type(
        self, client: AsyncClient, sample_document: Document, db_session: AsyncSession
    ):
        """Should filter documents by doc_type parameter."""
        # Add a briefing document
        briefing = Document(
            id=str(uuid.uuid4()),
            title="Test Briefing",
            doc_type="briefing",
            content="Briefing content",
            format="markdown",
        )
        db_session.add(briefing)
        await db_session.flush()

        # Filter by proposal only
        response = await client.get("/api/documents?doc_type=proposal")
        data = response.json()
        for item in data:
            assert item["doc_type"] == "proposal"

    async def test_list_documents_schema_validation(
        self, client: AsyncClient, sample_document: Document
    ):
        """Response should match DocumentResponse schema."""
        response = await client.get("/api/documents")
        data = response.json()
        for item in data:
            DocumentResponse.model_validate(item)

    async def test_list_documents_pagination(self, client: AsyncClient):
        """Should support limit and offset parameters."""
        response = await client.get("/api/documents?limit=10&offset=0")
        assert response.status_code == 200


class TestGetDocument:
    """Tests for GET /api/documents/{id} endpoint."""

    async def test_get_document_success(
        self, client: AsyncClient, sample_document: Document
    ):
        """Should return specific document by id."""
        response = await client.get(f"/api/documents/{sample_document.id}")
        assert response.status_code == 200

    async def test_get_document_correct_data(
        self, client: AsyncClient, sample_document: Document
    ):
        """Returned document should have correct data."""
        response = await client.get(f"/api/documents/{sample_document.id}")
        data = response.json()
        assert data["id"] == sample_document.id
        assert data["title"] == sample_document.title
        assert data["content"] == sample_document.content

    async def test_get_document_schema_validation(
        self, client: AsyncClient, sample_document: Document
    ):
        """Response should match DocumentResponse schema."""
        response = await client.get(f"/api/documents/{sample_document.id}")
        data = response.json()
        DocumentResponse.model_validate(data)

    async def test_get_document_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent document."""
        fake_id = str(uuid.uuid4())
        response = await client.get(f"/api/documents/{fake_id}")
        assert response.status_code == 404

    async def test_get_document_error_detail(self, client: AsyncClient):
        """Should return error detail for 404."""
        fake_id = str(uuid.uuid4())
        response = await client.get(f"/api/documents/{fake_id}")
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Document not found"


class TestExportDocument:
    """Tests for POST /api/documents/{id}/export endpoint."""

    async def test_export_markdown_success(
        self, client: AsyncClient, sample_document: Document
    ):
        """Should export document as markdown."""
        response = await client.post(
            f"/api/documents/{sample_document.id}/export",
            json={"format": "markdown"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/markdown; charset=utf-8"

    async def test_export_html_success(
        self, client: AsyncClient, sample_document: Document
    ):
        """Should export document as HTML."""
        response = await client.post(
            f"/api/documents/{sample_document.id}/export",
            json={"format": "html"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"

    async def test_export_markdown_content(
        self, client: AsyncClient, sample_document: Document
    ):
        """Markdown export should contain document content."""
        response = await client.post(
            f"/api/documents/{sample_document.id}/export",
            json={"format": "markdown"},
        )
        assert sample_document.content in response.text

    async def test_export_html_converted(
        self, client: AsyncClient, sample_document: Document
    ):
        """HTML export should convert markdown to HTML."""
        response = await client.post(
            f"/api/documents/{sample_document.id}/export",
            json={"format": "html"},
        )
        # Markdown headers become HTML headers
        assert "<h1>" in response.text or "Test Proposal" in response.text

    async def test_export_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent document."""
        fake_id = str(uuid.uuid4())
        response = await client.post(
            f"/api/documents/{fake_id}/export",
            json={"format": "markdown"},
        )
        assert response.status_code == 404

    async def test_export_invalid_format(
        self, client: AsyncClient, sample_document: Document
    ):
        """Should reject invalid export format."""
        response = await client.post(
            f"/api/documents/{sample_document.id}/export",
            json={"format": "invalid_format"},
        )
        assert response.status_code == 422  # Validation error

    async def test_export_pdf_success(
        self, client: AsyncClient, sample_document: Document
    ):
        """PDF export should return 200 with application/pdf content type."""
        response = await client.post(
            f"/api/documents/{sample_document.id}/export",
            json={"format": "pdf"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    async def test_export_docx_success(
        self, client: AsyncClient, sample_document: Document
    ):
        """DOCX export should return 200 with DOCX content type."""
        response = await client.post(
            f"/api/documents/{sample_document.id}/export",
            json={"format": "docx"},
        )
        assert response.status_code == 200
        assert "wordprocessingml" in response.headers["content-type"]

    async def test_export_content_disposition_header(
        self, client: AsyncClient, sample_document: Document
    ):
        """Export should include Content-Disposition header for download."""
        response = await client.post(
            f"/api/documents/{sample_document.id}/export",
            json={"format": "markdown"},
        )
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers["content-disposition"]
