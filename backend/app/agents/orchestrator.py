"""Orchestrator Agent - Coordinates all other agents using MAF workflow patterns.

Social Media Command Center variant with two-wave parallel dispatch:
  Wave 1 (context gathering): researcher, strategist, memory, analyst
  Wave 2 (creation + review): scribe, advisor
"""

import asyncio
import uuid
import time
from datetime import datetime
from typing import Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.prompts import AGENT_PROMPTS
from app.agents.strategist import run_strategist
from app.agents.researcher import run_researcher
from app.agents.analyst import run_analyst
from app.agents.scribe import run_scribe
from app.agents.advisor import run_advisor
from app.agents.memory import run_memory
from app.services.llm_service import get_llm_service
from app.services.trace_service import get_trace_service
from app.services.document_service import get_document_service
from app.api.websocket import ConnectionManager
from app.models.database import Document


# Intent classification schema for structured output
INTENT_SCHEMA = {
    "name": "intent_analysis",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "primary_intent": {
                "type": "string",
                "enum": [
                    "content_creation",
                    "content_strategy",
                    "content_review",
                    "trend_research",
                    "question",
                    "other",
                ],
            },
            "target_platforms": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["linkedin", "twitter", "instagram"],
                },
            },
            "required_agents": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["strategist", "researcher", "analyst", "scribe", "advisor", "memory"],
                },
            },
            "key_entities": {
                "type": "array",
                "items": {"type": "string"},
            },
            "task_description": {"type": "string"},
        },
        "required": [
            "primary_intent",
            "target_platforms",
            "required_agents",
            "key_entities",
            "task_description",
        ],
        "additionalProperties": False,
    },
}

# Routing: which agents run in each wave per intent type
_WAVE_CONFIG = {
    "content_creation": {
        "wave1": ["researcher", "strategist", "memory", "analyst"],
        "wave2": ["scribe", "advisor"],
    },
    "content_strategy": {
        "wave1": ["researcher", "strategist", "memory", "analyst"],
        "wave2": ["advisor"],
    },
    "content_review": {
        "wave1": ["memory"],
        "wave2": ["advisor"],
    },
    "trend_research": {
        "wave1": ["researcher", "analyst", "memory"],
        "wave2": [],
    },
}


