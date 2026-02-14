/**
 * Zustand store for global state management.
 * Handles conversations, messages, and agent status.
 */

import { create } from "zustand";
import { devtools, subscribeWithSelector } from "zustand/middleware";
import { useShallow } from "zustand/react/shallow";
import type {
  Conversation,
  Message,
  AgentName,
  AgentStatusType,
  Document,
  Citation,
} from "./types";

// Stable empty arrays to prevent infinite re-renders
export const EMPTY_MESSAGES: Message[] = [];
export const EMPTY_CITATIONS: Citation[] = [];

// ============ Agent State ============

interface AgentState {
  agent_type: AgentName;
  status: AgentStatusType;
  current_task: string | null;
  last_activity: string | null;
  tool_calls: { name: string; type: "tool" | "mcp" }[];
}

const AGENT_NAMES: AgentName[] = [
  "orchestrator",
  "strategist",
  "researcher",
  "analyst",
  "scribe",
  "advisor",
  "memory",
];

function createInitialAgentStates(): Record<AgentName, AgentState> {
  return AGENT_NAMES.reduce(
    (acc, name) => {
      acc[name] = {
        agent_type: name,
        status: "idle",
        current_task: null,
        last_activity: null,
        tool_calls: [],
      };
      return acc;
    },
    {} as Record<AgentName, AgentState>
  );
}

// ============ Store Interface ============

interface OneShotStore {
  // Conversations
  conversations: Conversation[];
  activeConversationId: string | null;
  setConversations: (conversations: Conversation[]) => void;
  addConversation: (conversation: Conversation) => void;
  setActiveConversation: (id: string | null) => void;
  updateConversation: (id: string, updates: Partial<Conversation>) => void;

  // Messages
  messages: Record<string, Message[]>;
  setMessages: (conversationId: string, messages: Message[]) => void;
  addMessage: (conversationId: string, message: Message) => void;
  appendToLastMessage: (conversationId: string, token: string) => void;

  // Agents
  agentStates: Record<AgentName, AgentState>;
  updateAgentStatus: (
    agentName: AgentName,
    status: AgentStatusType,
    task?: string | null
  ) => void;
  addAgentToolCall: (
    agentName: AgentName,
    toolName: string,
    toolType: "tool" | "mcp"
  ) => void;
  resetAgentStates: () => void;

  // Documents
  documents: Document[];
  setDocuments: (documents: Document[]) => void;
  addDocument: (document: Document) => void;

  // UI State
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  isLoading: boolean;
  setLoading: (loading: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;

  // Streaming state
  isStreaming: boolean;
  streamingMessageId: string | null;
  setStreaming: (streaming: boolean, messageId?: string | null) => void;

  // Citations
  citations: Record<string, Citation[]>;  // keyed by conversation ID
  addCitations: (conversationId: string, citations: Citation[]) => void;
  clearCitations: (conversationId: string) => void;
}

export const useStore = create<OneShotStore>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // ============ Conversations ============
      conversations: [],
      activeConversationId: null,

      setConversations: (conversations) => set({ conversations }),

      addConversation: (conversation) =>
        set((state) => ({
          conversations: [conversation, ...state.conversations],
        })),

      setActiveConversation: (id) => set({ activeConversationId: id }),

      updateConversation: (id, updates) =>
        set((state) => ({
          conversations: state.conversations.map((c) =>
            c.id === id ? { ...c, ...updates } : c
          ),
        })),

      // ============ Messages ============
      messages: {},

      setMessages: (conversationId, messages) =>
        set((state) => ({
          messages: { ...state.messages, [conversationId]: messages },
        })),

      addMessage: (conversationId, message) =>
        set((state) => ({
          messages: {
            ...state.messages,
            [conversationId]: [
              ...(state.messages[conversationId] || []),
              message,
            ],
          },
        })),

      appendToLastMessage: (conversationId, token) =>
        set((state) => {
          const msgs = state.messages[conversationId];
          if (!msgs || msgs.length === 0) return state;

          const updated = [...msgs];
          const lastIdx = updated.length - 1;
          updated[lastIdx] = {
            ...updated[lastIdx],
            content: updated[lastIdx].content + token,
          };

          return {
            messages: { ...state.messages, [conversationId]: updated },
          };
        }),

      // ============ Agents ============
      agentStates: createInitialAgentStates(),

      updateAgentStatus: (agentName, status, task = null) =>
        set((state) => ({
          agentStates: {
            ...state.agentStates,
            [agentName]: {
              ...state.agentStates[agentName],
              status,
              current_task: task,
              last_activity: new Date().toISOString(),
              // Clear tool_calls when agent goes idle or starts fresh
              tool_calls: status === "idle" ? [] : state.agentStates[agentName].tool_calls,
            },
          },
        })),

      addAgentToolCall: (agentName, toolName, toolType) =>
        set((state) => ({
          agentStates: {
            ...state.agentStates,
            [agentName]: {
              ...state.agentStates[agentName],
              tool_calls: [
                ...state.agentStates[agentName].tool_calls,
                { name: toolName, type: toolType },
              ],
            },
          },
        })),

      resetAgentStates: () => set({ agentStates: createInitialAgentStates() }),

      // ============ Documents ============
      documents: [],
      setDocuments: (documents) => set({ documents }),
      addDocument: (document) =>
        set((state) => ({ documents: [document, ...state.documents] })),

      // ============ UI State ============
      isSidebarOpen: true,
      toggleSidebar: () =>
        set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

      isLoading: false,
      setLoading: (loading) => set({ isLoading: loading }),

      error: null,
      setError: (error) => set({ error }),

      // ============ Streaming ============
      isStreaming: false,
      streamingMessageId: null,
      setStreaming: (streaming, messageId = null) =>
        set({ isStreaming: streaming, streamingMessageId: messageId }),

      // ============ Citations ============
      citations: {},

      addCitations: (conversationId, newCitations) =>
        set((state) => {
          const existing = state.citations[conversationId] || [];
          // Deduplicate by URL
          const seen = new Set(existing.map((c) => c.url).filter(Boolean));
          const unique = newCitations.filter(
            (c) => !c.url || !seen.has(c.url)
          );
          return {
            citations: {
              ...state.citations,
              [conversationId]: [...existing, ...unique],
            },
          };
        }),

      clearCitations: (conversationId) =>
        set((state) => ({
          citations: { ...state.citations, [conversationId]: [] },
        })),
    }))
  )
);

// ============ Selectors ============

export const selectActiveConversation = (state: OneShotStore) =>
  state.conversations.find((c) => c.id === state.activeConversationId);

export const selectActiveMessages = (state: OneShotStore): Message[] =>
  state.activeConversationId
    ? state.messages[state.activeConversationId] || EMPTY_MESSAGES
    : EMPTY_MESSAGES;

export const selectActiveAgents = (state: OneShotStore) =>
  Object.values(state.agentStates).filter((a) => a.status !== "idle");

export const selectActiveCitations = (state: OneShotStore): Citation[] =>
  state.activeConversationId
    ? state.citations[state.activeConversationId] || EMPTY_CITATIONS
    : EMPTY_CITATIONS;

// Re-export useShallow for components
export { useShallow };
