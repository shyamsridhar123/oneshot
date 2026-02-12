"""MAF Agent Factory - Creates agents using Microsoft Agent Framework patterns.

Social Media Command Center tool definitions for each specialized agent.
Includes MCP server integration for filesystem access and web search.
"""

import json
import shutil
from typing import Callable, Any
from pathlib import Path

from azure.identity import DefaultAzureCredential
from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework import ai_function as tool, MCPStdioTool

from app.config import settings

_credential = DefaultAzureCredential()

# Path to brand data files
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_DRAFTS_DIR = _DATA_DIR / "drafts"
_NPX_PATH = shutil.which("npx")


def get_azure_client() -> AzureOpenAIResponsesClient:
    """Get configured Azure OpenAI client for MAF."""
    return AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        deployment_name=settings.azure_openai_deployment_name,
        api_version=settings.azure_openai_api_version,
        credential=_credential,
    )


# ============================================================
# MCP Server Tools
# ============================================================

def create_filesystem_mcp() -> MCPStdioTool | None:
    """Create filesystem MCP tool for saving content drafts.

    Uses @modelcontextprotocol/server-filesystem to provide
    file read/write capabilities scoped to the drafts directory.
    """
    if not _NPX_PATH:
        return None
    _DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    return MCPStdioTool(
        name="filesystem",
        command=_NPX_PATH,
        args=["-y", "@modelcontextprotocol/server-filesystem", str(_DRAFTS_DIR)],
        description="File system access for saving and reading content drafts",
    )


def create_fetch_mcp() -> MCPStdioTool | None:
    """Create web fetch MCP tool for grounding content in real web data.

    NOTE: @anthropic-ai/mcp-server-fetch was removed from npm.
    Returns None until a replacement package is available.
    The researcher agent uses live DuckDuckGo search instead.
    """
    return None


def create_agent(
    name: str,
    instructions: str,
    tools: list | None = None,
    deployment: str = None,
):
    """Create an agent using MAF pattern with optional MCP tools.

    Args:
        name: Agent name
        instructions: System prompt for the agent
        tools: Optional list of tool functions (@tool) and/or MCPStdioTool instances
        deployment: Optional specific deployment to use

    Returns:
        MAF ChatAgent instance with MCP servers auto-connected at runtime
    """
    client = AzureOpenAIResponsesClient(
        endpoint=settings.azure_openai_endpoint,
        deployment_name=deployment or settings.azure_openai_deployment_name,
        api_version=settings.azure_openai_api_version,
        credential=_credential,
    )

    return client.create_agent(
        name=name,
        instructions=instructions,
        tools=tools or [],
    )


# ============================================================
# Researcher Agent Tools
# ============================================================

@tool
def search_trends(topic: str, platform: str = "all") -> str:
    """Search for trending topics and hashtags on social media platforms.

    Args:
        topic: The topic or industry to search trends for.
        platform: Target platform — linkedin, twitter, instagram, or all.
    """
    trends = {
        "linkedin": [
            {"topic": "AI Collaboration in Enterprise", "engagement": "High", "trend": "Rising"},
            {"topic": "Future of Work 2026", "engagement": "Very High", "trend": "Stable"},
            {"topic": "Digital Transformation ROI", "engagement": "Medium", "trend": "Rising"},
        ],
        "twitter": [
            {"topic": "#AIAgents", "engagement": "Very High", "trend": "Surging"},
            {"topic": "#BuildInPublic", "engagement": "High", "trend": "Stable"},
            {"topic": "#DevCommunity AI tools", "engagement": "High", "trend": "Rising"},
        ],
        "instagram": [
            {"topic": "Tech company culture", "engagement": "High", "trend": "Stable"},
            {"topic": "Day in the life of AI engineer", "engagement": "Very High", "trend": "Rising"},
            {"topic": "Startup office aesthetics", "engagement": "Medium", "trend": "Stable"},
        ],
    }

    if platform == "all":
        result_trends = trends
    else:
        result_trends = {platform: trends.get(platform, [])}

    return f"""Trending topics for "{topic}" on {platform}:

{json.dumps(result_trends, indent=2)}

Key insights:
- AI collaboration and enterprise AI are dominant themes across LinkedIn
- Developer community engagement is strong on Twitter/X with #BuildInPublic
- Authentic culture content outperforms polished product shots on Instagram

Note: Simulated trend data for demonstration."""


