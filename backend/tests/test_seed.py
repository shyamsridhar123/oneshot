"""Tests for seed data integrity."""

import pytest
import uuid
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import KnowledgeItem, Engagement
from app.data.seed import (
    SAMPLE_ENGAGEMENTS,
    SAMPLE_FRAMEWORKS,
    SAMPLE_EXPERTISE,
)


class TestSeedDataConstants:
    """Tests for seed data constant definitions."""

    def test_sample_engagements_count(self):
        """Should have expected number of sample engagements."""
        assert len(SAMPLE_ENGAGEMENTS) == 8

    def test_sample_frameworks_count(self):
        """Should have expected number of sample frameworks."""
        assert len(SAMPLE_FRAMEWORKS) == 10

    def test_sample_expertise_count(self):
        """Should have expected number of expertise areas."""
        assert len(SAMPLE_EXPERTISE) == 5

    def test_engagement_required_fields(self):
        """Each engagement should have required fields."""
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
        for engagement in SAMPLE_ENGAGEMENTS:
            for field in required_fields:
                assert field in engagement, f"Missing field '{field}' in engagement"

    def test_framework_required_fields(self):
        """Each framework should have required fields."""
        required_fields = ["title", "category", "content", "tags"]
        for framework in SAMPLE_FRAMEWORKS:
            for field in required_fields:
                assert field in framework, f"Missing field '{field}' in framework"

    def test_expertise_required_fields(self):
        """Each expertise area should have required fields."""
        required_fields = ["title", "category", "content", "tags"]
        for expertise in SAMPLE_EXPERTISE:
            for field in required_fields:
                assert field in expertise, f"Missing field '{field}' in expertise"

    def test_engagement_industries_variety(self):
        """Engagements should cover multiple industries."""
        industries = {eng["client_industry"] for eng in SAMPLE_ENGAGEMENTS}
        assert len(industries) >= 5, "Should have at least 5 different industries"

    def test_framework_categories(self):
        """All frameworks should have category 'framework'."""
        for framework in SAMPLE_FRAMEWORKS:
            assert framework["category"] == "framework"

    def test_expertise_categories(self):
        """All expertise items should have category 'expertise'."""
        for expertise in SAMPLE_EXPERTISE:
            assert expertise["category"] == "expertise"

    def test_engagement_team_members_not_empty(self):
        """Each engagement should have at least one team member."""
        for engagement in SAMPLE_ENGAGEMENTS:
            assert len(engagement["team_members"]) >= 1

    def test_framework_tags_not_empty(self):
        """Each framework should have at least one tag."""
        for framework in SAMPLE_FRAMEWORKS:
            assert len(framework["tags"]) >= 1

    def test_engagement_status_values(self):
        """Engagement status should be valid."""
        valid_statuses = ["completed", "in_progress", "planned"]
        for engagement in SAMPLE_ENGAGEMENTS:
            assert engagement["status"] in valid_statuses


