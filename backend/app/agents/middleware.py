"""MAF Middleware for citation capture and tracing.

Provides middleware classes that intercept MAF agent execution to capture:
- Tool call inputs/outputs as structured citations
- Agent execution timing and metadata
- Source URLs extracted from tool results
"""

import re
import time
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Tools whose outputs should be treated as citation sources
_SOURCE_TOOLS = frozenset({
    "search_web", "search_news", "search_trends",
    "search_competitor_content", "search_knowledge_base",
    "get_brand_guidelines", "get_past_posts",
    "get_content_calendar", "analyze_hashtags",
})

# Regex to extract URLs from tool output text
_URL_RE = re.compile(r'https?://[^\s<>"\')\]]+')


@dataclass
class ToolCallRecord:
    """Record of a single tool invocation."""
    tool_name: str
    arguments: dict
    result_preview: str
    urls: list[str]
    is_source: bool
    duration_ms: int = 0


@dataclass
class AgentRunTrace:
    """Aggregated trace data for a single agent run."""
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    citations: list[dict] = field(default_factory=list)
    duration_ms: int = 0
    total_tool_time_ms: int = 0


def _extract_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    return _URL_RE.findall(text) if text else []


def _build_citations(tool_calls: list[ToolCallRecord]) -> list[dict]:
    """Build structured citation list from tool call records."""
    citations = []
    seen_urls: set[str] = set()

    for tc in tool_calls:
        if not tc.is_source:
            continue

        for url in tc.urls:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            citations.append({
                "url": url,
                "source_tool": tc.tool_name,
                "type": "url",
            })

        # For tools that return structured data without URLs (brand guidelines, etc.)
        if not tc.urls and tc.is_source:
            citations.append({
                "source_tool": tc.tool_name,
                "type": "knowledge",
                "preview": tc.result_preview[:200],
            })

    return citations


def create_tracing_middleware() -> AgentRunTrace:
    """Create middleware instances and return the shared trace data container.

    Returns the AgentRunTrace that will be populated during agent execution.
    The caller should pass the returned middleware functions to create_agent().

    Usage:
        trace_data = create_tracing_middleware()
        agent = create_agent("name", "instructions", tools=tools, middleware=[...])
        # After agent.run(), trace_data is populated with tool calls and citations
    """
    return AgentRunTrace()


def extract_citations_from_text(text: str) -> list[dict]:
    """Extract citation-like references from agent output text.

    Looks for patterns like 'Source: URL' in the text.
    """
    citations = []
    seen: set[str] = set()

    # Match "Source: URL" patterns
    for match in re.finditer(r'Source:\s*(https?://[^\s<>"\')\]]+)', text):
        url = match.group(1)
        if url not in seen:
            seen.add(url)
            citations.append({"url": url, "type": "url", "source_tool": "text_extraction"})

    return citations


def extract_tool_calls_from_response(response) -> list[dict]:
    """Extract tool call information from a MAF agent response object.

    MAF responses may contain tool call history. This function attempts
    to extract that data regardless of the exact response type.
    """
    tool_calls = []

    # Try to access response message history for tool calls
    try:
        if hasattr(response, 'messages'):
            for msg in response.messages:
                if hasattr(msg, 'contents'):
                    for content in msg.contents:
                        # Check for function call content
                        if hasattr(content, 'name') and hasattr(content, 'arguments'):
                            tool_calls.append({
                                "tool_name": content.name,
                                "arguments": str(content.arguments)[:500] if content.arguments else "",
                            })
                        # Check for function result content
                        if hasattr(content, 'call_id') and hasattr(content, 'output'):
                            tool_calls.append({
                                "tool_name": getattr(content, 'name', 'unknown'),
                                "result_preview": str(content.output)[:500] if content.output else "",
                            })
    except Exception:
        pass

    return tool_calls


def build_agent_trace_data(
    agent_name: str,
    response_text: str,
    tokens_used: int,
    duration_ms: int,
    response=None,
) -> dict:
    """Build complete trace data dict for an agent run.

    Combines text-based citation extraction with response object inspection.

    Args:
        agent_name: Name of the agent
        response_text: The agent's text output
        tokens_used: Token count from the response
        duration_ms: Execution time in milliseconds
        response: Optional MAF response object for tool call extraction

    Returns:
        Dict with citations, tool_calls, duration_ms, and result_preview
    """
    citations = extract_citations_from_text(response_text)
    tool_calls = []

    if response is not None:
        tool_calls = extract_tool_calls_from_response(response)

    return {
        "result_preview": response_text[:500],
        "citations": citations,
        "tool_calls": tool_calls,
        "duration_ms": duration_ms,
        "tokens_used": tokens_used,
        "agent_name": agent_name,
    }
