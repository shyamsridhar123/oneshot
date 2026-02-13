"""MAF Middleware for citation capture and tracing.

Provides utilities that capture:
- URLs embedded in agent / tool output text
- Knowledge-source references from internal tools (brand guidelines, past posts, etc.)
- Tool call metadata from MAF response objects
"""

import re
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Tools whose outputs should be treated as citation sources
_URL_SOURCE_TOOLS = frozenset({
    "search_web", "search_news", "search_trends",
    "search_competitor_content", "analyze_hashtags",
})

_KNOWLEDGE_SOURCE_TOOLS = frozenset({
    "search_knowledge_base",
    "get_brand_guidelines", "get_past_posts",
    "get_content_calendar",
})

_ALL_SOURCE_TOOLS = _URL_SOURCE_TOOLS | _KNOWLEDGE_SOURCE_TOOLS

# Human-readable labels for knowledge tools
_KNOWLEDGE_LABELS: dict[str, str] = {
    "get_brand_guidelines": "Brand Guidelines",
    "get_past_posts": "Past Post Performance",
    "get_content_calendar": "Content Calendar",
    "search_knowledge_base": "Knowledge Base",
}

# Regex to extract URLs from any text
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


def extract_citations_from_text(text: str) -> list[dict]:
    """Extract citation-like references from text.

    Captures:
    - All bare URLs found anywhere in the text
    - "Source: <non-URL label>" patterns as named sources
    """
    if not text:
        return []

    citations: list[dict] = []
    seen: set[str] = set()

    # 1) All URLs in the text
    for url in _URL_RE.findall(text):
        if url not in seen:
            seen.add(url)
            citations.append({"url": url, "type": "url", "source_tool": "text_extraction"})

    # 2) "Source: <label>" where label is NOT a URL (those were caught above)
    for match in re.finditer(r'Source:\s*([^\n]+)', text):
        label = match.group(1).strip()
        if label and not label.startswith("http") and label != "N/A":
            key = label[:80]
            if key not in seen:
                seen.add(key)
                citations.append({
                    "source_tool": "text_extraction",
                    "type": "knowledge",
                    "preview": label[:200],
                })

    return citations


def make_knowledge_citation(tool_name: str, preview: str = "") -> dict:
    """Create a knowledge-type citation for an internal data tool."""
    return {
        "source_tool": tool_name,
        "type": "knowledge",
        "preview": _KNOWLEDGE_LABELS.get(tool_name, tool_name) + (f": {preview[:120]}" if preview else ""),
    }


def extract_tool_calls_and_citations(response) -> tuple[list[dict], list[dict]]:
    """Extract tool call info AND citations from a MAF agent response object.

    Returns (tool_calls, citations) extracted from the response message history.
    """
    tool_calls: list[dict] = []
    citations: list[dict] = []
    seen_urls: set[str] = set()
    seen_tools: set[str] = set()

    try:
        if not hasattr(response, "messages"):
            return tool_calls, citations

        for msg in response.messages:
            if not hasattr(msg, "contents"):
                continue
            for content in msg.contents:
                # Function call
                if hasattr(content, "name") and hasattr(content, "arguments"):
                    tool_calls.append({
                        "tool_name": content.name,
                        "arguments": str(content.arguments)[:500] if content.arguments else "",
                    })

                # Function result — extract citations from output
                if hasattr(content, "call_id") and hasattr(content, "output"):
                    name = getattr(content, "name", "unknown")
                    output = str(content.output) if content.output else ""

                    tool_calls.append({
                        "tool_name": name,
                        "result_preview": output[:500],
                    })

                    # URL citations from URL-source tools
                    if name in _URL_SOURCE_TOOLS:
                        for url in _extract_urls(output):
                            if url not in seen_urls:
                                seen_urls.add(url)
                                citations.append({
                                    "url": url,
                                    "source_tool": name,
                                    "type": "url",
                                })

                    # Knowledge citations from internal tools
                    if name in _KNOWLEDGE_SOURCE_TOOLS and name not in seen_tools:
                        seen_tools.add(name)
                        citations.append(make_knowledge_citation(name, output[:120]))

    except Exception:
        pass

    return tool_calls, citations


def build_agent_trace_data(
    agent_name: str,
    response_text: str,
    tokens_used: int,
    duration_ms: int,
    response=None,
) -> dict:
    """Build complete trace data dict for an agent run.

    Combines text-based citation extraction with MAF response object inspection.
    """
    citations = extract_citations_from_text(response_text)
    tool_calls: list[dict] = []

    if response is not None:
        resp_tool_calls, resp_citations = extract_tool_calls_and_citations(response)
        tool_calls = resp_tool_calls
        # Merge response citations, dedup by url or preview
        existing = {c.get("url") or c.get("preview", "") for c in citations}
        for c in resp_citations:
            key = c.get("url") or c.get("preview", "")
            if key and key not in existing:
                existing.add(key)
                citations.append(c)

    return {
        "result_preview": response_text[:500],
        "citations": citations,
        "tool_calls": tool_calls,
        "duration_ms": duration_ms,
        "tokens_used": tokens_used,
        "agent_name": agent_name,
    }