async def process_message(
    conversation_id: str,
    message_content: str,
    message_metadata: dict,
    ws_manager: ConnectionManager,
    db: AsyncSession,
) -> str:
    """Process a user message through the orchestrator.

    Two-wave parallel dispatch:
      Wave 1: Context gathering (researcher, strategist, memory, analyst)
      Wave 2: Content creation + review (scribe, advisor) using Wave 1 outputs
    """
    llm = get_llm_service()
    trace_service = get_trace_service()

    start_time = time.time()

    # Start orchestrator trace
    trace = await trace_service.start_trace(
        db=db,
        agent_name="orchestrator",
        task_type="message_processing",
        input_data={"message": message_content, "metadata": message_metadata},
    )

    # Notify WebSocket clients
    await ws_manager.send_agent_started(conversation_id, "orchestrator", "Analyzing request")

    try:
        # ── Step 1: Classify intent ────────────────────────────────
        await ws_manager.send_agent_thinking(
            conversation_id, "orchestrator", "Understanding your request...", 0.1
        )

        intent = await llm.structured_output(
            prompt=f"""Analyze this user request and determine how to handle it:

User Request: {message_content}

Determine:
1. The primary intent:
   - content_creation: User wants to create social media posts for one or more platforms
   - content_strategy: User wants a content plan, calendar, or strategy
   - content_review: User wants existing content reviewed for brand alignment
   - trend_research: User wants to understand current trends, topics, or competitor activity
   - question: A general question about social media or the platform
   - other: Anything else
2. Target platforms mentioned or implied (linkedin, twitter, instagram). If none specified, include all three.
3. Which specialist agents should be involved
4. Key entities mentioned (brands, topics, platforms, campaigns)
5. A clear task description""",
            output_schema=INTENT_SCHEMA,
            system_prompt=AGENT_PROMPTS["orchestrator"],
        )

        # Default to all platforms when none detected
        if not intent["target_platforms"]:
            intent["target_platforms"] = ["linkedin", "twitter", "instagram"]

        platforms_str = ", ".join(intent["target_platforms"])
        await ws_manager.send_agent_thinking(
            conversation_id,
            "orchestrator",
            f"Intent: {intent['primary_intent']} | Platforms: {platforms_str} | Agents: {', '.join(intent['required_agents'])}",
            0.2,
        )

        # ── Step 2: Determine waves ───────────────────────────────
        waves = _WAVE_CONFIG.get(
            intent["primary_intent"],
            {"wave1": intent["required_agents"][:3], "wave2": []},
        )

        base_context = {
            "message": message_content,
            "entities": intent["key_entities"],
            "intent": intent["primary_intent"],
            "platforms": intent["target_platforms"],
            "previous_results": {},
        }

        all_results: dict[str, str] = {}
        all_tokens: dict[str, int] = {}

        # ── Wave 1: Context gathering (parallel) ──────────────────
        if waves["wave1"]:
            for agent_name in waves["wave1"]:
                await ws_manager.send_agent_handoff(
                    conversation_id, "orchestrator", agent_name, intent["task_description"]
                )

            w1_results = await asyncio.gather(
                *[
                    _execute_agent(
                        agent_name=name,
                        task=intent["task_description"],
                        context=base_context,
                        conversation_id=conversation_id,
                        ws_manager=ws_manager,
                        db=db,
                    )
                    for name in waves["wave1"]
                ]
            )

            for name, (result, tokens) in zip(waves["wave1"], w1_results):
                all_results[name] = result
                all_tokens[name] = tokens

        # ── Wave 2: Creation + review (parallel, with Wave 1 context) ─
        if waves["wave2"]:
            wave2_context = {**base_context, "previous_results": all_results}

            for agent_name in waves["wave2"]:
                await ws_manager.send_agent_handoff(
                    conversation_id, "orchestrator", agent_name, intent["task_description"]
                )

            w2_results = await asyncio.gather(
                *[
                    _execute_agent(
                        agent_name=name,
                        task=intent["task_description"],
                        context=wave2_context,
                        conversation_id=conversation_id,
                        ws_manager=ws_manager,
                        db=db,
                    )
                    for name in waves["wave2"]
                ]
            )

            for name, (result, tokens) in zip(waves["wave2"], w2_results):
                all_results[name] = result
                all_tokens[name] = tokens

        # ── Record agent traces ───────────────────────────────────
        for agent_name in all_results:
            agent_trace = await trace_service.start_trace(
                db=db,
                agent_name=agent_name,
                task_type=intent["task_description"][:50],
                input_data={"task": intent["task_description"]},
            )
            await trace_service.complete_trace(
                db=db,
                trace=agent_trace,
                output_data={"result_preview": all_results[agent_name][:200]},
                tokens_used=all_tokens.get(agent_name, 0),
            )

        # ── Step 3: Synthesize final response ─────────────────────
        await ws_manager.send_agent_thinking(
            conversation_id, "orchestrator", "Synthesizing response...", 0.9
        )

        if all_results:
            synthesis_prompt = f"""Based on the following agent outputs, synthesize a comprehensive response to the user's request.

User Request: {message_content}
Target Platforms: {platforms_str}
Intent: {intent['primary_intent']}

Agent Outputs:
{_format_agent_results(all_results)}

Provide a well-structured response that:
- Includes platform-specific content for each requested platform
- References engagement data and best practices from the Analyst
- Incorporates brand guidelines from the Memory agent
- Notes any compliance feedback from the Advisor
- Includes recommended posting schedule if applicable"""

            response = await llm.complete(
                prompt=synthesis_prompt,
                system_prompt=AGENT_PROMPTS["orchestrator"],
            )
        else:
            response = await llm.complete(
                prompt=message_content,
                system_prompt=AGENT_PROMPTS["orchestrator"],
            )

        # ── Save document for content intents ─────────────────────
        if intent["primary_intent"] in ("content_creation", "content_strategy") and all_results:
            doc_service = get_document_service()
            topic = intent["key_entities"][0] if intent["key_entities"] else "Social Media Content"

            doc = await doc_service.create_document(
                db=db,
                title=f"Social Post: {intent['task_description'][:60]}",
                doc_type="social_post",
                content=response,
                metadata={
                    "topic": topic,
                    "platforms": intent["target_platforms"],
                    "intent": intent["primary_intent"],
                    "conversation_id": conversation_id,
                    "generated_via": "chat",
                },
            )

            await ws_manager.send_document_generated(
                conversation_id, doc.id, "social_post", doc.title
            )

        # ── Complete orchestrator trace ────────────────────────────
        duration_ms = int((time.time() - start_time) * 1000)
        await trace_service.complete_trace(
            db=db,
            trace=trace,
            output_data={"response": response[:500], "agents_used": list(all_results.keys())},
            tokens_used=llm.last_tokens_used,
        )

        await ws_manager.send_agent_completed(
            conversation_id,
            "orchestrator",
            f"Completed with {len(all_results)} agents",
            duration_ms,
        )

        return response

    except Exception as e:
        await trace_service.fail_trace(db=db, trace=trace, error=str(e))
        raise


