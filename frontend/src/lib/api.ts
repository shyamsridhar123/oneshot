/**
 * API client for backend communication.
 * All functions return typed responses matching backend schemas.
 */

import type {
  Conversation,
  ConversationCreate,
  Message,
  MessageCreate,
  Document,
  ProposalRequest,
  KnowledgeItem,
  KnowledgeSearchRequest,
  ResearchRequest,
  BriefingRequest,
  AgentTrace,
  Metrics,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchJson<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new ApiError(response.status, error);
  }

  return response.json();
}

// ============ Chat API ============

export const chatApi = {
  listConversations: (limit = 20, offset = 0) =>
    fetchJson<Conversation[]>(
      `/api/chat/conversations?limit=${limit}&offset=${offset}`
    ),

  createConversation: (data: ConversationCreate) =>
    fetchJson<Conversation>("/api/chat/conversations", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getConversation: (id: string) =>
    fetchJson<Conversation>(`/api/chat/conversations/${id}`),

  listMessages: (conversationId: string, limit = 50, offset = 0) =>
    fetchJson<Message[]>(
      `/api/chat/conversations/${conversationId}/messages?limit=${limit}&offset=${offset}`
    ),

  sendMessage: (conversationId: string, data: MessageCreate) =>
    fetchJson<Message>(
      `/api/chat/conversations/${conversationId}/messages`,
      {
        method: "POST",
        body: JSON.stringify(data),
      }
    ),
};

// ============ Proposals API ============

export const proposalsApi = {
  list: (limit = 20, offset = 0) =>
    fetchJson<Document[]>(`/api/proposals?limit=${limit}&offset=${offset}`),

  get: (id: string) => fetchJson<Document>(`/api/proposals/${id}`),

  generate: (data: ProposalRequest) =>
    fetchJson<Document>("/api/proposals/generate", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// ============ Research API ============

export const researchApi = {
  query: (data: ResearchRequest) =>
    fetchJson<{ query: string; status: string; message: string }>(
      "/api/research/query",
      {
        method: "POST",
        body: JSON.stringify(data),
      }
    ),

  briefing: (data: BriefingRequest) =>
    fetchJson<{ company_name: string; status: string; message: string }>(
      "/api/research/briefing",
      {
        method: "POST",
        body: JSON.stringify(data),
      }
    ),
};

// ============ Documents API ============

export const documentsApi = {
  list: (docType?: string, limit = 20, offset = 0) => {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (docType) params.set("doc_type", docType);
    return fetchJson<Document[]>(`/api/documents?${params}`);
  },

  get: (id: string) => fetchJson<Document>(`/api/documents/${id}`),

  export: (id: string, format: "pdf" | "docx" | "markdown" | "html") =>
    fetch(`${API_BASE}/api/documents/${id}/export`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ format }),
    }),
};

// ============ Knowledge API ============

export const knowledgeApi = {
  search: (data: KnowledgeSearchRequest) =>
    fetchJson<KnowledgeItem[]>("/api/knowledge/search", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  list: (category?: string, limit = 20, offset = 0) => {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (category) params.set("category", category);
    return fetchJson<KnowledgeItem[]>(`/api/knowledge?${params}`);
  },

  get: (id: string) => fetchJson<KnowledgeItem>(`/api/knowledge/${id}`),
};

// ============ Analytics API ============

export const analyticsApi = {
  traces: (agentName?: string, status?: string, limit = 50, offset = 0) => {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (agentName) params.set("agent_name", agentName);
    if (status) params.set("status", status);
    return fetchJson<AgentTrace[]>(`/api/analytics/traces?${params}`);
  },

  metrics: (period: "day" | "week" | "month" = "day") =>
    fetchJson<Metrics>(`/api/analytics/metrics?period=${period}`),
};

export { ApiError };
