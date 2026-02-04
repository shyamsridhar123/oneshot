"""Tests for core endpoints: health check and root."""

import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""

    async def test_health_check_returns_200(self, client: AsyncClient):
        """Health check should return 200 status."""
        response = await client.get("/health")
        assert response.status_code == 200

    async def test_health_check_returns_healthy_status(self, client: AsyncClient):
        """Health check should return healthy status in body."""
        response = await client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    async def test_health_check_response_structure(self, client: AsyncClient):
        """Health check should have correct response structure."""
        response = await client.get("/health")
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        assert "version" in data


class TestRootEndpoint:
    """Tests for GET / root endpoint."""

    async def test_root_returns_200(self, client: AsyncClient):
        """Root endpoint should return 200 status."""
        response = await client.get("/")
        assert response.status_code == 200

    async def test_root_returns_api_info(self, client: AsyncClient):
        """Root endpoint should return API information."""
        response = await client.get("/")
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "docs" in data

    async def test_root_api_name(self, client: AsyncClient):
        """Root endpoint should return Federation API name."""
        response = await client.get("/")
        data = response.json()
        assert data["name"] == "Federation API"

    async def test_root_docs_link(self, client: AsyncClient):
        """Root endpoint should point to /docs."""
        response = await client.get("/")
        data = response.json()
        assert data["docs"] == "/docs"
