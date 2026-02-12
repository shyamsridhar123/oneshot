"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


# ============ Chat Schemas ============

class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    content: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""
    title: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
    message_count: int = 0

    class Config:
        from_attributes = True


# ============ Agent Schemas ============

class AgentStatus(BaseModel):
    """Schema for agent status updates."""
    agent_id: str
    agent_type: str
    status: str  # idle, thinking, executing, waiting
    current_task: Optional[str] = None
    progress: Optional[float] = None
    last_activity: datetime


class AgentTraceResponse(BaseModel):
    """Schema for agent trace response."""
    id: str
    agent_name: str
    task_type: Optional[str]
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    tokens_used: int
    error: Optional[str] = None

    class Config:
        from_attributes = True


# ============ Document Schemas ============

class DocumentCreate(BaseModel):
    """Schema for creating a document."""
    title: str
    doc_type: str
    content: str
    format: str = "markdown"
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: str
    title: str
    doc_type: str
    content: str
    format: str
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class ExportRequest(BaseModel):
    """Schema for document export request."""
    format: str = Field(..., pattern="^(pdf|docx|markdown|html)$")


# ============ Knowledge Schemas ============

class KnowledgeSearchRequest(BaseModel):
    """Schema for knowledge search."""
    query: str = Field(..., min_length=1)
    category: Optional[str] = None
    industry: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)


class KnowledgeItemResponse(BaseModel):
    """Schema for knowledge item response."""
    id: str
    title: str
    content: str
    category: str
    industry: Optional[str]
    tags: list[str]
    score: Optional[float] = None

    class Config:
        from_attributes = True


# ============ Research Schemas ============

class ResearchRequest(BaseModel):
    """Schema for research query."""
    query: str = Field(..., min_length=1)
    research_type: str = Field(default="comprehensive")  # comprehensive, quick, deep
    sources: list[str] = Field(default_factory=lambda: ["web", "news", "company"])


class BriefingRequest(BaseModel):
    """Schema for client briefing request."""
    company_name: str
    industry: Optional[str] = None
    focus_areas: list[str] = Field(default_factory=list)


# ============ Content Generation Schemas ============

class ContentRequest(BaseModel):
    """Schema for social media content generation."""
    topic: str
    platforms: list[str] = Field(default_factory=lambda: ["linkedin", "twitter", "instagram"])
    content_type: str = Field(default="post")  # post, thread, campaign, calendar
    additional_context: Optional[str] = None


class ProposalRequest(BaseModel):
    """Schema for proposal generation (legacy, wraps ContentRequest)."""
    client_name: str
    client_industry: str
    engagement_type: str
    scope_description: str
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    additional_context: Optional[str] = None


class ProposalResponse(BaseModel):
    """Schema for proposal response."""
    id: str
    client_name: str
    title: str
    status: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ WebSocket Events ============

class WSEvent(BaseModel):
    """Base schema for WebSocket events."""
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: dict[str, Any]
