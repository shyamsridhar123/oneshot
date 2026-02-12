"""Research API routes - wired to Researcher agent with MCP tools."""

import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.schemas import ResearchRequest, BriefingRequest
from app.agents.researcher import run_researcher
from app.agents.memory import run_memory
from app.agents.scribe import run_scribe
from app.services.llm_service import get_llm_service
from app.agents.prompts import AGENT_PROMPTS
from app.api.websocket import manager as ws_manager

logger = logging.getLogger(__name__)

router = APIRouter()

# Tool info per agent, matching the orchestrator's _execute_agent pattern
_TOOL_INFO = {
    "researcher": [("search_web", "tool"), ("search_news", "tool"), ("search_trends", "tool"), ("fetch_mcp", "mcp")],
    "memory": [("get_brand_guidelines", "tool"), ("get_past_posts", "tool"), ("search_knowledge_base", "tool")],
    "scribe": [("filesystem_mcp", "mcp")],
}


async def _execute_with_ws(
    agent_name: str,
    task: str,
    run_fn,
    run_kwargs: dict,
    session_id: Optional[str],
) -> tuple[str, int]:
    """Execute an agent function, broadcasting WebSocket events if session_id is provided."""
    start_time = time.time()

    if session_id:
        await ws_manager.send_agent_started(session_id, agent_name, task[:100])
        for tool_name, tool_type in _TOOL_INFO.get(agent_name, []):
            await ws_manager.send_agent_tool_call(session_id, agent_name, tool_name, tool_type)

    try:
        result, tokens_used = await run_fn(**run_kwargs)
        duration_ms = int((time.time() - start_time) * 1000)

        if session_id:
            await ws_manager.send_agent_completed(
                session_id, agent_name, result[:100], duration_ms
            )

        return result, tokens_used

    except Exception as e:
        if session_id:
            await ws_manager.send_agent_completed(session_id, agent_name, f"Error: {str(e)}", 0)
        raise


@router.post("/query")
async def research_query(
    data: ResearchRequest,
    db: AsyncSession = Depends(get_db),
    session_id: Optional[str] = Query(None, description="WebSocket session ID for live agent status"),
):
    """Execute a research query via the Researcher agent with MCP tools."""
    context = {
        "message": data.query,
        "entities": [],
        "platforms": ["linkedin", "twitter", "instagram"],
        "sources": data.sources,
    }

    try:
        if session_id:
            await ws_manager.send_agent_started(session_id, "orchestrator", "Starting research query")
            await ws_manager.send_agent_thinking(session_id, "orchestrator", "Dispatching researcher agent...", 0.1)
            await ws_manager.send_agent_handoff(session_id, "orchestrator", "researcher", f"Research: {data.query}")

        findings, tokens_used = await _execute_with_ws(
            agent_name="researcher",
            task=f"Research: {data.query}",
            run_fn=run_researcher,
            run_kwargs={"task": f"Research: {data.query}", "context": context},
            session_id=session_id,
        )

        if session_id:
            await ws_manager.send_agent_completed(session_id, "orchestrator", "Research complete", 0)

        return {
            "query": data.query,
            "research_type": data.research_type,
            "status": "completed",
            "message": findings,
            "tokens_used": tokens_used,
        }
    except Exception as e:
        logger.error("Research query failed: %s", e)
        if session_id:
            await ws_manager.send_agent_completed(session_id, "orchestrator", f"Error: {str(e)}", 0)
        return {
            "query": data.query,
            "research_type": data.research_type,
            "status": "error",
            "message": f"Research failed: {str(e)}",
        }


@router.post("/briefing")
async def generate_briefing(
    data: BriefingRequest,
    db: AsyncSession = Depends(get_db),
    session_id: Optional[str] = Query(None, description="WebSocket session ID for live agent status"),
):
    """Generate a client briefing via Researcher + Memory + Scribe agents."""
    context = {
        "message": f"Generate a briefing for {data.company_name}",
        "entities": [data.company_name],
        "platforms": ["linkedin", "twitter", "instagram"],
    }
    if data.industry:
        context["message"] += f" in the {data.industry} industry"

    try:
        if session_id:
            await ws_manager.send_agent_started(session_id, "orchestrator", "Starting client briefing")
            await ws_manager.send_agent_thinking(session_id, "orchestrator", "Dispatching research agents...", 0.1)

        # Wave 1: researcher + memory in parallel
        if session_id:
            await ws_manager.send_agent_handoff(session_id, "orchestrator", "researcher", f"Research {data.company_name}")
            await ws_manager.send_agent_handoff(session_id, "orchestrator", "memory", f"Brand context for {data.company_name}")

        import asyncio
        (research_result, r_tokens), (memory_result, m_tokens) = await asyncio.gather(
            _execute_with_ws(
                agent_name="researcher",
                task=f"Research {data.company_name} for a client briefing",
                run_fn=run_researcher,
                run_kwargs={"task": f"Research {data.company_name} for a client briefing", "context": context},
                session_id=session_id,
            ),
            _execute_with_ws(
                agent_name="memory",
                task=f"Retrieve brand context relevant to {data.company_name}",
                run_fn=run_memory,
                run_kwargs={"task": f"Retrieve brand context relevant to {data.company_name}", "context": context, "db": db},
                session_id=session_id,
            ),
        )

        # Wave 2: scribe with context from wave 1
        if session_id:
            await ws_manager.send_agent_thinking(session_id, "orchestrator", "Writing briefing document...", 0.6)
            await ws_manager.send_agent_handoff(session_id, "orchestrator", "scribe", f"Write briefing for {data.company_name}")

        scribe_context = {
            **context,
            "previous_results": {
                "researcher": research_result,
                "memory": memory_result,
            },
        }
        briefing_content, s_tokens = await _execute_with_ws(
            agent_name="scribe",
            task=f"Write a professional briefing about {data.company_name}",
            run_fn=run_scribe,
            run_kwargs={"task": f"Write a professional briefing about {data.company_name}", "context": scribe_context},
            session_id=session_id,
        )

        if session_id:
            await ws_manager.send_agent_completed(session_id, "orchestrator", "Briefing complete", 0)

        return {
            "company_name": data.company_name,
            "status": "completed",
            "message": briefing_content,
            "tokens_used": r_tokens + m_tokens + s_tokens,
        }
    except Exception as e:
        logger.error("Briefing generation failed: %s", e)
        if session_id:
            await ws_manager.send_agent_completed(session_id, "orchestrator", f"Error: {str(e)}", 0)
        return {
            "company_name": data.company_name,
            "status": "error",
            "message": f"Briefing generation failed: {str(e)}",
        }
