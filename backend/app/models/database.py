"""SQLAlchemy database models for OneShot."""

import uuid
from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Float, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import relationship, DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


# ============ Core Entities ============

class Conversation(Base):
    """Chat conversation container."""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default=dict)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Individual message in a conversation."""
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default=dict)

    conversation = relationship("Conversation", back_populates="messages")
    agent_traces = relationship("AgentTrace", back_populates="message", cascade="all, delete-orphan")


# ============ Agent Tracing ============

class AgentTrace(Base):
    """Record of agent execution for observability."""
    __tablename__ = "agent_traces"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("messages.id"), nullable=True)
    agent_name = Column(String, nullable=False)
    task_type = Column(String, nullable=True)
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, default="running")  # running, completed, failed
    error = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0)

    # Citation and tracing fields
    citations = Column(JSON, default=list)       # Structured citation/source data
    tool_calls = Column(JSON, default=list)      # Tool invocation log with inputs/outputs
    duration_ms = Column(Integer, nullable=True)  # Execution time in milliseconds
    parent_trace_id = Column(String, ForeignKey("agent_traces.id"), nullable=True)

    message = relationship("Message", back_populates="agent_traces")
    parent_trace = relationship("AgentTrace", remote_side=[id], backref="child_traces")


# ============ Documents ============

class Document(Base):
    """Generated document (proposal, briefing, etc.)."""
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=True)
    title = Column(String, nullable=False)
    doc_type = Column(String, nullable=False)  # proposal, briefing, analysis, presentation
    content = Column(Text, nullable=False)  # Markdown or structured content
    format = Column(String, default="markdown")  # markdown, html, json
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default=dict)


# ============ Knowledge Base ============

class KnowledgeItem(Base):
    """Knowledge base item with embedding for semantic search."""
    __tablename__ = "knowledge_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # engagement, framework, template, expertise
    industry = Column(String, nullable=True)
    tags = Column(JSON, default=list)
    embedding = Column(JSON, nullable=True)  # Stored as list of floats
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default=dict)


class Engagement(Base):
    """Past engagement record for reference."""
    __tablename__ = "engagements"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_name = Column(String, nullable=False)
    client_industry = Column(String, nullable=False)
    engagement_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    outcomes = Column(Text, nullable=True)
    team_members = Column(JSON, default=list)
    frameworks_used = Column(JSON, default=list)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String, default="completed")
    embedding = Column(JSON, nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)


# ============ Analytics ============

class Metric(Base):
    """Performance and usage metrics."""
    __tablename__ = "metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    dimensions = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)


# ============ Database Setup ============

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
