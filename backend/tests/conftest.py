"""Pytest configuration and shared fixtures for Federation API tests."""

import asyncio
import pytest
import uuid
from typing import AsyncGenerator
from datetime import datetime

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.models.database import Base, get_db, Conversation, Message, Document, KnowledgeItem, Engagement


# Use test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./data/test_federation.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide test database session with rollback after each test."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide async HTTP client with test database override."""
    
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ============ Test Data Fixtures ============

@pytest.fixture
async def sample_conversation(db_session: AsyncSession) -> Conversation:
    """Create a sample conversation for testing."""
    conversation = Conversation(
        id=str(uuid.uuid4()),
        title="Test Conversation",
        metadata_={"test": True},
    )
    db_session.add(conversation)
    await db_session.flush()
    return conversation


@pytest.fixture
async def sample_message(db_session: AsyncSession, sample_conversation: Conversation) -> Message:
    """Create a sample message for testing."""
    message = Message(
        id=str(uuid.uuid4()),
        conversation_id=sample_conversation.id,
        role="user",
        content="Test message content",
        metadata_={"source": "test"},
    )
    db_session.add(message)
    await db_session.flush()
    return message


@pytest.fixture
async def sample_document(db_session: AsyncSession, sample_conversation: Conversation) -> Document:
    """Create a sample document for testing."""
    document = Document(
        id=str(uuid.uuid4()),
        conversation_id=sample_conversation.id,
        title="Test Proposal",
        doc_type="proposal",
        content="# Test Proposal\n\nThis is a test proposal document.",
        format="markdown",
        metadata_={"client": "Test Client"},
    )
    db_session.add(document)
    await db_session.flush()
    return document


@pytest.fixture
async def sample_knowledge_item(db_session: AsyncSession) -> KnowledgeItem:
    """Create a sample knowledge item for testing."""
    item = KnowledgeItem(
        id=str(uuid.uuid4()),
        title="Digital Transformation Framework",
        content="Framework for digital transformation assessment and implementation.",
        category="framework",
        industry="Technology",
        tags=["digital", "transformation", "framework"],
    )
    db_session.add(item)
    await db_session.flush()
    return item


@pytest.fixture
async def sample_engagement(db_session: AsyncSession) -> Engagement:
    """Create a sample engagement for testing."""
    engagement = Engagement(
        id=str(uuid.uuid4()),
        client_name="Test Corp",
        client_industry="Manufacturing",
        engagement_type="Digital Transformation",
        description="End-to-end digital transformation initiative.",
        outcomes="20% cost reduction, 30% efficiency improvement",
        team_members=["John Partner", "Jane Manager"],
        frameworks_used=["Digital Maturity Assessment"],
        status="completed",
    )
    db_session.add(engagement)
    await db_session.flush()
    return engagement


# ============ Validation Helpers ============

def validate_uuid(value: str) -> bool:
    """Validate that a string is a valid UUID."""
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def validate_datetime_iso(value: str) -> bool:
    """Validate that a string is a valid ISO datetime."""
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False
