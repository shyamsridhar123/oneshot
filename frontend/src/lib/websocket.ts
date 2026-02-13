/**
 * WebSocket handler for real-time agent updates.
 * Connects to backend /ws/agents/{conversation_id} endpoint.
 */

import type {
  WSEvent,
  WSEventType,
  AgentStartedEvent,
  AgentThinkingEvent,
  AgentCompletedEvent,
  AgentHandoffEvent,
  AgentToolCallEvent,
  StreamTokenEvent,
  DocumentGeneratedEvent,
  AgentCitationsEvent,
  ResponseCitationsEvent,
  AgentName,
} from "./types";
import { useStore } from "./store";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

type EventHandler<T = unknown> = (data: T) => void;

interface WSHandlers {
  onAgentStarted?: EventHandler<AgentStartedEvent>;
  onAgentThinking?: EventHandler<AgentThinkingEvent>;
  onAgentCompleted?: EventHandler<AgentCompletedEvent>;
  onAgentHandoff?: EventHandler<AgentHandoffEvent>;
  onAgentToolCall?: EventHandler<AgentToolCallEvent>;
  onAgentError?: EventHandler<{ agent_name: AgentName; error: string }>;
  onAgentCitations?: EventHandler<AgentCitationsEvent>;
  onResponseCitations?: EventHandler<ResponseCitationsEvent>;
  onStreamToken?: EventHandler<StreamTokenEvent>;
  onDocumentGenerated?: EventHandler<DocumentGeneratedEvent>;
  onConnectionEstablished?: EventHandler<void>;
  onConnectionError?: EventHandler<{ error: string }>;
  onClose?: EventHandler<void>;
}

class AgentWebSocket {
  private ws: WebSocket | null = null;
  private conversationId: string | null = null;
  private handlers: WSHandlers = {};
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;

  connect(conversationId: string, handlers: WSHandlers = {}): void {
    this.disconnect();
    this.conversationId = conversationId;
    this.handlers = handlers;
    this.reconnectAttempts = 0;
    this.createConnection();
  }

  private createConnection(): void {
    if (!this.conversationId) return;

    const url = `${WS_BASE}/ws/agents/${this.conversationId}`;
    
    try {
      this.ws = new WebSocket(url);
    } catch (error) {
      console.error(`[WS] Failed to create WebSocket connection to ${url}:`, error);
      this.handlers.onConnectionError?.({ error: "Failed to create WebSocket connection" });
      return;
    }

    this.ws.onopen = () => {
      console.log("[WS] Connected to", url);
      this.reconnectAttempts = 0;
      this.handlers.onConnectionEstablished?.();
    };

    this.ws.onmessage = (event) => {
      try {
        const wsEvent = JSON.parse(event.data) as WSEvent;
        this.handleEvent(wsEvent);
      } catch (error) {
        console.error("[WS] Failed to parse message:", error);
      }
    };

    this.ws.onerror = () => {
      // WebSocket onerror provides an Event, not Error - check readyState for context
      const state = this.ws?.readyState;
      const stateNames = ["CONNECTING", "OPEN", "CLOSING", "CLOSED"];
      const stateName = state !== undefined ? stateNames[state] : "UNKNOWN";
      console.error(
        `[WS] Connection error to ${url} (state: ${stateName}). ` +
        `Is the backend running at ${WS_BASE}?`
      );
      this.handlers.onConnectionError?.({ 
        error: `WebSocket connection failed (state: ${stateName}). Ensure backend is running.` 
      });
    };

    this.ws.onclose = (event) => {
      const reason = event.reason || "No reason provided";
      const wasClean = event.wasClean ? "clean" : "unclean";
      console.log(`[WS] Connection closed (${wasClean}, code: ${event.code}, reason: ${reason})`);
      this.handlers.onClose?.();
      this.attemptReconnect();
    };
  }

