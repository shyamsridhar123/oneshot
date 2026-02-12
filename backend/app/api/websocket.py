"""WebSocket handler for real-time agent updates."""

import json
from datetime import datetime
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

websocket_router = APIRouter()

# TODO: REVISIT IF NEEDED - Using parameterized path /ws/agents/{conversation_id}
# vs TRD's /ws/agents. The parameterized path is correct per implementation,
# but if clients have trouble with parameterized WS paths, consider switching
# to query params: /ws/agents?conversation_id=xxx


class ConnectionManager:
    """Manage WebSocket connections by conversation."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str):
        """Accept and track a new connection."""
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = set()
        self.active_connections[conversation_id].add(websocket)

    def disconnect(self, websocket: WebSocket, conversation_id: str):
        """Remove a connection."""
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].discard(websocket)
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]

    async def broadcast(self, conversation_id: str, event_type: str, data: dict):
        """Broadcast an event to all connections for a conversation."""
        if conversation_id not in self.active_connections:
            return

        message = json.dumps({
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        })

        dead_connections = set()
        for connection in self.active_connections[conversation_id]:
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.add(connection)

        # Clean up dead connections
        for conn in dead_connections:
            self.active_connections[conversation_id].discard(conn)

    async def send_agent_started(self, conversation_id: str, agent: str, task: str):
        """Send agent.started event."""
        await self.broadcast(conversation_id, "agent.started", {
            "agent_name": agent,
            "task": task,
        })

    async def send_agent_thinking(self, conversation_id: str, agent: str, thought: str, progress: float = None):
        """Send agent.thinking event."""
        await self.broadcast(conversation_id, "agent.thinking", {
            "agent_name": agent,
            "thought": thought,
            "progress": progress,
        })

    async def send_agent_completed(self, conversation_id: str, agent: str, result_summary: str, duration_ms: int):
        """Send agent.completed event."""
        await self.broadcast(conversation_id, "agent.completed", {
            "agent_name": agent,
            "result_summary": result_summary,
            "duration_ms": duration_ms,
        })

    async def send_agent_handoff(self, conversation_id: str, from_agent: str, to_agent: str, context: str):
        """Send agent.handoff event."""
        await self.broadcast(conversation_id, "agent.handoff", {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "context": context,
        })

    async def send_agent_tool_call(self, conversation_id: str, agent: str, tool_name: str, tool_type: str = "tool"):
        """Send agent.tool_call event when an agent invokes a tool or MCP server."""
        await self.broadcast(conversation_id, "agent.tool_call", {
            "agent_name": agent,
            "tool": tool_name,
            "tool_type": tool_type,
        })

    async def send_stream_token(self, conversation_id: str, agent: str, token: str):
        """Send stream.token event for streaming responses."""
        await self.broadcast(conversation_id, "stream.token", {
            "agent_name": agent,
            "token": token,
        })

    async def send_document_generated(self, conversation_id: str, document_id: str, doc_type: str, title: str):
        """Send document.generated event."""
        await self.broadcast(conversation_id, "document.generated", {
            "document_id": document_id,
            "type": doc_type,
            "title": title,
        })


# Global connection manager instance
manager = ConnectionManager()


@websocket_router.websocket("/ws/agents/{conversation_id}")
async def agent_updates(websocket: WebSocket, conversation_id: str):
    """WebSocket endpoint for real-time agent updates."""
    await manager.connect(websocket, conversation_id)
    try:
        while True:
            # Keep connection alive, handle any client messages
            data = await websocket.receive_text()
            # Could handle ping/pong or client commands here
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