async def _execute_agent(
    agent_name: str,
    task: str,
    context: dict,
    conversation_id: str,
    ws_manager: ConnectionManager,
    db: AsyncSession,
) -> tuple[str, int]:
    """Execute a specific agent and return its result with token usage."""
    start_time = time.time()

    await ws_manager.send_agent_started(conversation_id, agent_name, task[:100])

    # Notify which tools/MCP servers this agent will use
    _tool_info = {
        "researcher": [("search_web", "tool"), ("search_news", "tool"), ("search_trends", "tool"), ("fetch_mcp", "mcp")],
        "memory": [("get_brand_guidelines", "tool"), ("get_past_posts", "tool"), ("search_knowledge_base", "tool")],
        "analyst": [("calculate_engagement_metrics", "tool"), ("recommend_posting_schedule", "tool")],
        "scribe": [("filesystem_mcp", "mcp")],
    }
    for tool_name, tool_type in _tool_info.get(agent_name, []):
        await ws_manager.send_agent_tool_call(conversation_id, agent_name, tool_name, tool_type)

    try:
        if agent_name == "strategist":
            result, tokens_used = await run_strategist(task, context)
        elif agent_name == "researcher":
            result, tokens_used = await run_researcher(task, context)
        elif agent_name == "analyst":
            result, tokens_used = await run_analyst(task, context)
        elif agent_name == "scribe":
            result, tokens_used = await run_scribe(task, context)
        elif agent_name == "advisor":
            result, tokens_used = await run_advisor(task, context)
        elif agent_name == "memory":
            result, tokens_used = await run_memory(task, context)
        else:
            result = f"Unknown agent: {agent_name}"
            tokens_used = 0

        duration_ms = int((time.time() - start_time) * 1000)

        await ws_manager.send_agent_completed(
            conversation_id, agent_name, result[:100], duration_ms
        )

        return result, tokens_used

    except Exception as e:
        await ws_manager.send_agent_completed(conversation_id, agent_name, f"Error: {str(e)}", 0)
        return f"Error from {agent_name}: {str(e)}", 0


def _format_agent_results(results: dict) -> str:
    """Format agent results for synthesis."""
    formatted = []
    for agent, result in results.items():
        formatted.append(f"=== {agent.upper()} ===\n{result}\n")
    return "\n".join(formatted)


async def generate_social_content(
    topic: str,
    platforms: list[str],
    content_type: str = "post",
    additional_context: Optional[str] = None,
    db: AsyncSession = None,
):
    """Generate social media content directly (API endpoint).

    Args:
        topic: The topic or announcement to create content about.
        platforms: Target platforms (linkedin, twitter, instagram).
        content_type: Type of content — post, thread, campaign, calendar.
        additional_context: Extra context or instructions.
        db: Database session.
    """
    doc_service = get_document_service()
    llm = get_llm_service()

    scope = f"Create {content_type} about '{topic}' for {', '.join(platforms)}"
    if additional_context:
        scope += f". Additional context: {additional_context}"

    context = {"message": scope, "platforms": platforms}

    # Wave 1: Gather context
    research_result, _ = await run_researcher(scope, context)
    memory_result, _ = await run_memory(scope, context)
    strategy_result, _ = await run_strategist(scope, {**context, "previous_results": {"researcher": research_result, "memory": memory_result}})

    # Wave 2: Generate + review
    scribe_result, _ = await run_scribe(scope, {
        **context,
        "previous_results": {
            "researcher": research_result,
            "memory": memory_result,
            "strategist": strategy_result,
        },
    })
    advisor_result, _ = await run_advisor(scope, {
        **context,
        "previous_results": {"scribe": scribe_result},
    })

    # Synthesize
    content = await llm.complete(
        prompt=f"""Combine these outputs into final social media content:

Topic: {topic}
Platforms: {', '.join(platforms)}

Research: {research_result[:500]}
Strategy: {strategy_result[:500]}
Draft Content: {scribe_result}
Compliance Review: {advisor_result[:500]}

Produce the final platform-specific posts ready for publishing.""",
        system_prompt=AGENT_PROMPTS["orchestrator"],
    )

    # Save document
    doc = await doc_service.create_document(
        db=db,
        title=f"Social Post: {topic[:60]}",
        doc_type="social_post",
        content=content,
        metadata={
            "topic": topic,
            "platforms": platforms,
            "content_type": content_type,
            "generated_via": "api",
        },
    )

    return doc
