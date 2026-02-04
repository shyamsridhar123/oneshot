"""Chat API routes."""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db, Conversation, Message
from app.models.schemas import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.agents.orchestrator import process_message
from app.api.websocket import manager

router = APIRouter()


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all conversations."""
    result = await db.execute(
        select(Conversation)
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    conversations = result.scalars().all()
    
    response = []
    for conv in conversations:
        msg_count = await db.execute(
            select(func.count(Message.id)).where(Message.conversation_id == conv.id)
        )
        response.append(
            ConversationResponse(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                metadata=conv.metadata_ or {},
                message_count=msg_count.scalar() or 0,
            )
        )
    return response


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new conversation."""
    conversation = Conversation(
        id=str(uuid.uuid4()),
        title=data.title,
        metadata_=data.metadata,
    )
    db.add(conversation)
    await db.flush()
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        metadata=conversation.metadata_ or {},
        message_count=0,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific conversation."""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    msg_count = await db.execute(
        select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
    )
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        metadata=conversation.metadata_ or {},
        message_count=msg_count.scalar() or 0,
    )


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List messages in a conversation."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    messages = result.scalars().all()
    
    return [
        MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
            metadata=msg.metadata_ or {},
        )
        for msg in messages
    ]


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    """Send a message and trigger agent processing."""
    # Verify conversation exists or create it
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        # Auto-create conversation
        conversation = Conversation(
            id=conversation_id,
            title=data.content[:50] + "..." if len(data.content) > 50 else data.content,
        )
        db.add(conversation)
        await db.flush()
    
    # Create user message
    user_message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role="user",
        content=data.content,
        metadata_=data.metadata,
    )
    db.add(user_message)
    await db.flush()
    
    # Process with orchestrator (this triggers agents)
    try:
        response_content = await process_message(
            conversation_id=conversation_id,
            message_content=data.content,
            message_metadata=data.metadata,
            ws_manager=manager,
            db=db,
        )
    except Exception as e:
        response_content = f"I encountered an error processing your request: {str(e)}"
    
    # Create assistant message
    assistant_message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role="assistant",
        content=response_content,
    )
    db.add(assistant_message)
    await db.flush()  # Flush to populate default values like created_at
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    
    return MessageResponse(
        id=assistant_message.id,
        conversation_id=assistant_message.conversation_id,
        role=assistant_message.role,
        content=assistant_message.content,
        created_at=assistant_message.created_at,
        metadata=assistant_message.metadata_ or {},
    )