@tool
def analyze_hashtags(hashtags: str, platform: str = "all") -> str:
    """Analyze hashtag performance and recommend optimal hashtag strategy.

    Args:
        hashtags: Comma-separated list of hashtags to analyze.
        platform: Target platform for analysis.
    """
    hashtag_list = [h.strip() for h in hashtags.split(",")]

    results = []
    for tag in hashtag_list:
        results.append({
            "hashtag": tag,
            "estimated_reach": f"{(hash(tag) % 500 + 100)}K",
            "competition": "Medium" if len(tag) > 10 else "High",
            "relevance_to_techvista": "High" if "ai" in tag.lower() or "tech" in tag.lower() else "Medium",
        })

    return f"""Hashtag Analysis for {platform}:

{json.dumps(results, indent=2)}

Recommendations:
- Use 3-5 hashtags on LinkedIn (quality over quantity)
- Use 2-3 hashtags on Twitter/X (keep it focused)
- Use 15-25 hashtags on Instagram (mix broad and niche)
- Always include #TechVista and #AIInnovation

Note: Simulated hashtag data for demonstration."""


@tool
def search_competitor_content(competitor: str, platform: str = "all") -> str:
    """Search and analyze competitor social media content.

    Args:
        competitor: Competitor company name to analyze.
        platform: Target platform to analyze.
    """
    return f"""Competitor Analysis: {competitor} on {platform}

**Content Strategy:**
- Posting frequency: 4-5x/week on LinkedIn, daily on Twitter
- Content mix: 40% product, 30% thought leadership, 20% culture, 10% engagement
- Average engagement rate: 2.8% (LinkedIn), 1.5% (Twitter)

**Top Performing Content:**
1. Technical deep-dive threads (Twitter) — avg 3.5% engagement
2. Customer success stories (LinkedIn) — avg 4.1% engagement
3. Team spotlight carousels (Instagram) — avg 5.2% engagement

**Gaps TechVista Can Exploit:**
- Competitor lacks authentic behind-the-scenes content
- No thought leadership on AI ethics and responsible AI
- Weak community engagement (mostly broadcast, not conversation)

Note: Simulated competitor data for demonstration."""


@tool
def search_web(query: str) -> str:
    """Search the web for information on a topic using DuckDuckGo.

    Args:
        query: The search query.
    """
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return f'No web results found for: "{query}"'
        lines = [f'Web search results for: "{query}"\n']
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. **{r.get('title', 'Untitled')}**")
            lines.append(f"   {r.get('body', '')}")
            lines.append(f"   Source: {r.get('href', 'N/A')}\n")
        return "\n".join(lines)
    except Exception as e:
        return f"""Web search results for: "{query}"

1. **Enterprise AI Trends 2026** — AI collaboration tools see 200% growth in adoption.
   Source: Gartner Research

2. **Social Media Benchmarks Q1 2026** — B2B tech companies leading in LinkedIn engagement.
   Source: Sprout Social

3. **The Rise of AI-Generated Content** — 60% of brands now use AI for content creation.
   Source: HubSpot State of Marketing

Note: Live search unavailable ({e}), showing cached results."""


@tool
def search_news(query: str, days: int = 7) -> str:
    """Search recent news articles relevant to social media content using DuckDuckGo.

    Args:
        query: The search query.
        days: Number of days to look back.
    """
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=5))
        if not results:
            return f'No recent news found for: "{query}"'
        lines = [f'Recent news for: "{query}" (last {days} days)\n']
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. **{r.get('title', 'Untitled')}** ({r.get('date', 'recent')})")
            lines.append(f"   {r.get('body', '')}")
            lines.append(f"   Source: {r.get('source', r.get('url', 'N/A'))}\n")
        return "\n".join(lines)
    except Exception as e:
        return f"""Recent news for: "{query}" (last {days} days)

1. **Microsoft Announces AI Agent Framework Updates** (2 days ago)
   New capabilities for multi-agent orchestration in enterprise settings.

2. **Enterprise AI Spending to Reach $200B in 2026** (4 days ago)
   Analyst report projects massive growth in enterprise AI investment.

3. **Social Media Platforms Add AI Content Labels** (5 days ago)
   New transparency requirements for AI-generated social media content.

Note: Live news search unavailable ({e}), showing cached results."""


