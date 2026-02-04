"""Orchestrator Agent - Coordinates all other agents using MAF workflow patterns."""

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
                "enum": ["proposal", "research", "analysis", "document", "question", "other"],
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
        "required": ["primary_intent", "required_agents", "key_entities", "task_description"],
        "additionalProperties": False,
    },
}


async def process_message(
    conversation_id: str,
    message_content: str,
    message_metadata: dict,
    ws_manager: ConnectionManager,
    db: AsyncSession,
) -> str:
    """
    Process a user message through the orchestrator.
    
    This is the main entry point that:
    1. Analyzes intent
    2. Routes to appropriate agents
    3. Synthesizes the response
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
        # 1. Analyze intent using structured output
        await ws_manager.send_agent_thinking(conversation_id, "orchestrator", "Understanding your request...", 0.1)
        
        intent = await llm.structured_output(
            prompt=f"""Analyze this user request and determine how to handle it:

User Request: {message_content}

Determine:
1. The primary intent (proposal, research, analysis, document, question, other)
2. Which specialist agents should be involved:
   - For PROPOSALS: Include strategist, researcher, analyst, memory, scribe (all 5)
   - For RESEARCH/BRIEFINGS: Include researcher, memory, advisor
   - For ANALYSIS: Include analyst, memory
   - For DOCUMENTS: Include scribe, advisor
   - For QUESTIONS: Include memory (for knowledge queries) or minimal agents
3. Key entities mentioned (companies, industries, topics)
4. A clear task description""",
            output_schema=INTENT_SCHEMA,
            system_prompt=AGENT_PROMPTS["orchestrator"],
        )
        
        await ws_manager.send_agent_thinking(
            conversation_id, 
            "orchestrator", 
            f"Intent: {intent['primary_intent']}, involving {', '.join(intent['required_agents'])}",
            0.2
        )
        
        # 2. Execute agents in PARALLEL for speed
        # For proposals, use all recommended agents to showcase full capabilities
        # For other intents, cap at 3 for speed
        if intent["primary_intent"] == "proposal":
            # Ensure all key agents are included for proposals (demo showcase)
            proposal_agents = ["strategist", "researcher", "analyst", "memory", "scribe"]
            agents_to_run = list(dict.fromkeys(intent["required_agents"] + proposal_agents))[:6]
        elif intent["primary_intent"] == "research":
            # Research should include memory for past engagement context
            research_agents = ["researcher", "memory", "advisor"]
            agents_to_run = list(dict.fromkeys(intent["required_agents"] + research_agents))[:4]
        else:
            agents_to_run = intent["required_agents"][:3]  # Cap at 3 for simple queries
        
        # Send all handoff notifications first
        for agent_name in agents_to_run:
            await ws_manager.send_agent_handoff(
                conversation_id, 
                "orchestrator", 
                agent_name,
                intent["task_description"]
            )
        
        # Run all agents in parallel
        async def run_agent(agent_name: str) -> tuple[str, str, int]:
            result, tokens = await _execute_agent(
                agent_name=agent_name,
                task=intent["task_description"],
                context={
                    "message": message_content,
                    "entities": intent["key_entities"],
                    "intent": intent["primary_intent"],
                    "previous_results": {},  # No sequential dependency
                },
                conversation_id=conversation_id,
                ws_manager=ws_manager,
                db=db,
            )
            return agent_name, result, tokens
        
        # Execute all agents concurrently
        results = await asyncio.gather(*[run_agent(name) for name in agents_to_run])
        agent_results = {name: result for name, result, _ in results}
        agent_tokens = {name: tokens for name, _, tokens in results}
        
        # Create traces for all agents after parallel execution
        for agent_name, result, tokens in results:
            agent_trace = await trace_service.start_trace(
                db=db,
                agent_name=agent_name,
                task_type=intent["task_description"][:50],
                input_data={"task": intent["task_description"]},
            )
            await trace_service.complete_trace(
                db=db,
                trace=agent_trace,
                output_data={"result_preview": result[:200]},
                tokens_used=tokens,
            )
        
        # 3. Synthesize final response
        await ws_manager.send_agent_thinking(conversation_id, "orchestrator", "Synthesizing response...", 0.9)
        
        if agent_results:
            synthesis_prompt = f"""Based on the following agent outputs, synthesize a comprehensive response to the user's request.

User Request: {message_content}

Agent Outputs:
{_format_agent_results(agent_results)}

Provide a well-structured, professional response that addresses the user's needs."""
            
            response = await llm.complete(
                prompt=synthesis_prompt,
                system_prompt=AGENT_PROMPTS["orchestrator"],
            )
        else:
            # Direct response for simple questions
            response = await llm.complete(
                prompt=message_content,
                system_prompt=AGENT_PROMPTS["orchestrator"],
            )
        
        # If this was a proposal request, save it as a Document
        if intent["primary_intent"] == "proposal" and agent_results:
            doc_service = get_document_service()
            # Extract client name from entities or message
            client_name = intent["key_entities"][0] if intent["key_entities"] else "Client"
            
            doc = await doc_service.create_document(
                db=db,
                title=f"Proposal: {intent['task_description'][:50]}",
                doc_type="proposal",
                content=response,
                metadata={
                    "client_name": client_name,
                    "conversation_id": conversation_id,
                    "generated_via": "chat",
                }
            )
            
            # Notify about document generation
            await ws_manager.send_document_generated(
                conversation_id,
                doc.id,
                "proposal",
                doc.title
            )
        
        # Complete trace
        duration_ms = int((time.time() - start_time) * 1000)
        await trace_service.complete_trace(
            db=db,
            trace=trace,
            output_data={"response": response[:500], "agents_used": list(agent_results.keys())},
            tokens_used=llm.last_tokens_used,
        )
        
        await ws_manager.send_agent_completed(
            conversation_id, 
            "orchestrator", 
            f"Completed with {len(agent_results)} agents",
            duration_ms
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
    
    try:
        # Route to appropriate agent - all now return (result, tokens_used)
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
            conversation_id, 
            agent_name, 
            result[:100],
            duration_ms
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


async def generate_proposal(
    client_name: str,
    client_industry: str,
    engagement_type: str,
    scope_description: str,
    budget_range: Optional[str] = None,
    timeline: Optional[str] = None,
    additional_context: Optional[str] = None,
    db: AsyncSession = None,
):
    """Generate a full proposal document."""
    doc_service = get_document_service()
    llm = get_llm_service()
    
    # Gather context - agents now return (result, tokens_used)
    research_context, _ = await run_researcher(
        f"Research {client_name} in {client_industry}",
        {"message": scope_description}
    )
    
    memory_context, _ = await run_memory(
        f"Find similar engagements for {engagement_type} in {client_industry}",
        {"message": scope_description}
    )
    
    # Generate proposal via strategist
    proposal_content, _ = await run_strategist(
        f"Generate a proposal for {client_name}",
        {
            "message": scope_description,
            "client_name": client_name,
            "client_industry": client_industry,
            "engagement_type": engagement_type,
            "budget_range": budget_range,
            "timeline": timeline,
            "additional_context": additional_context,
            "research": research_context,
            "similar_engagements": memory_context,
        }
    )
    
    # Create document
    doc = await doc_service.create_document(
        db=db,
        title=f"Proposal: {engagement_type} for {client_name}",
        doc_type="proposal",
        content=proposal_content,
        metadata={
            "client_name": client_name,
            "client_industry": client_industry,
            "engagement_type": engagement_type,
        }
    )
    
    return doc