class TestSeedDataIntegrity:
    """Tests for seed data loaded into database."""

    async def test_seed_engagements_to_db(self, db_session: AsyncSession):
        """Should be able to create engagements from seed data."""
        for eng_data in SAMPLE_ENGAGEMENTS[:3]:  # Test subset
            engagement = Engagement(
                id=str(uuid.uuid4()),
                client_name=eng_data["client_name"],
                client_industry=eng_data["client_industry"],
                engagement_type=eng_data["engagement_type"],
                description=eng_data["description"],
                outcomes=eng_data["outcomes"],
                team_members=eng_data["team_members"],
                frameworks_used=eng_data["frameworks_used"],
                status=eng_data["status"],
            )
            db_session.add(engagement)
        
        await db_session.flush()
        
        # Verify insertion
        result = await db_session.execute(select(func.count(Engagement.id)))
        count = result.scalar()
        assert count >= 3

    async def test_seed_frameworks_to_db(self, db_session: AsyncSession):
        """Should be able to create frameworks from seed data."""
        for fw_data in SAMPLE_FRAMEWORKS[:3]:  # Test subset
            item = KnowledgeItem(
                id=str(uuid.uuid4()),
                title=fw_data["title"],
                content=fw_data["content"],
                category=fw_data["category"],
                industry=fw_data.get("industry"),
                tags=fw_data["tags"],
            )
            db_session.add(item)
        
        await db_session.flush()
        
        # Verify insertion
        result = await db_session.execute(
            select(func.count(KnowledgeItem.id)).where(
                KnowledgeItem.category == "framework"
            )
        )
        count = result.scalar()
        assert count >= 3

    async def test_seed_expertise_to_db(self, db_session: AsyncSession):
        """Should be able to create expertise from seed data."""
        for exp_data in SAMPLE_EXPERTISE[:3]:  # Test subset
            item = KnowledgeItem(
                id=str(uuid.uuid4()),
                title=exp_data["title"],
                content=exp_data["content"],
                category=exp_data["category"],
                industry=exp_data.get("industry"),
                tags=exp_data["tags"],
            )
            db_session.add(item)
        
        await db_session.flush()
        
        # Verify insertion
        result = await db_session.execute(
            select(func.count(KnowledgeItem.id)).where(
                KnowledgeItem.category == "expertise"
            )
        )
        count = result.scalar()
        assert count >= 3

    async def test_engagement_query_by_industry(self, db_session: AsyncSession):
        """Should be able to query engagements by industry."""
        # Insert test engagements
        for eng_data in SAMPLE_ENGAGEMENTS:
            engagement = Engagement(
                id=str(uuid.uuid4()),
                client_name=eng_data["client_name"],
                client_industry=eng_data["client_industry"],
                engagement_type=eng_data["engagement_type"],
                description=eng_data["description"],
                status=eng_data["status"],
            )
            db_session.add(engagement)
        await db_session.flush()

        # Query by Manufacturing industry
        result = await db_session.execute(
            select(Engagement).where(Engagement.client_industry == "Manufacturing")
        )
        manufacturing_engagements = result.scalars().all()
        assert len(manufacturing_engagements) >= 1

    async def test_knowledge_query_by_category(self, db_session: AsyncSession):
        """Should be able to query knowledge items by category."""
        # Insert test frameworks
        for fw_data in SAMPLE_FRAMEWORKS:
            item = KnowledgeItem(
                id=str(uuid.uuid4()),
                title=fw_data["title"],
                content=fw_data["content"],
                category=fw_data["category"],
                tags=fw_data["tags"],
            )
            db_session.add(item)
        await db_session.flush()

        # Query frameworks
        result = await db_session.execute(
            select(KnowledgeItem).where(KnowledgeItem.category == "framework")
        )
        frameworks = result.scalars().all()
        assert len(frameworks) == 10


class TestSeedDataContent:
    """Tests for seed data content quality."""

    def test_engagement_descriptions_not_empty(self):
        """Engagement descriptions should not be empty."""
        for engagement in SAMPLE_ENGAGEMENTS:
            assert len(engagement["description"]) >= 50

    def test_framework_content_meaningful(self):
        """Framework content should be substantial."""
        for framework in SAMPLE_FRAMEWORKS:
            assert len(framework["content"]) >= 100

    def test_expertise_content_meaningful(self):
        """Expertise content should be substantial."""
        for expertise in SAMPLE_EXPERTISE:
            assert len(expertise["content"]) >= 50

    def test_engagement_outcomes_present(self):
        """All engagements should have outcomes documented."""
        for engagement in SAMPLE_ENGAGEMENTS:
            assert len(engagement["outcomes"]) >= 20

    def test_framework_titles_unique(self):
        """Framework titles should be unique."""
        titles = [fw["title"] for fw in SAMPLE_FRAMEWORKS]
        assert len(titles) == len(set(titles))

    def test_engagement_clients_unique(self):
        """Engagement client names should be unique."""
        clients = [eng["client_name"] for eng in SAMPLE_ENGAGEMENTS]
        assert len(clients) == len(set(clients))

    def test_tags_are_lowercase(self):
        """Tags should be lowercase for consistency."""
        for framework in SAMPLE_FRAMEWORKS:
            for tag in framework["tags"]:
                assert tag == tag.lower(), f"Tag '{tag}' should be lowercase"

    def test_engagement_types_variety(self):
        """Engagements should cover various types."""
        types = {eng["engagement_type"] for eng in SAMPLE_ENGAGEMENTS}
        assert len(types) >= 5, "Should have at least 5 different engagement types"