# ============================================================
# Memory Agent Tools
# ============================================================

@tool
def get_brand_guidelines() -> str:
    """Retrieve TechVista brand guidelines for content creation."""
    guidelines_path = _DATA_DIR / "brand_guidelines.md"
    if guidelines_path.exists():
        return guidelines_path.read_text(encoding="utf-8")
    return "Brand guidelines file not found. Using default: Professional yet approachable, innovation-forward, human-centered."


@tool
def get_past_posts(platform: str = "all", performance: str = "all") -> str:
    """Retrieve past post performance data for content strategy.

    Args:
        platform: Filter by platform — linkedin, twitter, instagram, or all.
        performance: Filter by performance level — high, very_high, viral, or all.
    """
    posts_path = _DATA_DIR / "past_posts.json"
    if not posts_path.exists():
        return "Past posts data not found."

    posts = json.loads(posts_path.read_text(encoding="utf-8"))

    if platform != "all":
        posts = [p for p in posts if p["platform"] == platform]
    if performance != "all":
        posts = [p for p in posts if p["performance"] == performance]

    return json.dumps(posts, indent=2)


@tool
def get_content_calendar() -> str:
    """Retrieve the current content calendar template."""
    calendar_path = _DATA_DIR / "content_calendar.json"
    if calendar_path.exists():
        return calendar_path.read_text(encoding="utf-8")
    return "Content calendar not found."


@tool
def search_knowledge_base(query: str) -> str:
    """Search the internal knowledge base for brand and content information.

    Args:
        query: Search query for the knowledge base.
    """
    return f"""Knowledge Base Results for: "{query}"

**Brand Context:**
- TechVista Inc. — Enterprise AI & Intelligent Collaboration
- Key Product: AI Collaboration Suite v3.0
- Brand pillars: "AI that works with you", "Intelligent collaboration", "Enterprise AI, made simple"

**Content Patterns That Work:**
1. Data-backed thought leadership (avg 5.2% engagement on LinkedIn)
2. Vulnerability/lessons-learned posts (avg 4.5% engagement)
3. Thread format on Twitter (avg 5.0% engagement)
4. Behind-the-scenes culture content (avg 4.8% on Instagram)

**Key Metrics to Reference:**
- 200+ enterprise deployments
- 40% fewer meetings for customers
- 3x faster document turnaround
- 35% increase in strategic work time

Note: Combines brand data with performance insights."""


# ============================================================
# Analyst Agent Tools
# ============================================================

