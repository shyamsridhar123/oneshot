"""Tests for agent factory, tools, and MCP integration."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.agents.factory import (
    search_trends,
    search_web,
    search_news,
    search_competitor_content,
    analyze_hashtags,
    get_brand_guidelines,
    get_past_posts,
    get_content_calendar,
    search_knowledge_base,
    calculate_engagement_metrics,
    recommend_posting_schedule,
    AGENT_TOOLS,
    get_agent_tools,
    create_filesystem_mcp,
    create_fetch_mcp,
)


# ============================================================
# Researcher Tools
# ============================================================

class TestSearchTrends:
    """Tests for the search_trends tool function."""

    def test_search_trends_returns_string(self):
        result = search_trends("AI", "all")
        assert isinstance(result, str)

    def test_search_trends_contains_topic(self):
        result = search_trends("cloud computing", "all")
        assert "cloud computing" in result

    def test_search_trends_specific_platform(self):
        result = search_trends("AI", "linkedin")
        assert "linkedin" in result

    def test_search_trends_default_platform(self):
        result = search_trends("AI")
        assert "all" in result

    def test_search_trends_contains_json_data(self):
        result = search_trends("AI", "twitter")
        assert "#AIAgents" in result or "twitter" in result


class TestSearchWeb:
    """Tests for the search_web tool function."""

    def test_search_web_returns_string(self):
        result = search_web("enterprise AI")
        assert isinstance(result, str)

    def test_search_web_contains_query(self):
        result = search_web("machine learning 2026")
        assert "machine learning 2026" in result


class TestSearchNews:
    """Tests for the search_news tool function."""

    def test_search_news_returns_string(self):
        result = search_news("AI agents")
        assert isinstance(result, str)

    def test_search_news_contains_query(self):
        result = search_news("AI agents", 14)
        assert "AI agents" in result
        assert "14 days" in result

    def test_search_news_default_days(self):
        result = search_news("AI")
        assert "7 days" in result


class TestSearchCompetitorContent:
    """Tests for the search_competitor_content tool function."""

    def test_returns_string(self):
        result = search_competitor_content("Acme Corp", "linkedin")
        assert isinstance(result, str)

    def test_contains_competitor_name(self):
        result = search_competitor_content("Acme Corp")
        assert "Acme Corp" in result


class TestAnalyzeHashtags:
    """Tests for the analyze_hashtags tool function."""

    def test_returns_string(self):
        result = analyze_hashtags("#AIAgents, #TechVista")
        assert isinstance(result, str)

    def test_handles_multiple_hashtags(self):
        result = analyze_hashtags("#AIAgents, #TechVista, #Enterprise")
        assert "AIAgents" in result


# ============================================================
# Memory Agent Tools
# ============================================================

class TestGetBrandGuidelines:
    """Tests for the get_brand_guidelines tool function."""

    def test_returns_string(self):
        result = get_brand_guidelines()
        assert isinstance(result, str)

    def test_returns_content_or_default(self):
        result = get_brand_guidelines()
        # Either returns file content or the default message
        assert len(result) > 0


class TestGetPastPosts:
    """Tests for the get_past_posts tool function."""

    def test_returns_string(self):
        result = get_past_posts()
        assert isinstance(result, str)

    def test_filter_by_platform(self):
        result = get_past_posts(platform="linkedin")
        assert isinstance(result, str)


class TestGetContentCalendar:
    """Tests for the get_content_calendar tool function."""

    def test_returns_string(self):
        result = get_content_calendar()
        assert isinstance(result, str)


class TestSearchKnowledgeBase:
    """Tests for the search_knowledge_base tool function."""

    def test_returns_string(self):
        result = search_knowledge_base("AI collaboration")
        assert isinstance(result, str)

    def test_contains_query(self):
        result = search_knowledge_base("brand pillars")
        assert "brand pillars" in result or "TechVista" in result


# ============================================================
# Analyst Agent Tools
# ============================================================

class TestCalculateEngagementMetrics:
    """Tests for the calculate_engagement_metrics tool function."""

    def test_returns_string(self):
        result = calculate_engagement_metrics("linkedin", "text")
        assert isinstance(result, str)

    def test_contains_platform(self):
        result = calculate_engagement_metrics("linkedin", "carousel")
        assert "linkedin" in result

    def test_contains_engagement_data(self):
        result = calculate_engagement_metrics("twitter", "thread")
        assert "engagement" in result.lower()

    def test_unknown_content_type_uses_default(self):
        result = calculate_engagement_metrics("linkedin", "unknown_type")
        assert isinstance(result, str)
        assert "2.0%" in result  # default engagement rate


class TestRecommendPostingSchedule:
    """Tests for the recommend_posting_schedule tool function."""

    def test_returns_string(self):
        result = recommend_posting_schedule("linkedin,twitter")
        assert isinstance(result, str)

    def test_contains_schedule_data(self):
        result = recommend_posting_schedule("linkedin", 10)
        assert "Posting Schedule" in result

    def test_custom_posts_per_week(self):
        result = recommend_posting_schedule("twitter", 20)
        assert "20 posts/week" in result


# ============================================================
# Agent Tool Mapping
# ============================================================

class TestAgentToolMapping:
    """Tests for the AGENT_TOOLS mapping and get_agent_tools function."""

    def test_researcher_has_tools(self):
        assert "researcher" in AGENT_TOOLS
        assert len(AGENT_TOOLS["researcher"]) >= 4

    def test_memory_has_tools(self):
        assert "memory" in AGENT_TOOLS
        assert len(AGENT_TOOLS["memory"]) >= 3

    def test_analyst_has_tools(self):
        assert "analyst" in AGENT_TOOLS
        assert len(AGENT_TOOLS["analyst"]) >= 2

    def test_researcher_tools_include_search(self):
        tool_funcs = AGENT_TOOLS["researcher"]
        tool_names = [getattr(t, 'name', getattr(t, '__name__', str(t))) for t in tool_funcs]
        assert any("search" in n for n in tool_names)

    def test_get_agent_tools_returns_list(self):
        tools = get_agent_tools("researcher", include_mcp=False)
        assert isinstance(tools, list)
        assert len(tools) >= 4

    def test_get_agent_tools_empty_for_unknown(self):
        tools = get_agent_tools("nonexistent_agent", include_mcp=False)
        assert tools == []

    def test_get_agent_tools_does_not_mutate_mapping(self):
        original_count = len(AGENT_TOOLS.get("researcher", []))
        get_agent_tools("researcher", include_mcp=False)
        assert len(AGENT_TOOLS.get("researcher", [])) == original_count


# ============================================================
# MCP Tool Integration
# ============================================================

class TestMCPToolCreation:
    """Tests for MCP tool creation functions."""

    def test_create_filesystem_mcp_with_npx(self):
        """Should return MCPStdioTool when npx is available."""
        with patch("app.agents.factory._NPX_PATH", "/usr/bin/npx"):
            result = create_filesystem_mcp()
            assert result is not None
            assert result.name == "filesystem"

    def test_create_filesystem_mcp_without_npx(self):
        """Should return None when npx is not available."""
        with patch("app.agents.factory._NPX_PATH", None):
            result = create_filesystem_mcp()
            assert result is None

    def test_create_fetch_mcp_with_npx(self):
        """Should return MCPStdioTool when npx is available."""
        with patch("app.agents.factory._NPX_PATH", "/usr/bin/npx"):
            result = create_fetch_mcp()
            assert result is not None
            assert result.name == "fetch"

    def test_create_fetch_mcp_without_npx(self):
        """Should return None when npx is not available."""
        with patch("app.agents.factory._NPX_PATH", None):
            result = create_fetch_mcp()
            assert result is None

    def test_get_agent_tools_scribe_includes_mcp(self):
        """Scribe should get filesystem MCP when available."""
        with patch("app.agents.factory._NPX_PATH", "/usr/bin/npx"):
            tools = get_agent_tools("scribe", include_mcp=True)
            has_mcp = any(
                hasattr(t, "name") and t.name == "filesystem" for t in tools
            )
            assert has_mcp

    def test_get_agent_tools_researcher_includes_mcp(self):
        """Researcher should get fetch MCP when available."""
        with patch("app.agents.factory._NPX_PATH", "/usr/bin/npx"):
            tools = get_agent_tools("researcher", include_mcp=True)
            has_mcp = any(
                hasattr(t, "name") and t.name == "fetch" for t in tools
            )
            assert has_mcp

    def test_get_agent_tools_no_mcp_flag(self):
        """Should exclude MCP tools when include_mcp is False."""
        with patch("app.agents.factory._NPX_PATH", "/usr/bin/npx"):
            tools = get_agent_tools("scribe", include_mcp=False)
            has_mcp = any(
                hasattr(t, "name") and t.name == "filesystem" for t in tools
            )
            assert not has_mcp

    def test_analyst_has_no_mcp_tools(self):
        """Analyst should not receive any MCP tools."""
        with patch("app.agents.factory._NPX_PATH", "/usr/bin/npx"):
            tools = get_agent_tools("analyst", include_mcp=True)
            mcp_tools = [t for t in tools if hasattr(t, "name") and t.name in ("filesystem", "fetch")]
            assert len(mcp_tools) == 0


# ============================================================
# Scribe Agent
# ============================================================

class TestScribeAgent:
    """Tests for the scribe agent module."""

    async def test_scribe_fallback_on_auth_error(self):
        """Scribe should fall back to direct LLM when MAF agent fails."""
        from unittest.mock import AsyncMock

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Generated content"
        mock_response.tokens_used = 100
        mock_llm.complete_with_usage = AsyncMock(return_value=mock_response)

        with patch("app.agents.scribe.create_agent", side_effect=Exception("Auth failed")), \
             patch("app.agents.scribe.get_llm_service", return_value=mock_llm):
            from app.agents.scribe import run_scribe
            text, tokens = await run_scribe("Write a post", {"message": "AI launch"})
            assert text == "Generated content"
            assert tokens == 100
            mock_llm.complete_with_usage.assert_awaited_once()

    async def test_scribe_uses_wave1_context(self):
        """Scribe should incorporate Wave 1 agent outputs in prompt."""
        from unittest.mock import AsyncMock

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Content with context"
        mock_response.tokens_used = 50
        mock_llm.complete_with_usage = AsyncMock(return_value=mock_response)

        context = {
            "previous_results": {
                "strategist": "Focus on thought leadership",
                "researcher": "AI trending on LinkedIn",
                "analyst": "Best time: 9AM",
                "memory": "Brand voice: professional",
            },
            "platforms": ["linkedin"],
        }

        with patch("app.agents.scribe.create_agent", side_effect=Exception("Auth")), \
             patch("app.agents.scribe.get_llm_service", return_value=mock_llm):
            from app.agents.scribe import run_scribe
            text, tokens = await run_scribe("Write LinkedIn post", context)
            assert text == "Content with context"

            # Verify the prompt included Wave 1 context
            call_args = mock_llm.complete_with_usage.call_args
            prompt = call_args.kwargs.get("prompt", "")
            assert "Content Strategy" in prompt
            assert "Research & Trends" in prompt
            assert "Engagement Data" in prompt
            assert "Brand Context" in prompt

    async def test_scribe_uses_target_platforms(self):
        """Scribe prompt should include target platforms."""
        from unittest.mock import AsyncMock

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Platform content"
        mock_response.tokens_used = 30
        mock_llm.complete_with_usage = AsyncMock(return_value=mock_response)

        with patch("app.agents.scribe.create_agent", side_effect=Exception("Auth")), \
             patch("app.agents.scribe.get_llm_service", return_value=mock_llm):
            from app.agents.scribe import run_scribe
            await run_scribe("Write posts", {"platforms": ["twitter", "instagram"]})

            call_args = mock_llm.complete_with_usage.call_args
            prompt = call_args.kwargs.get("prompt", "")
            assert "twitter" in prompt
            assert "instagram" in prompt


# ============================================================
# Researcher Agent
# ============================================================

class TestResearcherAgent:
    """Tests for the researcher agent module."""

    async def test_researcher_fallback_on_auth_error(self):
        """Researcher should fall back to direct tool calls + LLM when MAF fails."""
        from unittest.mock import AsyncMock

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Research findings"
        mock_response.tokens_used = 200
        mock_llm.complete_with_usage = AsyncMock(return_value=mock_response)

        with patch("app.agents.researcher.create_agent", side_effect=Exception("Auth")), \
             patch("app.agents.researcher.get_llm_service", return_value=mock_llm):
            from app.agents.researcher import run_researcher
            text, tokens = await run_researcher(
                "Research AI trends",
                {"message": "AI collaboration launch", "entities": ["Microsoft"], "platforms": ["linkedin"]},
            )
            assert text == "Research findings"
            assert tokens == 200

    async def test_researcher_fallback_uses_tools(self):
        """Researcher fallback should call search_web, search_news, search_trends."""
        from unittest.mock import AsyncMock

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Synthesized research"
        mock_response.tokens_used = 150
        mock_llm.complete_with_usage = AsyncMock(return_value=mock_response)

        with patch("app.agents.researcher.create_agent", side_effect=Exception("Auth")), \
             patch("app.agents.researcher.get_llm_service", return_value=mock_llm), \
             patch("app.agents.researcher.search_web", return_value="web results") as mock_web, \
             patch("app.agents.researcher.search_news", return_value="news results") as mock_news, \
             patch("app.agents.researcher.search_trends", return_value="trend results") as mock_trends:
            from app.agents.researcher import run_researcher
            await run_researcher(
                "Research AI trends",
                {"message": "AI launch", "entities": [], "platforms": ["twitter"]},
            )
            mock_web.assert_called_once()
            mock_news.assert_called_once()
            mock_trends.assert_called_once()

    async def test_researcher_fallback_includes_competitor_analysis(self):
        """Researcher fallback should analyze competitors from entities."""
        from unittest.mock import AsyncMock

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Competitor research"
        mock_response.tokens_used = 180
        mock_llm.complete_with_usage = AsyncMock(return_value=mock_response)

        with patch("app.agents.researcher.create_agent", side_effect=Exception("Auth")), \
             patch("app.agents.researcher.get_llm_service", return_value=mock_llm), \
             patch("app.agents.researcher.search_competitor_content", return_value="comp data") as mock_comp:
            from app.agents.researcher import run_researcher
            await run_researcher(
                "Research competitors",
                {"message": "Analyze market", "entities": ["Acme", "BigCorp"], "platforms": ["linkedin"]},
            )
            assert mock_comp.call_count == 2

    async def test_researcher_default_platforms(self):
        """Researcher should default to all 3 platforms."""
        from unittest.mock import AsyncMock

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Research"
        mock_response.tokens_used = 50
        mock_llm.complete_with_usage = AsyncMock(return_value=mock_response)

        with patch("app.agents.researcher.create_agent", side_effect=Exception("Auth")), \
             patch("app.agents.researcher.get_llm_service", return_value=mock_llm):
            from app.agents.researcher import run_researcher
            await run_researcher("Research", {"message": "test"})

            call_args = mock_llm.complete_with_usage.call_args
            prompt = call_args.kwargs.get("prompt", "")
            assert "linkedin" in prompt
            assert "twitter" in prompt
            assert "instagram" in prompt


# ============================================================
# Prompts Module
# ============================================================

class TestAgentPrompts:
    """Tests for agent prompt definitions."""

    def test_all_prompts_defined(self):
        from app.agents.prompts import AGENT_PROMPTS
        expected_agents = ["orchestrator", "strategist", "researcher", "analyst", "scribe", "advisor", "memory"]
        for agent in expected_agents:
            assert agent in AGENT_PROMPTS, f"Missing prompt for {agent}"

    def test_prompts_are_non_empty_strings(self):
        from app.agents.prompts import AGENT_PROMPTS
        for name, prompt in AGENT_PROMPTS.items():
            assert isinstance(prompt, str), f"{name} prompt should be a string"
            assert len(prompt) > 100, f"{name} prompt is too short"

    def test_prompts_mention_reasoning_patterns(self):
        from app.agents.prompts import AGENT_PROMPTS
        patterns = {
            "orchestrator": "Decomposition",
            "strategist": "Chain-of-Thought",
            "researcher": "ReAct",
            "scribe": "Template",
            "advisor": "Self-Reflection",
            "analyst": "Data",
            "memory": "Retrieval",
        }
        for agent, pattern in patterns.items():
            assert pattern.lower() in AGENT_PROMPTS[agent].lower(), \
                f"{agent} prompt should mention {pattern}"