  private handleEvent(event: WSEvent): void {
    const store = useStore.getState();

    switch (event.event_type as WSEventType) {
      case "agent.started": {
        const data = event.data as AgentStartedEvent;
        store.updateAgentStatus(data.agent_name, "executing", data.task);
        this.handlers.onAgentStarted?.(data);
        break;
      }

      case "agent.thinking": {
        const data = event.data as AgentThinkingEvent;
        store.updateAgentStatus(data.agent_name, "thinking", data.thought);
        this.handlers.onAgentThinking?.(data);
        break;
      }

      case "agent.completed": {
        const data = event.data as AgentCompletedEvent;
        store.updateAgentStatus(data.agent_name, "completed");
        this.handlers.onAgentCompleted?.(data);
        break;
      }

      case "agent.handoff": {
        const data = event.data as AgentHandoffEvent;
        // Keep orchestrator as "waiting" while coordinating, only set other agents to idle
        if (data.from_agent === "orchestrator") {
          store.updateAgentStatus(data.from_agent, "waiting", "Coordinating agents...");
        } else {
          store.updateAgentStatus(data.from_agent, "idle");
        }
        store.updateAgentStatus(data.to_agent, "waiting", data.context);
        this.handlers.onAgentHandoff?.(data);
        break;
      }

      case "agent.tool_call": {
        const data = event.data as AgentToolCallEvent;
        store.addAgentToolCall(data.agent_name, data.tool, data.tool_type);
        this.handlers.onAgentToolCall?.(data);
        break;
      }

      case "agent.error": {
        const data = event.data as { agent_name: AgentName; error: string };
        store.updateAgentStatus(data.agent_name, "error");
        this.handlers.onAgentError?.(data);
        break;
      }

      case "stream.token": {
        const data = event.data as StreamTokenEvent;
        if (store.activeConversationId) {
          store.appendToLastMessage(store.activeConversationId, data.token);
        }
        this.handlers.onStreamToken?.(data);
        break;
      }

      case "document.generated": {
        const data = event.data as DocumentGeneratedEvent;
        this.handlers.onDocumentGenerated?.(data);
        break;
      }

      case "agent.citations": {
        const data = event.data as AgentCitationsEvent;
        if (this.conversationId) {
          store.addCitations(this.conversationId, data.citations);
        }
        this.handlers.onAgentCitations?.(data);
        break;
      }

      case "response.citations": {
        const data = event.data as ResponseCitationsEvent;
        if (this.conversationId) {
          store.addCitations(this.conversationId, data.citations);
        }
        this.handlers.onResponseCitations?.(data);
        break;
      }

      case "connection.established":
        this.handlers.onConnectionEstablished?.();
        break;

      case "connection.error": {
        const data = event.data as { error: string };
        this.handlers.onConnectionError?.(data);
        break;
      }

      default:
        console.warn("[WS] Unknown event type:", event.event_type);
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log("[WS] Max reconnect attempts reached");
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);

    console.log(`[WS] Attempting reconnect ${this.reconnectAttempts} in ${delay}ms`);

    this.reconnectTimeout = setTimeout(() => {
      this.createConnection();
    }, delay);
  }

  disconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.conversationId = null;
    useStore.getState().resetAgentStates();
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  getConversationId(): string | null {
    return this.conversationId;
  }
}

// Singleton instance
export const agentWs = new AgentWebSocket();

// React hook for WebSocket connection
import { useEffect, useRef } from "react";

export function useAgentWebSocket(
  conversationId: string | null,
  handlers: WSHandlers = {}
) {
  const handlersRef = useRef(handlers);
  handlersRef.current = handlers;

  useEffect(() => {
    if (!conversationId) {
      agentWs.disconnect();
      return;
    }

    agentWs.connect(conversationId, handlersRef.current);

    return () => {
      // Don't disconnect on cleanup - let it persist across re-renders
    };
  }, [conversationId]);

  return {
    isConnected: agentWs.isConnected(),
    disconnect: () => agentWs.disconnect(),
  };
}
