/**
 * TypeScript types matching backend Pydantic schemas.
 * Keep in sync with backend/app/models/schemas.py
 */

// ============ Chat Types ============

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface MessageCreate {
  content: string;
  metadata?: Record<string, unknown>;
}

export interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
  message_count: number;
}

export interface ConversationCreate {
  title?: string;
  metadata?: Record<string, unknown>;
}

// ============ Agent Types ============

export type AgentName =
  | "orchestrator"
  | "strategist"
  | "researcher"
  | "analyst"
  | "scribe"
  | "advisor"
  | "memory";

export type AgentStatusType =
  | "idle"
  | "thinking"
  | "executing"
  | "waiting"
  | "completed"
  | "error";

export interface AgentStatus {
  agent_id: string;
  agent_type: AgentName;
  status: AgentStatusType;
  current_task: string | null;
  progress: number | null;
  last_activity: string;
}

export interface AgentTrace {
  id: string;
  agent_name: AgentName;
  task_type: string | null;
  status: string;
  started_at: string;
  completed_at: string | null;
  tokens_used: number;
  error: string | null;
}

// ============ Document Types ============

export interface Document {
  id: string;
  title: string;
  doc_type: string;
  content: string;
  format: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface DocumentCreate {
  title: string;
  doc_type: string;
  content: string;
  format?: string;
  metadata?: Record<string, unknown>;
}

// ============ Knowledge Types ============

export interface KnowledgeItem {
  id: string;
  title: string;
  content: string;
  category: string;
  industry: string | null;
  tags: string[];
  score?: number;
}

export interface KnowledgeSearchRequest {
  query: string;
  category?: string;
  industry?: string;
  limit?: number;
}

// ============ Research Types ============

export interface ResearchRequest {
  query: string;
  research_type?: "comprehensive" | "quick" | "deep";
  sources?: string[];
}

export interface BriefingRequest {
  company_name: string;
  industry?: string;
  focus_areas?: string[];
}

// ============ Proposal Types ============

export interface ProposalRequest {
  client_name: string;
  client_industry: string;
  engagement_type: string;
  scope_description: string;
  budget_range?: string;
  timeline?: string;
  additional_context?: string;
}

// ============ WebSocket Event Types ============

export type WSEventType =
  | "agent.started"
  | "agent.thinking"
  | "agent.completed"
  | "agent.handoff"
  | "agent.error"
  | "agent.tool_call"
  | "stream.token"
  | "document.generated"
  | "connection.established"
  | "connection.error";

export interface WSEvent<T = unknown> {
  event_type: WSEventType;
  timestamp: string;
  data: T;
}

export interface AgentStartedEvent {
  agent_name: AgentName;
  task: string;
}

export interface AgentThinkingEvent {
  agent_name: AgentName;
  thought: string;
}

export interface AgentCompletedEvent {
  agent_name: AgentName;
  result: string;
  tokens_used?: number;
}

export interface AgentHandoffEvent {
  from_agent: AgentName;
  to_agent: AgentName;
  context: string;
}

export interface StreamTokenEvent {
  token: string;
  agent_name: AgentName;
}

export interface DocumentGeneratedEvent {
  document_id: string;
  doc_type: string;
  title: string;
}

export interface AgentToolCallEvent {
  agent_name: AgentName;
  tool: string;
  tool_type: "tool" | "mcp";
}

// ============ Analytics Types ============

export interface AgentStats {
  agent: AgentName;
  executions: number;
  avg_tokens: number;
}

export interface Metrics {
  period: string;
  since: string;
  agent_stats: AgentStats[];
  total_executions: number;
}
