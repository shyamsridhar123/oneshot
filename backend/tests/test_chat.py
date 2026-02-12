"""Tests for chat API endpoints."""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Conversation, Message
from app.models.schemas import ConversationResponse, MessageResponse


class TestListConversations:
    """Tests for GET /api/chat/conversations endpoint."""

    async def test_list_conversations_empty(self, client: AsyncClient):
        """Should return empty list when no conversations exist."""
        response = await client.get("/api/chat/conversations")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_conversations_with_data(
        self, client: AsyncClient, sample_conversation: Conversation
    ):
        """Should return list of conversations."""
        response = await client.get("/api/chat/conversations")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["id"] == sample_conversation.id

    async def test_list_conversations_schema_validation(
        self, client: AsyncClient, sample_conversation: Conversation
    ):
        """Response should match ConversationResponse schema."""
        response = await client.get("/api/chat/conversations")
        data = response.json()
        # Validate each item matches schema
        for item in data:
            ConversationResponse.model_validate(item)

    async def test_list_conversations_pagination(
        self, client: AsyncClient, sample_conversation: Conversation
    ):
        """Should support limit and offset parameters."""
        response = await client.get("/api/chat/conversations?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCreateConversation:
    """Tests for POST /api/chat/conversations endpoint."""

    async def test_create_conversation_success(self, client: AsyncClient):
        """Should create a new conversation."""
        payload = {"title": "Test Conversation", "metadata": {"test": True}}
        response = await client.post("/api/chat/conversations", json=payload)
        assert response.status_code == 200

    async def test_create_conversation_returns_id(self, client: AsyncClient):
        """Created conversation should have valid UUID id."""
        payload = {"title": "New Conversation"}
        response = await client.post("/api/chat/conversations", json=payload)
        data = response.json()
        assert "id" in data
        uuid.UUID(data["id"])  # Validates UUID format

    async def test_create_conversation_schema_validation(self, client: AsyncClient):
        """Response should match ConversationResponse schema."""
        payload = {"title": "Schema Test"}
        response = await client.post("/api/chat/conversations", json=payload)
        data = response.json()
        ConversationResponse.model_validate(data)

    async def test_create_conversation_without_title(self, client: AsyncClient):
        """Should create conversation even without title."""
        payload = {"metadata": {"optional": True}}
        response = await client.post("/api/chat/conversations", json=payload)
        assert response.status_code == 200

    async def test_create_conversation_with_metadata(self, client: AsyncClient):
        """Should preserve metadata in created conversation."""
        payload = {"title": "Meta Test", "metadata": {"key": "value"}}
        response = await client.post("/api/chat/conversations", json=payload)
        data = response.json()
        assert data["metadata"]["key"] == "value"


class TestGetConversation:
    """Tests for GET /api/chat/conversations/{id} endpoint."""

    async def test_get_conversation_success(
        self, client: AsyncClient, sample_conversation: Conversation
    ):
        """Should return specific conversation by id."""
        response = await client.get(f"/api/chat/conversations/{sample_conversation.id}")
        assert response.status_code == 200

    async def test_get_conversation_correct_data(
        self, client: AsyncClient, sample_conversation: Conversation
    ):
        """Returned conversation should have correct data."""
        response = await client.get(f"/api/chat/conversations/{sample_conversation.id}")
        data = response.json()
        assert data["id"] == sample_conversation.id
        assert data["title"] == sample_conversation.title

    async def test_get_conversation_schema_validation(
        self, client: AsyncClient, sample_conversation: Conversation
    ):
        """Response should match ConversationResponse schema."""
        response = await client.get(f"/api/chat/conversations/{sample_conversation.id}")
        data = response.json()
        ConversationResponse.model_validate(data)

    async def test_get_conversation_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent conversation."""
        fake_id = str(uuid.uuid4())
        response = await client.get(f"/api/chat/conversations/{fake_id}")
        assert response.status_code == 404

    async def test_get_conversation_invalid_id_format(self, client: AsyncClient):
        """Should handle invalid id format gracefully."""
        response = await client.get("/api/chat/conversations/invalid-id-format")
        assert response.status_code == 404


class TestListMessages:
    """Tests for GET /api/chat/conversations/{id}/messages endpoint."""

    async def test_list_messages_empty(
        self, client: AsyncClient, sample_conversation: Conversation
    ):
        """Should return empty list when no messages exist."""
        response = await client.get(f"/api/chat/conversations/{sample_conversation.id}/messages")
        # Note: sample_conversation fixture may not have messages
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_list_messages_with_data(
        self, client: AsyncClient, sample_message: Message
    ):
        """Should return list of messages in conversation."""
        response = await client.get(
            f"/api/chat/conversations/{sample_message.conversation_id}/messages"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_list_messages_schema_validation(
        self, client: AsyncClient, sample_message: Message
    ):
        """Response should match MessageResponse schema."""
        response = await client.get(
            f"/api/chat/conversations/{sample_message.conversation_id}/messages"
        )
        data = response.json()
        for item in data:
            MessageResponse.model_validate(item)

    async def test_list_messages_pagination(
        self, client: AsyncClient, sample_message: Message
    ):
        """Should support limit and offset parameters."""
        response = await client.get(
            f"/api/chat/conversations/{sample_message.conversation_id}/messages?limit=10&offset=0"
        )
        assert response.status_code == 200


class TestSendMessage:
    """Tests for POST /api/chat/conversations/{id}/messages endpoint."""

    async def test_send_message_validation_empty_content(self, client: AsyncClient):
        """Should reject empty message content."""
        conv_id = str(uuid.uuid4())
        payload = {"content": "", "metadata": {}}
        response = await client.post(
            f"/api/chat/conversations/{conv_id}/messages", json=payload
        )
        assert response.status_code == 422  # Validation error

    async def test_send_message_creates_conversation(self, client: AsyncClient):
        """Should auto-create conversation if not exists."""
        conv_id = str(uuid.uuid4())
        payload = {"content": "Hello, this is a test message.", "metadata": {}}
        response = await client.post(
            f"/api/chat/conversations/{conv_id}/messages", json=payload
        )
        assert response.status_code == 200

    async def test_send_message_schema_validation(
        self, client: AsyncClient, sample_conversation: Conversation
    ):
        """Response should match MessageResponse schema if successful."""
        payload = {"content": "Test message for schema validation.", "metadata": {}}
        response = await client.post(
            f"/api/chat/conversations/{sample_conversation.id}/messages",
            json=payload,
        )
        assert response.status_code == 200
        data = response.json()
        MessageResponse.model_validate(data)
