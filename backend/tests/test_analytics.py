"""Tests for analytics API endpoints."""

import pytest
import uuid
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import AgentTrace, Message, Conversation, Document
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


class TestSocialAnalytics:
    """Tests for GET /api/analytics/social endpoint."""

    async def test_social_analytics_success(self, client: AsyncClient):
        """Should return 200 with correct structure."""
        response = await client.get("/api/analytics/social")
        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert "since" in data
        assert "summary" in data
        assert "agent_performance" in data
        assert "content_by_type" in data

    async def test_social_analytics_summary_fields(self, client: AsyncClient):
        """Summary should contain all expected fields."""
        response = await client.get("/api/analytics/social")
        data = response.json()
        summary = data["summary"]
        assert "total_content_generated" in summary
        assert "social_posts" in summary
        assert "avg_generation_seconds" in summary
        assert "total_agent_executions" in summary
        assert "total_tokens_used" in summary

    async def test_social_analytics_default_period(self, client: AsyncClient):
        """Should default to week period."""
        response = await client.get("/api/analytics/social")
        data = response.json()
        assert data["period"] == "week"

    async def test_social_analytics_day_period(self, client: AsyncClient):
        """Should support day period parameter."""
        response = await client.get("/api/analytics/social?period=day")
        data = response.json()
        assert data["period"] == "day"

    async def test_social_analytics_month_period(self, client: AsyncClient):
        """Should support month period parameter."""
        response = await client.get("/api/analytics/social?period=month")
        data = response.json()
        assert data["period"] == "month"

    async def test_social_analytics_with_traces(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Agent performance should reflect trace data."""
        now = datetime.utcnow()
        for agent, tokens, status in [
            ("orchestrator", 500, "completed"),
            ("researcher", 200, "completed"),
            ("scribe", 300, "completed"),
            ("analyst", 150, "failed"),
        ]:
            trace = AgentTrace(
                id=str(uuid.uuid4()),
                agent_name=agent,
                task_type="generate_content",
                status=status,
                started_at=now - timedelta(seconds=10),
                completed_at=now,
                tokens_used=tokens,
            )
            db_session.add(trace)
        await db_session.flush()

        response = await client.get("/api/analytics/social?period=day")
        data = response.json()
        assert data["summary"]["total_agent_executions"] >= 4
        assert data["summary"]["total_tokens_used"] >= 1150

    async def test_social_analytics_agent_performance_structure(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Agent performance entries should have correct fields."""
        trace = AgentTrace(
            id=str(uuid.uuid4()),
            agent_name="scribe",
            task_type="generate_content",
            status="completed",
            started_at=datetime.utcnow() - timedelta(seconds=5),
            completed_at=datetime.utcnow(),
            tokens_used=250,
        )
        db_session.add(trace)
        await db_session.flush()

        response = await client.get("/api/analytics/social?period=day")
        data = response.json()
        for perf in data["agent_performance"]:
            assert "agent" in perf
            assert "executions" in perf
            assert "avg_duration_seconds" in perf
            assert "total_tokens" in perf
            assert "avg_tokens" in perf
            assert "success_rate" in perf
            assert "failures" in perf

    async def test_social_analytics_content_by_type(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Content by type should count documents by doc_type."""
        for doc_type in ["social_post", "social_post", "proposal"]:
            doc = Document(
                id=str(uuid.uuid4()),
                title=f"Test {doc_type}",
                doc_type=doc_type,
                content="Test content",
                format="markdown",
            )
            db_session.add(doc)
        await db_session.flush()

        response = await client.get("/api/analytics/social?period=week")
        data = response.json()
        content = data["content_by_type"]
        assert content.get("social_post", 0) >= 2
        assert content.get("proposal", 0) >= 1

    async def test_social_analytics_success_rate_calculation(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Success rate should be correctly calculated."""
        now = datetime.utcnow()
        # 3 successful, 1 failed = 75% success rate
        for i, status in enumerate(["completed", "completed", "completed", "failed"]):
            trace = AgentTrace(
                id=str(uuid.uuid4()),
                agent_name="rate_test_agent",
                task_type="test",
                status=status,
                started_at=now - timedelta(seconds=5),
                completed_at=now,
                tokens_used=100,
            )
            db_session.add(trace)
        await db_session.flush()

        response = await client.get("/api/analytics/social?period=day")
        data = response.json()
        rate_agent = next(
            (p for p in data["agent_performance"] if p["agent"] == "rate_test_agent"),
            None,
        )
        assert rate_agent is not None
        assert rate_agent["success_rate"] == 75.0
        assert rate_agent["failures"] == 1

    async def test_social_analytics_sorted_by_executions(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Agent performance should be sorted by executions descending."""
        now = datetime.utcnow()
        # Create different counts per agent
        for agent, count in [("low_agent", 1), ("high_agent", 5), ("mid_agent", 3)]:
            for _ in range(count):
                trace = AgentTrace(
                    id=str(uuid.uuid4()),
                    agent_name=agent,
                    task_type="test",
                    status="completed",
                    started_at=now - timedelta(seconds=2),
                    completed_at=now,
                    tokens_used=50,
                )
                db_session.add(trace)
        await db_session.flush()

        response = await client.get("/api/analytics/social?period=day")
        data = response.json()
        perfs = data["agent_performance"]
        executions = [p["executions"] for p in perfs]
        assert executions == sorted(executions, reverse=True)
