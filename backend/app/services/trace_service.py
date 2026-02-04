"""Agent tracing service for observability."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import AgentTrace


class TraceService:
    """Service for recording agent execution traces."""

    async def start_trace(
        self,
        db: AsyncSession,
        agent_name: str,
        task_type: str,
        input_data: dict,
        message_id: Optional[str] = None,
    ) -> AgentTrace:
        """Start a new agent trace."""
        trace = AgentTrace(
            id=str(uuid.uuid4()),
            message_id=message_id,
            agent_name=agent_name,
            task_type=task_type,
            input_data=input_data,
            started_at=datetime.utcnow(),
            status="running",
        )
        db.add(trace)
        await db.flush()
        return trace

    async def complete_trace(
        self,
        db: AsyncSession,
        trace: AgentTrace,
        output_data: dict,
        tokens_used: int = 0,
    ) -> AgentTrace:
        """Mark a trace as completed."""
        trace.output_data = output_data
        trace.completed_at = datetime.utcnow()
        trace.status = "completed"
        trace.tokens_used = tokens_used
        await db.flush()
        return trace

    async def fail_trace(
        self,
        db: AsyncSession,
        trace: AgentTrace,
        error: str,
    ) -> AgentTrace:
        """Mark a trace as failed."""
        trace.completed_at = datetime.utcnow()
        trace.status = "failed"
        trace.error = error
        await db.flush()
        return trace


# Singleton
_trace_service: TraceService | None = None


def get_trace_service() -> TraceService:
    """Get or create trace service singleton."""
    global _trace_service
    if _trace_service is None:
        _trace_service = TraceService()
    return _trace_service
