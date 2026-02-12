"""Tests for seed data integrity."""

import pytest
import uuid
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import KnowledgeItem, Engagement
from app.data.seed import (
    SAMPLE_CAMPAIGNS,
    SAMPLE_STRATEGIES,
)


class TestSeedDataConstants:
    """Tests for seed data constant definitions."""

    def test_sample_campaigns_count(self):
        """Should have expected number of sample campaigns."""
        assert len(SAMPLE_CAMPAIGNS) == 5

    def test_sample_strategies_count(self):
        """Should have expected number of sample strategies."""
        assert len(SAMPLE_STRATEGIES) == 6

    def test_campaign_required_fields(self):
        """Each campaign should have required fields."""
        required_fields = [
            "client_name",
            "client_industry",
            "engagement_type",
            "description",
            "outcomes",
            "team_members",
            "frameworks_used",
            "status",
            "days_ago",
        ]
        for campaign in SAMPLE_CAMPAIGNS:
            for field in required_fields:
                assert field in campaign, f"Missing field '{field}' in campaign"

    def test_strategy_required_fields(self):
        """Each strategy should have required fields."""
        required_fields = ["title", "category", "content", "tags"]
        for strategy in SAMPLE_STRATEGIES:
            for field in required_fields:
                assert field in strategy, f"Missing field '{field}' in strategy"

    def test_campaign_types_variety(self):
        """Campaigns should cover various types."""
        types = {camp["engagement_type"] for camp in SAMPLE_CAMPAIGNS}
        assert len(types) >= 4, "Should have at least 4 different campaign types"

    def test_strategy_categories(self):
        """All strategies should have category 'strategy'."""
        for strategy in SAMPLE_STRATEGIES:
            assert strategy["category"] == "strategy"

    def test_campaign_team_members_not_empty(self):
        """Each campaign should have at least one team member."""
        for campaign in SAMPLE_CAMPAIGNS:
            assert len(campaign["team_members"]) >= 1

    def test_strategy_tags_not_empty(self):
        """Each strategy should have at least one tag."""
        for strategy in SAMPLE_STRATEGIES:
            assert len(strategy["tags"]) >= 1

    def test_campaign_status_values(self):
        """Campaign status should be valid."""
        valid_statuses = ["completed", "in_progress", "planned"]
        for campaign in SAMPLE_CAMPAIGNS:
            assert campaign["status"] in valid_statuses


class TestSeedDataIntegrity:
    """Tests for seed data loaded into database."""

    async def test_seed_campaigns_to_db(self, db_session: AsyncSession):
        """Should be able to create campaigns from seed data."""
        for camp_data in SAMPLE_CAMPAIGNS[:3]:  # Test subset
            engagement = Engagement(
                id=str(uuid.uuid4()),
                client_name=camp_data["client_name"],
                client_industry=camp_data["client_industry"],
                engagement_type=camp_data["engagement_type"],
                description=camp_data["description"],
                outcomes=camp_data["outcomes"],
                team_members=camp_data["team_members"],
                frameworks_used=camp_data["frameworks_used"],
                status=camp_data["status"],
            )
            db_session.add(engagement)

        await db_session.flush()

        # Verify insertion
        result = await db_session.execute(select(func.count(Engagement.id)))
        count = result.scalar()
        assert count >= 3

    async def test_seed_strategies_to_db(self, db_session: AsyncSession):
        """Should be able to create strategies from seed data."""
        for strat_data in SAMPLE_STRATEGIES[:3]:  # Test subset
            item = KnowledgeItem(
                id=str(uuid.uuid4()),
                title=strat_data["title"],
                content=strat_data["content"],
                category=strat_data["category"],
                industry=strat_data.get("industry"),
                tags=strat_data["tags"],
            )
            db_session.add(item)

        await db_session.flush()

        # Verify insertion
        result = await db_session.execute(
            select(func.count(KnowledgeItem.id)).where(
                KnowledgeItem.category == "strategy"
            )
        )
        count = result.scalar()
        assert count >= 3

    async def test_campaign_query_by_type(self, db_session: AsyncSession):
        """Should be able to query campaigns by engagement type."""
        for camp_data in SAMPLE_CAMPAIGNS:
            engagement = Engagement(
                id=str(uuid.uuid4()),
                client_name=camp_data["client_name"],
                client_industry=camp_data["client_industry"],
                engagement_type=camp_data["engagement_type"],
                description=camp_data["description"],
                status=camp_data["status"],
            )
            db_session.add(engagement)
        await db_session.flush()

        # Query by Technology industry
        result = await db_session.execute(
            select(Engagement).where(Engagement.client_industry == "Technology")
        )
        tech_campaigns = result.scalars().all()
        assert len(tech_campaigns) >= 1

    async def test_knowledge_query_by_category(self, db_session: AsyncSession):
        """Should be able to query knowledge items by category."""
        for strat_data in SAMPLE_STRATEGIES:
            item = KnowledgeItem(
                id=str(uuid.uuid4()),
                title=strat_data["title"],
                content=strat_data["content"],
                category=strat_data["category"],
                tags=strat_data["tags"],
            )
            db_session.add(item)
        await db_session.flush()

        # Query strategies
        result = await db_session.execute(
            select(KnowledgeItem).where(KnowledgeItem.category == "strategy")
        )
        strategies = result.scalars().all()
        assert len(strategies) == 6


class TestSeedDataContent:
    """Tests for seed data content quality."""

    def test_campaign_descriptions_not_empty(self):
        """Campaign descriptions should not be empty."""
        for campaign in SAMPLE_CAMPAIGNS:
            assert len(campaign["description"]) >= 50

    def test_strategy_content_meaningful(self):
        """Strategy content should be substantial."""
        for strategy in SAMPLE_STRATEGIES:
            assert len(strategy["content"]) >= 100

    def test_campaign_outcomes_present(self):
        """All campaigns should have outcomes documented."""
        for campaign in SAMPLE_CAMPAIGNS:
            assert len(campaign["outcomes"]) >= 20

    def test_strategy_titles_unique(self):
        """Strategy titles should be unique."""
        titles = [strat["title"] for strat in SAMPLE_STRATEGIES]
        assert len(titles) == len(set(titles))

    def test_campaign_types_unique(self):
        """Campaign engagement types should be unique."""
        types = [camp["engagement_type"] for camp in SAMPLE_CAMPAIGNS]
        assert len(types) == len(set(types))

    def test_tags_are_lowercase(self):
        """Tags should be lowercase for consistency."""
        for strategy in SAMPLE_STRATEGIES:
            for tag in strategy["tags"]:
                assert tag == tag.lower(), f"Tag '{tag}' should be lowercase"
