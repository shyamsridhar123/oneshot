"""Tests for analytics API endpoints."""

import pytest
import uuid
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import AgentTrace, Message, Conversation
from app.models.schemas import AgentTraceResponse


class TestListTraces:
    """Tests for GET /api/analytics/traces endpoint."""

    async def test_list_traces_empty(self, client: AsyncClient):
        """Should return empty list when no traces exist."""
        response = await client.get("/api/analytics/traces")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_traces_with_data(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Should return list of traces."""
        # Create a trace
        trace = AgentTrace(
            id=str(uuid.uuid4()),
            agent_name="orchestrator",
            task_type="process_message",
            status="completed",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow() + timedelta(seconds=5),
            tokens_used=150,
        )
        db_session.add(trace)
        await db_session.flush()

        response = await client.get("/api/analytics/traces")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_list_traces_schema_validation(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Response should match AgentTraceResponse schema."""
        trace = AgentTrace(
            id=str(uuid.uuid4()),
            agent_name="researcher",
            task_type="search",
            status="completed",
            started_at=datetime.utcnow(),
            tokens_used=100,
        )
        db_session.add(trace)
        await db_session.flush()

        response = await client.get("/api/analytics/traces")
        data = response.json()
        for item in data:
            AgentTraceResponse.model_validate(item)

    async def test_list_traces_filter_by_agent(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Should filter traces by agent_name."""
        # Create traces for different agents
        for agent in ["orchestrator", "researcher", "analyst"]:
            trace = AgentTrace(
                id=str(uuid.uuid4()),
                agent_name=agent,
                task_type="test",
                status="completed",
                started_at=datetime.utcnow(),
                tokens_used=50,
            )
            db_session.add(trace)
        await db_session.flush()

        response = await client.get("/api/analytics/traces?agent_name=researcher")
        data = response.json()
        for item in data:
            assert item["agent_name"] == "researcher"

    async def test_list_traces_filter_by_status(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Should filter traces by status."""
        # Create traces with different statuses
        for status in ["completed", "failed", "running"]:
            trace = AgentTrace(
                id=str(uuid.uuid4()),
                agent_name="test_agent",
                task_type="test",
                status=status,
                started_at=datetime.utcnow(),
                tokens_used=25,
            )
            db_session.add(trace)
        await db_session.flush()

        response = await client.get("/api/analytics/traces?status=completed")
        data = response.json()
        for item in data:
            assert item["status"] == "completed"

    async def test_list_traces_pagination(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Should support limit and offset parameters."""
        # Create multiple traces
        for i in range(10):
            trace = AgentTrace(
                id=str(uuid.uuid4()),
                agent_name="paginated_agent",
                task_type="test",
                status="completed",
                started_at=datetime.utcnow(),
                tokens_used=i * 10,
            )
            db_session.add(trace)
        await db_session.flush()

        response = await client.get("/api/analytics/traces?limit=5&offset=0")
        data = response.json()
        assert len(data) <= 5

    async def test_list_traces_includes_tokens(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Traces should include tokens_used field."""
        trace = AgentTrace(
            id=str(uuid.uuid4()),
            agent_name="token_test",
            task_type="test",
            status="completed",
            started_at=datetime.utcnow(),
            tokens_used=500,
        )
        db_session.add(trace)
        await db_session.flush()

        response = await client.get("/api/analytics/traces")
        data = response.json()
        for item in data:
            assert "tokens_used" in item


class TestGetMetrics:
    """Tests for GET /api/analytics/metrics endpoint."""

    async def test_get_metrics_success(self, client: AsyncClient):
        """Should return metrics."""
        response = await client.get("/api/analytics/metrics")
        assert response.status_code == 200

    async def test_get_metrics_response_structure(self, client: AsyncClient):
        """Response should have correct structure."""
        response = await client.get("/api/analytics/metrics")
        data = response.json()
        assert "period" in data
        assert "since" in data
        assert "agent_stats" in data
        assert "total_executions" in data

    async def test_get_metrics_day_period(self, client: AsyncClient):
        """Should support day period."""
        response = await client.get("/api/analytics/metrics?period=day")
        data = response.json()
        assert data["period"] == "day"

    async def test_get_metrics_week_period(self, client: AsyncClient):
        """Should support week period."""
        response = await client.get("/api/analytics/metrics?period=week")
        data = response.json()
        assert data["period"] == "week"

    async def test_get_metrics_month_period(self, client: AsyncClient):
        """Should support month period."""
        response = await client.get("/api/analytics/metrics?period=month")
        data = response.json()
        assert data["period"] == "month"

    async def test_get_metrics_default_period(self, client: AsyncClient):
        """Should default to day period."""
        response = await client.get("/api/analytics/metrics")
        data = response.json()
        assert data["period"] == "day"

    async def test_get_metrics_with_traces(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Metrics should reflect actual trace data."""
        # Create traces for different agents
        for agent, tokens in [("orchestrator", 100), ("researcher", 200), ("analyst", 150)]:
            trace = AgentTrace(
                id=str(uuid.uuid4()),
                agent_name=agent,
                task_type="test",
                status="completed",
                started_at=datetime.utcnow(),
                tokens_used=tokens,
            )
            db_session.add(trace)
        await db_session.flush()

        response = await client.get("/api/analytics/metrics?period=day")
        data = response.json()
        assert data["total_executions"] >= 3
        assert len(data["agent_stats"]) >= 3

    async def test_get_metrics_agent_stats_structure(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Agent stats should have correct structure."""
        trace = AgentTrace(
            id=str(uuid.uuid4()),
            agent_name="metric_test",
            task_type="test",
            status="completed",
            started_at=datetime.utcnow(),
            tokens_used=250,
        )
        db_session.add(trace)
        await db_session.flush()

        response = await client.get("/api/analytics/metrics?period=day")
        data = response.json()
        for stat in data["agent_stats"]:
            assert "agent" in stat
            assert "executions" in stat
            assert "avg_tokens" in stat

    async def test_get_metrics_since_datetime(self, client: AsyncClient):
        """Response should include since datetime."""
        response = await client.get("/api/analytics/metrics?period=week")
        data = response.json()
        assert "since" in data
        # Validate it's a valid ISO datetime
        datetime.fromisoformat(data["since"])
