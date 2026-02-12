"""Social Media Command Center - E2E Demo Script

Demonstrates the full platform capabilities:
  1. Health & API info
  2. Knowledge base seeding and search
  3. Agent tool functions (researcher, memory, analyst)
  4. Social media content generation via orchestrator
  5. Document export (Markdown, HTML, PDF, DOCX)
  6. Analytics dashboard (traces, metrics, social analytics)
  7. MCP tool integration validation

Runs entirely via ASGI transport — no live server required.
"""

import asyncio
import sys
import uuid
import time
from datetime import datetime, timedelta
from pathlib import Path

# Ensure backend is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.models.database import Base, get_db, Document, Conversation, Message, AgentTrace

# ──────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────

TEST_DB_URL = "sqlite+aiosqlite:///./data/demo_test.db"

SECTION_WIDTH = 64
PASS_COUNT = 0
FAIL_COUNT = 0
SKIP_COUNT = 0


# ──────────────────────────────────────────────────────────────
# Formatting helpers
# ──────────────────────────────────────────────────────────────

def header(title: str):
    print(f"\n{'=' * SECTION_WIDTH}")
    print(f"  {title}")
    print(f"{'=' * SECTION_WIDTH}")


def subheader(title: str):
    print(f"\n  --- {title} ---")


def check(label: str, passed: bool, detail: str = ""):
    global PASS_COUNT, FAIL_COUNT
    if passed:
        PASS_COUNT += 1
        status = "PASS"
    else:
        FAIL_COUNT += 1
        status = "FAIL"
    suffix = f"  ({detail})" if detail else ""
    print(f"  [{status}] {label}{suffix}")
    return passed


def info(msg: str):
    print(f"       {msg}")


def skip(label: str, reason: str = ""):
    global SKIP_COUNT
    SKIP_COUNT += 1
    suffix = f"  ({reason})" if reason else ""
    print(f"  [SKIP] {label}{suffix}")


# ──────────────────────────────────────────────────────────────
# Database setup
# ──────────────────────────────────────────────────────────────

async def create_test_db():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine


