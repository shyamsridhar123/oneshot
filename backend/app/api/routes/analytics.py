"""Analytics API routes."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db, AgentTrace, Metric
from app.models.schemas import AgentTraceResponse

router = APIRouter()


@router.get("/traces", response_model=list[AgentTraceResponse])
async def list_traces(
    agent_name: str = None,
    status: str = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List agent execution traces."""
    query = select(AgentTrace).order_by(AgentTrace.started_at.desc())
    
    if agent_name:
        query = query.where(AgentTrace.agent_name == agent_name)
    if status:
        query = query.where(AgentTrace.status == status)
    
    result = await db.execute(query.offset(offset).limit(limit))
    traces = result.scalars().all()
    
    return [
        AgentTraceResponse(
            id=trace.id,
            agent_name=trace.agent_name,
            task_type=trace.task_type,
            status=trace.status,
            started_at=trace.started_at,
            completed_at=trace.completed_at,
            tokens_used=trace.tokens_used,
            error=trace.error,
        )
        for trace in traces
    ]


@router.get("/metrics")
async def get_metrics(
    period: str = "day",  # day, week, month
    db: AsyncSession = Depends(get_db),
):
    """Get performance metrics."""
    now = datetime.utcnow()
    
    if period == "day":
        since = now - timedelta(days=1)
    elif period == "week":
        since = now - timedelta(weeks=1)
    else:
        since = now - timedelta(days=30)
    
    # Agent execution stats
    trace_result = await db.execute(
        select(
            AgentTrace.agent_name,
            func.count(AgentTrace.id).label("count"),
            func.avg(AgentTrace.tokens_used).label("avg_tokens"),
        )
        .where(AgentTrace.started_at >= since)
        .group_by(AgentTrace.agent_name)
    )
    agent_stats = trace_result.all()
    
    return {
        "period": period,
        "since": since.isoformat(),
        "agent_stats": [
            {
                "agent": stat.agent_name,
                "executions": stat.count,
                "avg_tokens": round(stat.avg_tokens or 0, 2),
            }
            for stat in agent_stats
        ],
        "total_executions": sum(stat.count for stat in agent_stats),
    }