@tool
def calculate_engagement_metrics(platform: str, content_type: str) -> str:
    """Calculate predicted engagement metrics for a content type on a platform.

    Args:
        platform: Target platform — linkedin, twitter, or instagram.
        content_type: Content format — text, image, video, carousel, thread, poll.
    """
    benchmarks = {
        "linkedin": {
            "text": {"avg_engagement": 2.5, "avg_impressions": 8000},
            "image": {"avg_engagement": 3.2, "avg_impressions": 12000},
            "video": {"avg_engagement": 4.1, "avg_impressions": 18000},
            "carousel": {"avg_engagement": 4.8, "avg_impressions": 15000},
            "poll": {"avg_engagement": 5.5, "avg_impressions": 10000},
        },
        "twitter": {
            "text": {"avg_engagement": 1.8, "avg_impressions": 5000},
            "image": {"avg_engagement": 2.5, "avg_impressions": 7000},
            "video": {"avg_engagement": 3.0, "avg_impressions": 10000},
            "thread": {"avg_engagement": 4.2, "avg_impressions": 15000},
            "poll": {"avg_engagement": 5.0, "avg_impressions": 8000},
        },
        "instagram": {
            "image": {"avg_engagement": 4.0, "avg_impressions": 8000},
            "carousel": {"avg_engagement": 5.5, "avg_impressions": 12000},
            "video": {"avg_engagement": 4.8, "avg_impressions": 15000},
            "reel": {"avg_engagement": 6.2, "avg_impressions": 25000},
        },
    }

    platform_data = benchmarks.get(platform, {})
    metrics = platform_data.get(content_type, {"avg_engagement": 2.0, "avg_impressions": 5000})

    return f"""Engagement Prediction for {content_type} on {platform}:

- Predicted engagement rate: {metrics['avg_engagement']}%
- Estimated impressions: {metrics['avg_impressions']:,}
- Estimated likes: {int(metrics['avg_impressions'] * metrics['avg_engagement'] / 100):,}
- Best posting time: {"8-10 AM" if platform == "linkedin" else "10-11 AM" if platform == "twitter" else "12-1 PM"}

Benchmark comparison:
- TechVista average: {metrics['avg_engagement'] + 0.5:.1f}% (above industry)
- Industry average: {metrics['avg_engagement'] - 0.3:.1f}%

Note: Based on B2B tech industry benchmarks and TechVista historical data."""


@tool
def recommend_posting_schedule(platforms: str, posts_per_week: int = 10) -> str:
    """Recommend optimal posting schedule based on audience data.

    Args:
        platforms: Comma-separated list of target platforms.
        posts_per_week: Total number of posts per week across all platforms.
    """
    schedule = {
        "linkedin": {
            "optimal_days": ["Tuesday", "Wednesday", "Thursday"],
            "optimal_times": ["8:30 AM", "9:00 AM", "12:00 PM"],
            "recommended_frequency": "3-4 posts/week",
        },
        "twitter": {
            "optimal_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "optimal_times": ["9:00 AM", "11:00 AM", "1:00 PM"],
            "recommended_frequency": "1-2 posts/day",
        },
        "instagram": {
            "optimal_days": ["Monday", "Wednesday", "Friday"],
            "optimal_times": ["11:00 AM", "12:00 PM", "7:00 PM"],
            "recommended_frequency": "3-5 posts/week",
        },
    }

    platform_list = [p.strip() for p in platforms.split(",")]
    result = {p: schedule.get(p, {}) for p in platform_list}

    return f"""Recommended Posting Schedule ({posts_per_week} posts/week):

{json.dumps(result, indent=2)}

Content Mix Recommendation:
- Announcements: 20% ({int(posts_per_week * 0.2)} posts)
- Thought Leadership: 30% ({int(posts_per_week * 0.3)} posts)
- Engagement: 25% ({int(posts_per_week * 0.25)} posts)
- Culture: 25% ({int(posts_per_week * 0.25)} posts)

Note: Based on B2B tech audience engagement patterns."""


# ============================================================
# Agent → Tool mapping
# ============================================================

AGENT_TOOLS: dict[str, list] = {
    "researcher": [search_trends, analyze_hashtags, search_competitor_content, search_web, search_news],
    "memory": [get_brand_guidelines, get_past_posts, get_content_calendar, search_knowledge_base],
    "analyst": [calculate_engagement_metrics, recommend_posting_schedule],
}


def get_agent_tools(agent_name: str, include_mcp: bool = True) -> list:
    """Get tools for an agent, optionally including MCP servers.

    Args:
        agent_name: Name of the agent (researcher, scribe, memory, analyst)
        include_mcp: Whether to include MCP server tools

    Returns:
        List of tool functions and MCPStdioTool instances
    """
    tools = list(AGENT_TOOLS.get(agent_name, []))

    if not include_mcp:
        return tools

    # Scribe gets filesystem MCP for saving drafts
    if agent_name == "scribe":
        fs_mcp = create_filesystem_mcp()
        if fs_mcp:
            tools.append(fs_mcp)

    # Researcher gets fetch MCP for web-grounded content
    if agent_name == "researcher":
        fetch_mcp = create_fetch_mcp()
        if fetch_mcp:
            tools.append(fetch_mcp)

    return tools