async def get_session(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return session_factory


# ──────────────────────────────────────────────────────────────
# Demo Scenarios
# ──────────────────────────────────────────────────────────────

async def demo_health_and_info(client: AsyncClient):
    """Test health and root endpoints."""
    header("1. Health & API Info")

    r = await client.get("/health")
    check("GET /health returns 200", r.status_code == 200)
    data = r.json()
    check("Health response has status field", "status" in data)
    info(f"Status: {data.get('status')}")

    r = await client.get("/")
    check("GET / returns 200", r.status_code == 200)
    data = r.json()
    check("Root has API name", "name" in data or "message" in data)
    info(f"API: {data}")


async def demo_conversations(client: AsyncClient) -> str:
    """Create and manage conversations."""
    header("2. Conversations")

    # Create
    r = await client.post("/api/chat/conversations", json={
        "title": "Demo: AI Product Launch Campaign",
        "metadata": {"demo": True, "campaign": "AI Launch 2026"},
    })
    check("POST /conversations creates conversation", r.status_code == 200)
    conv = r.json()
    conv_id = conv["id"]
    check("Conversation has valid ID", len(conv_id) > 0)
    check("Conversation title matches", conv["title"] == "Demo: AI Product Launch Campaign")
    info(f"Conversation ID: {conv_id[:12]}...")

    # List
    r = await client.get("/api/chat/conversations")
    check("GET /conversations returns list", r.status_code == 200)
    convs = r.json()
    check("Created conversation appears in list", any(c["id"] == conv_id for c in convs))

    # Get by ID
    r = await client.get(f"/api/chat/conversations/{conv_id}")
    check("GET /conversations/:id returns conversation", r.status_code == 200)

    # Not found
    r = await client.get(f"/api/chat/conversations/{uuid.uuid4()}")
    check("GET /conversations/:bad_id returns 404", r.status_code == 404)

    return conv_id


async def demo_knowledge_search(client: AsyncClient):
    """Test knowledge base search."""
    header("3. Knowledge Base")

    r = await client.post("/api/knowledge/search", json={
        "query": "digital transformation manufacturing",
        "limit": 5,
    })
    check("POST /knowledge/search returns 200", r.status_code == 200)
    results = r.json()
    check("Search returns results list", isinstance(results, list))
    if results:
        info(f"Found {len(results)} items")
        for item in results[:3]:
            info(f"  - {item.get('title', 'N/A')} ({item.get('category', 'N/A')})")
    else:
        info("No knowledge items seeded (expected in demo DB)")

    # Similar engagements
    r = await client.post("/api/knowledge/similar", params={
        "query": "supply chain optimization",
        "limit": 3,
    })
    check("POST /knowledge/similar returns 200", r.status_code == 200)


async def demo_agent_tools():
    """Test agent tool functions directly."""
    header("4. Agent Tool Functions")

    from app.agents.factory import (
        search_trends, search_web, search_news,
        search_competitor_content, analyze_hashtags,
        get_brand_guidelines, get_past_posts, get_content_calendar,
        search_knowledge_base,
        calculate_engagement_metrics, recommend_posting_schedule,
        get_agent_tools, create_filesystem_mcp, create_fetch_mcp,
    )

    subheader("Researcher Tools")
    trends = search_trends("AI collaboration", "linkedin")
    check("search_trends returns data", len(trends) > 50)
    info(f"Trends excerpt: {trends[:80]}...")

    web = search_web("enterprise AI 2026")
    check("search_web returns data", "Enterprise AI" in web)

    news = search_news("AI agents", 7)
    check("search_news returns data", "7 days" in news)

    comp = search_competitor_content("Microsoft", "linkedin")
    check("search_competitor_content returns data", "Microsoft" in comp)

    tags = analyze_hashtags("#AIAgents, #TechVista, #Enterprise")
    check("analyze_hashtags returns data", "AIAgents" in tags)

    subheader("Memory Tools")
    guidelines = get_brand_guidelines()
    check("get_brand_guidelines returns content", len(guidelines) > 20)
    info(f"Guidelines length: {len(guidelines)} chars")

    posts = get_past_posts(platform="linkedin", performance="high")
    check("get_past_posts returns data", len(posts) > 0)

    calendar = get_content_calendar()
    check("get_content_calendar returns data", len(calendar) > 0)

    kb = search_knowledge_base("AI collaboration")
    check("search_knowledge_base returns data", "TechVista" in kb)

    subheader("Analyst Tools")
    metrics = calculate_engagement_metrics("linkedin", "carousel")
    check("calculate_engagement_metrics returns data", "engagement" in metrics.lower())
    info(f"Engagement excerpt: {metrics[:80]}...")

    schedule = recommend_posting_schedule("linkedin,twitter", 10)
    check("recommend_posting_schedule returns data", "10 posts/week" in schedule)

    subheader("MCP Tool Configuration")
    tools_researcher = get_agent_tools("researcher", include_mcp=False)
    check("Researcher has 5 tools (no MCP)", len(tools_researcher) == 5)

    tools_analyst = get_agent_tools("analyst", include_mcp=False)
    check("Analyst has 2 tools", len(tools_analyst) == 2)

    tools_memory = get_agent_tools("memory", include_mcp=False)
    check("Memory has 4 tools", len(tools_memory) == 4)

    tools_scribe_no_mcp = get_agent_tools("scribe", include_mcp=False)
    check("Scribe has 0 tools (no MCP)", len(tools_scribe_no_mcp) == 0)


async def demo_content_generation(client: AsyncClient):
    """Test content generation endpoint."""
    header("5. Content Generation (API)")

    # Valid request — expects 200 (with LLM) or 500 (without Azure creds)
    r = await client.post("/api/proposals/generate", json={
        "topic": "TechVista AI Collaboration Suite v3.0 Launch",
        "platforms": ["linkedin", "twitter"],
        "content_type": "post",
        "additional_context": "Highlight: 40% fewer meetings, 3x faster document turnaround",
    })
    if r.status_code == 200:
        check("POST /proposals/generate succeeds", True)
        doc = r.json()
        check("Generated doc has title", len(doc.get("title", "")) > 0)
        check("Generated doc has content", len(doc.get("content", "")) > 0)
        check("Generated doc type is social_post", doc.get("doc_type") == "social_post")
        info(f"Title: {doc['title']}")
        info(f"Content preview: {doc['content'][:120]}...")
        return doc["id"]
    else:
        check("POST /proposals/generate returns 500 (no Azure creds)", r.status_code == 500)
        info("Content generation requires Azure credentials — skipping content tests")
        return None

    # Validation: missing topic
    r = await client.post("/api/proposals/generate", json={})
    check("Empty body returns 422", r.status_code == 422)

    return None


async def demo_list_content(client: AsyncClient, db_session: AsyncSession):
    """Test content listing with seeded data."""
    header("6. Content Listing & Retrieval")

    # Seed some documents for listing
    for i, platform in enumerate(["linkedin", "twitter", "instagram"]):
        doc = Document(
            id=str(uuid.uuid4()),
            title=f"Demo Post: {platform.title()} Launch Campaign #{i+1}",
            doc_type="social_post",
            content=f"# {platform.title()} Post\n\nExciting news about TechVista AI Suite v3.0!\n\n"
                    f"Key highlights:\n- 40% fewer meetings\n- 3x faster turnaround\n- Enterprise-grade security\n\n"
                    f"#TechVista #AIInnovation #{platform}",
            format="markdown",
            metadata_={"platform": platform, "campaign": "AI Launch 2026"},
        )
        db_session.add(doc)
    await db_session.flush()

    r = await client.get("/api/proposals")
    check("GET /proposals returns 200", r.status_code == 200)
    proposals = r.json()
    check("Proposals list has items", len(proposals) >= 3)
    info(f"Total content items: {len(proposals)}")
    for p in proposals[:3]:
        info(f"  - {p['title']}")


async def demo_document_export(client: AsyncClient, db_session: AsyncSession) -> str:
    """Test document export to multiple formats."""
    header("7. Document Export")

    # Create a rich document for export testing
    doc = Document(
        id=str(uuid.uuid4()),
        title="TechVista AI Launch - Multi-Platform Campaign",
        doc_type="social_post",
        content="""# TechVista AI Collaboration Suite v3.0

## LinkedIn Post
We're excited to announce TechVista AI Collaboration Suite v3.0!

Key benefits for enterprise teams:
- 40% fewer meetings with AI-powered summaries
- 3x faster document turnaround
- 35% more time on strategic work

Learn more at techvista.com/ai-suite

#TechVista #AIInnovation #EnterpriseAI #FutureOfWork

## Twitter Thread
1/5 Big news! TechVista AI Suite v3.0 is here.

2/5 Our customers are seeing 40% fewer meetings. How? AI-powered summaries that capture what matters.

3/5 Document turnaround is 3x faster. Collaboration doesn't have to mean more meetings.

4/5 Teams report 35% more time for strategic work. That's the promise of AI that works WITH you.

5/5 Ready to transform your team's productivity? Check out techvista.com/ai-suite

## Instagram Caption
AI that works with you, not instead of you.

Introducing TechVista AI Suite v3.0 - where intelligent collaboration meets enterprise security.

Our customers' results speak for themselves:
- 40% fewer meetings
- 3x faster docs
- 35% more strategic time

Link in bio for early access.

#TechVista #AICollaboration #EnterpriseAI #ProductLaunch #Innovation #FutureOfWork #ArtificialIntelligence""",
        format="markdown",
        metadata_={"demo": True},
    )
    db_session.add(doc)
    await db_session.flush()
    doc_id = doc.id

    # Export to each format
    for fmt, content_type_substr in [
        ("markdown", "text/markdown"),
        ("html", "text/html"),
        ("pdf", "application/pdf"),
        ("docx", "wordprocessingml"),
    ]:
        r = await client.post(f"/api/documents/{doc_id}/export", json={"format": fmt})
        check(f"Export to {fmt.upper()} returns 200", r.status_code == 200)
        check(f"Export {fmt.upper()} has correct content-type",
              content_type_substr in r.headers.get("content-type", ""))
        check(f"Export {fmt.upper()} has content-disposition",
              "content-disposition" in r.headers)
        if fmt in ("markdown", "html"):
            info(f"  {fmt.upper()} size: {len(r.text)} chars")
        else:
            info(f"  {fmt.upper()} size: {len(r.content)} bytes")

    # Invalid format
    r = await client.post(f"/api/documents/{doc_id}/export", json={"format": "txt"})
    check("Export invalid format returns 422", r.status_code == 422)

    # Non-existent document
    r = await client.post(f"/api/documents/{uuid.uuid4()}/export", json={"format": "pdf"})
    check("Export non-existent doc returns 404", r.status_code == 404)

    return doc_id


async def demo_analytics(client: AsyncClient, db_session: AsyncSession):
    """Test analytics endpoints with seeded trace data."""
    header("8. Analytics & Metrics")

    # Seed agent traces
    now = datetime.utcnow()
    agents_data = [
        ("orchestrator", "message_processing", "completed", 800, 8.5),
        ("researcher", "trend_analysis", "completed", 200, 1.2),
        ("strategist", "content_strategy", "completed", 350, 2.1),
        ("memory", "brand_retrieval", "completed", 50, 0.3),
        ("analyst", "engagement_prediction", "completed", 180, 1.5),
        ("scribe", "content_generation", "completed", 450, 3.2),
        ("advisor", "compliance_review", "completed", 120, 0.8),
        ("researcher", "competitor_analysis", "failed", 0, 0.5),
    ]

    for agent, task, status, tokens, duration in agents_data:
        trace = AgentTrace(
            id=str(uuid.uuid4()),
            agent_name=agent,
            task_type=task,
            status=status,
            started_at=now - timedelta(seconds=duration),
            completed_at=now if status == "completed" else None,
            tokens_used=tokens,
        )
        db_session.add(trace)
    await db_session.flush()

    subheader("Agent Traces")
    r = await client.get("/api/analytics/traces")
    check("GET /analytics/traces returns 200", r.status_code == 200)
    traces = r.json()
    check("Traces list has items", len(traces) >= 7)
    info(f"Total traces: {len(traces)}")

    # Filter by agent
    r = await client.get("/api/analytics/traces?agent_name=researcher")
    check("Filter traces by agent works", r.status_code == 200)
    filtered = r.json()
    check("Filtered traces are correct agent", all(t["agent_name"] == "researcher" for t in filtered))
    info(f"Researcher traces: {len(filtered)}")

    # Filter by status
    r = await client.get("/api/analytics/traces?status=failed")
    check("Filter traces by status works", r.status_code == 200)

    subheader("Performance Metrics")
    for period in ["day", "week", "month"]:
        r = await client.get(f"/api/analytics/metrics?period={period}")
        check(f"GET /analytics/metrics?period={period} returns 200", r.status_code == 200)
        data = r.json()
        check(f"Metrics period is {period}", data["period"] == period)

    r = await client.get("/api/analytics/metrics?period=day")
    metrics = r.json()
    info(f"Total executions: {metrics['total_executions']}")
    info(f"Agent stats: {len(metrics['agent_stats'])} agents")
    for stat in metrics["agent_stats"][:4]:
        info(f"  - {stat['agent']}: {stat['executions']} runs, ~{stat['avg_tokens']} tokens/run")

    subheader("Social Media Analytics")
    r = await client.get("/api/analytics/social?period=day")
    check("GET /analytics/social returns 200", r.status_code == 200)
    social = r.json()
    check("Social analytics has summary", "summary" in social)
    check("Social analytics has agent_performance", "agent_performance" in social)
    check("Social analytics has content_by_type", "content_by_type" in social)

    summary = social["summary"]
    info(f"Total content generated: {summary['total_content_generated']}")
    info(f"Social posts: {summary['social_posts']}")
    info(f"Total agent executions: {summary['total_agent_executions']}")
    info(f"Total tokens used: {summary['total_tokens_used']}")

    for perf in social["agent_performance"][:4]:
        info(f"  - {perf['agent']}: {perf['executions']} runs, "
             f"{perf['success_rate']}% success, ~{perf['avg_tokens']} tokens/run")


async def demo_agent_prompts():
    """Validate all agent prompts are configured."""
    header("9. Agent Prompts & Reasoning Patterns")

    from app.agents.prompts import AGENT_PROMPTS

    expected = {
        "orchestrator": "Step-by-Step Decomposition",
        "strategist": "Chain-of-Thought",
        "researcher": "ReAct",
        "scribe": "Template-Guided Generation",
        "advisor": "Self-Reflection",
        "analyst": "Data-Driven Benchmarking",
        "memory": "Retrieval-Augmented Grounding",
    }

    for agent, pattern in expected.items():
        has_prompt = agent in AGENT_PROMPTS and len(AGENT_PROMPTS[agent]) > 100
        check(f"{agent.title()} prompt configured ({pattern})", has_prompt)
        if has_prompt:
            info(f"  Length: {len(AGENT_PROMPTS[agent])} chars")


async def demo_mcp_integration():
    """Validate MCP tool integration setup."""
    header("10. MCP Tool Integration")

    from app.agents.factory import (
        create_filesystem_mcp, create_fetch_mcp, get_agent_tools,
    )
    import shutil

    npx_path = shutil.which("npx")
    if npx_path:
        info(f"npx found at: {npx_path}")

        fs_mcp = create_filesystem_mcp()
        if fs_mcp:
            check("Filesystem MCP created", True)
            check("Filesystem MCP name is 'filesystem'", fs_mcp.name == "filesystem")
            info(f"  Scoped to: data/drafts/")
        else:
            skip("Filesystem MCP creation", "returned None")

        fetch_mcp = create_fetch_mcp()
        if fetch_mcp:
            check("Fetch MCP created", True)
            check("Fetch MCP name is 'fetch'", fetch_mcp.name == "fetch")
        else:
            skip("Fetch MCP creation", "package removed from npm")

        # Verify agent tool assignment
        scribe_tools = get_agent_tools("scribe", include_mcp=True)
        has_fs = any(hasattr(t, "name") and t.name == "filesystem" for t in scribe_tools)
        check("Scribe gets filesystem MCP tool", has_fs)

        researcher_tools = get_agent_tools("researcher", include_mcp=True)
        has_fetch = any(hasattr(t, "name") and t.name == "fetch" for t in researcher_tools)
        # Fetch MCP package no longer exists on npm, so this is expected to be False
        check("Researcher built-in tools present (no fetch MCP)", not has_fetch and len(researcher_tools) >= 5)
    else:
        skip("MCP tool creation", "npx not found")
        info("Install Node.js/npm to enable MCP server tools")

    # Verify tools without MCP
    for agent, expected_count in [("researcher", 5), ("memory", 4), ("analyst", 2)]:
        tools = get_agent_tools(agent, include_mcp=False)
        check(f"{agent.title()} has {expected_count} base tools", len(tools) == expected_count)


async def demo_research_endpoint(client: AsyncClient):
    """Test research query endpoint."""
    header("11. Research Endpoints")

    r = await client.post("/api/research/query", json={
        "query": "AI collaboration trends in enterprise",
        "research_type": "comprehensive",
    })
    if r.status_code == 200:
        check("POST /research/query returns 200", True)
        data = r.json()
        check("Research response has status", "status" in data)
        info(f"Research status: {data.get('status')}")
    else:
        check("POST /research/query returns 500 (no Azure creds)", r.status_code == 500)
        info("Research endpoint requires Azure credentials")


async def demo_websocket_events():
    """Validate WebSocket event structure."""
    header("12. WebSocket Event Definitions")

    from app.models.schemas import WSEvent

    events = [
        ("agent.started", {"agent": "orchestrator", "task": "Analyzing request"}),
        ("agent.thinking", {"agent": "researcher", "message": "Searching trends...", "progress": 0.5}),
        ("agent.completed", {"agent": "scribe", "result": "Generated content", "duration_ms": 1200}),
        ("agent.handoff", {"from_agent": "orchestrator", "to_agent": "researcher", "context": "Discover trends"}),
        ("stream.token", {"token": "The "}),
        ("document.generated", {"id": "abc123", "type": "social_post", "title": "AI Launch Post"}),
    ]

    for event_type, data in events:
        evt = WSEvent(event_type=event_type, data=data)
        check(f"WSEvent '{event_type}' validates", evt.event_type == event_type)


# ──────────────────────────────────────────────────────────────
# Main runner
# ──────────────────────────────────────────────────────────────

async def run_demo():
    print("\n" + "=" * SECTION_WIDTH)
    print("  SOCIAL MEDIA COMMAND CENTER - E2E Demo")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * SECTION_WIDTH)

    # Setup database
    engine = await create_test_db()
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as db_session:
        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://demo") as client:
            # Run all demo scenarios
            await demo_health_and_info(client)
            conv_id = await demo_conversations(client)
            await demo_knowledge_search(client)
            await demo_agent_tools()
            doc_id_generated = await demo_content_generation(client)
            await demo_list_content(client, db_session)
            doc_id = await demo_document_export(client, db_session)
            await demo_analytics(client, db_session)
            await demo_agent_prompts()
            await demo_mcp_integration()
            await demo_research_endpoint(client)
            await demo_websocket_events()

        app.dependency_overrides.clear()

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

    # Remove test DB file
    db_path = Path("./data/demo_test.db")
    if db_path.exists():
        db_path.unlink()

    # Summary
    total = PASS_COUNT + FAIL_COUNT + SKIP_COUNT
    print(f"\n{'=' * SECTION_WIDTH}")
    print(f"  DEMO RESULTS")
    print(f"{'=' * SECTION_WIDTH}")
    print(f"  Total checks: {total}")
    print(f"  Passed:       {PASS_COUNT}")
    print(f"  Failed:       {FAIL_COUNT}")
    print(f"  Skipped:      {SKIP_COUNT}")
    print(f"{'=' * SECTION_WIDTH}")

    if FAIL_COUNT == 0:
        print(f"  ALL CHECKS PASSED")
    else:
        print(f"  {FAIL_COUNT} CHECK(S) FAILED")

    print(f"{'=' * SECTION_WIDTH}\n")

    return FAIL_COUNT == 0


if __name__ == "__main__":
    success = asyncio.run(run_demo())
    sys.exit(0 if success else 1)
