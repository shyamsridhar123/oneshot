# Federation API Documentation

> **AI-Powered Professional Services Platform API Reference**

This document provides a comprehensive reference for all Federation REST and WebSocket APIs, explaining how each endpoint integrates with the frontend UX and the underlying agent system.

---

## Table of Contents

1. [Overview](#overview)
2. [Base Configuration](#base-configuration)
3. [Chat API](#chat-api)
4. [Proposals API](#proposals-api)
5. [Research API](#research-api)
6. [Documents API](#documents-api)
7. [Knowledge API](#knowledge-api)
8. [Analytics API](#analytics-api)
9. [WebSocket API](#websocket-api)
10. [Error Handling](#error-handling)
11. [TypeScript Types Reference](#typescript-types-reference)

---

## Overview

The Federation API is a FastAPI-based backend that powers a multi-agent AI platform for professional services. The architecture consists of:

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 14, React Query, Zustand | Interactive UX with real-time updates |
| **Backend** | FastAPI (Python) | REST + WebSocket API server |
| **Agents** | Microsoft Agent Framework | 7 specialized AI agents for task execution |
| **Database** | SQLite + aiosqlite | Async persistent storage |

### Agent Roles

| Agent | Purpose | Triggered By |
|-------|---------|--------------|
| **Orchestrator** | Decomposes tasks, coordinates agents | All user messages |
| **Strategist** | Creates proposals and engagement scopes | Proposal generation |
| **Researcher** | Web search, news, company intelligence | Research queries |
| **Analyst** | Data visualization, financial modeling | Analysis requests |
| **Scribe** | Document generation with branding | Document creation |
| **Advisor** | Client communications, executive summaries | Briefings |
| **Memory** | Knowledge retrieval, RAG patterns | Context lookups |

---

## Base Configuration

### Endpoints

| Environment | REST Base URL | WebSocket URL |
|-------------|---------------|---------------|
| Development | `http://localhost:8000` | `ws://localhost:8000` |
| Production | Configured via `NEXT_PUBLIC_API_URL` | Configured via `NEXT_PUBLIC_WS_URL` |

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Root Endpoint

```http
GET /
```

**Response:**
```json
{
  "name": "Federation API",
  "description": "AI-Powered Professional Services Platform",
  "docs": "/docs"
}
```

---

## Chat API

The Chat API powers the main conversation interface, enabling users to interact with the multi-agent system through natural language.

### UX Integration

The **Chat Interface** (`/` - home page) uses these endpoints to:
- Display the conversation sidebar with history
- Load message history when selecting a conversation
- Send new messages and receive AI agent responses
- Show real-time agent processing status via WebSocket

```
+-------------------------------------------------------------+
|  Conversations Sidebar  |       Chat Messages Area          |
|  ---------------------  |  ------------------------------- |
|  📁 New Conversation    |  👤 User: "Help me with..."      |
|  📁 Previous Chat 1     |  🤖 Assistant: "Based on..."     |
|  📁 Previous Chat 2     |                                   |
|                         |  [Message Input] [Send]           |
+-------------------------------------------------------------+
```

### Endpoints

#### List Conversations

```http
GET /api/chat/conversations
```

Retrieves all conversations for display in the sidebar, ordered by most recent activity.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Maximum conversations to return |
| `offset` | integer | 0 | Pagination offset |

**Response:** `ConversationResponse[]`

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Digital Transformation Strategy",
    "created_at": "2026-02-04T10:30:00Z",
    "updated_at": "2026-02-04T14:22:00Z",
    "metadata": {},
    "message_count": 12
  }
]
```

**UX Context:** Populates the conversation sidebar on the left. Users click items to load that conversation's messages.

---

#### Create Conversation

```http
POST /api/chat/conversations
```

Creates a new empty conversation. Typically called when user clicks the "+" button in the sidebar.

**Request Body:** `ConversationCreate`

```json
{
  "title": "New Client Engagement",
  "metadata": {
    "client_id": "acme-corp"
  }
}
```

**Response:** `ConversationResponse`

**UX Context:** Creates a new conversation entry in the sidebar and sets it as active.

---

#### Get Conversation

```http
GET /api/chat/conversations/{conversation_id}
```

Fetches details for a specific conversation.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `conversation_id` | string (UUID) | Unique conversation identifier |

**Response:** `ConversationResponse`

**Error:** `404` if conversation not found

---

#### List Messages

```http
GET /api/chat/conversations/{conversation_id}/messages
```

Retrieves all messages in a conversation, ordered chronologically (oldest first).

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Maximum messages to return |
| `offset` | integer | 0 | Pagination offset |

**Response:** `MessageResponse[]`

```json
[
  {
    "id": "msg-001",
    "conversation_id": "conv-001",
    "role": "user",
    "content": "Help me prepare a proposal for Acme Corp",
    "created_at": "2026-02-04T10:30:00Z",
    "metadata": {}
  },
  {
    "id": "msg-002",
    "conversation_id": "conv-001",
    "role": "assistant",
    "content": "I'll help you prepare a comprehensive proposal...",
    "created_at": "2026-02-04T10:30:15Z",
    "metadata": {}
  }
]
```

**UX Context:** Loads the message history when a conversation is selected. Messages are displayed as chat bubbles with user messages on the right and assistant responses on the left.

---

#### Send Message

```http
POST /api/chat/conversations/{conversation_id}/messages
```

**This is the primary API for user interaction.** Sends a user message and triggers the agent processing pipeline. The Orchestrator agent receives the message and coordinates other agents as needed.

**Request Body:** `MessageCreate`

```json
{
  "content": "Research the latest AI trends in healthcare and prepare a summary",
  "metadata": {
    "include_sources": true
  }
}
```

**Response:** `MessageResponse`

The response contains the final assistant message after all agent processing completes.

**Processing Flow:**

```
User Message -> Orchestrator -> [Agents Execute] -> Final Response
                    |
                    +-> Researcher (if research needed)
                    +-> Analyst (if analysis needed)
                    +-> Scribe (if document generation)
                    +-> Memory (for context retrieval)
                    +-> Strategist (for proposals)
```

**UX Context:**
1. User types message and presses Enter or clicks Send
2. Optimistic update: User message appears immediately
3. Loading indicator: "Agents are working..."
4. WebSocket receives real-time agent status updates
5. Final response appears as assistant message

**Note:** If `conversation_id` doesn't exist, the API auto-creates the conversation.

---

## Proposals API

The Proposals API enables AI-driven generation of professional consulting proposals. The Strategist and Scribe agents collaborate to create comprehensive proposal documents.

### UX Integration

The **Proposals Page** (`/proposals`) provides:
- Grid view of all generated proposals
- Modal form for generating new proposals
- Export functionality (PDF, DOCX, Markdown, HTML)

```
+-------------------------------------------------------------+
|  Proposals                            [+ Generate Proposal] |
|  ----------------------------------------------------------  |
|  +-------------+ +-------------+ +-------------+            |
|  | Acme Corp   | | TechStart   | | Global Inc  |            |
|  | Digital Tx  | | AI Strategy | | Cloud Migr  |            |
|  | [View]      | | [View]      | | [View]      |            |
|  | [Export]    | | [Export]    | | [Export]    |            |
|  +-------------+ +-------------+ +-------------+            |
+-------------------------------------------------------------+
```

### Endpoints

#### List Proposals

```http
GET /api/proposals
```

Returns all generated proposal documents.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Maximum proposals to return |
| `offset` | integer | 0 | Pagination offset |

**Response:** `DocumentResponse[]`

```json
[
  {
    "id": "prop-001",
    "title": "Acme Corp Digital Transformation Proposal",
    "doc_type": "proposal",
    "content": "# Executive Summary\n\n...",
    "format": "markdown",
    "created_at": "2026-02-04T10:30:00Z",
    "metadata": {
      "client_name": "Acme Corp",
      "engagement_type": "Digital Transformation"
    }
  }
]
```

**UX Context:** Populates the proposals grid on page load. Each card shows title, creation date, and preview of content.

---

#### Get Proposal

```http
GET /api/proposals/{proposal_id}
```

Retrieves a specific proposal for viewing.

**Response:** `DocumentResponse`

**Error:** `404` if proposal not found

---

#### Generate Proposal

```http
POST /api/proposals/generate
```

**Triggers AI agent-driven proposal generation.** The Orchestrator dispatches to Strategist (for strategy), Researcher (for context), and Scribe (for document formatting).

**Request Body:** `ProposalRequest`

```json
{
  "client_name": "Acme Corporation",
  "client_industry": "Technology",
  "engagement_type": "Digital Transformation",
  "scope_description": "End-to-end digital transformation including cloud migration, process automation, and AI integration",
  "budget_range": "$500k - $2M",
  "timeline": "6-12 months",
  "additional_context": "Client is particularly interested in leveraging AI for customer service"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `client_name` | string | ✓ | Client company name |
| `client_industry` | string | ✓ | Industry sector |
| `engagement_type` | string | ✓ | Type of engagement |
| `scope_description` | string | ✓ | Detailed project scope |
| `budget_range` | string | | Expected budget range |
| `timeline` | string | | Project timeline |
| `additional_context` | string | | Extra requirements |

**Response:** `DocumentResponse`

The generated proposal includes:
- Executive Summary
- Scope of Work
- Methodology
- Timeline & Milestones
- Team Structure
- Pricing
- Terms & Conditions

**UX Context:**
1. User fills out the "Generate Proposal" form in the modal
2. Clicks "Generate" → loading spinner appears
3. Agents process the request (may take 30-60 seconds)
4. New proposal card appears in the grid
5. User can view, edit, or export

---

## Research API

The Research API provides AI-powered research capabilities using the Researcher agent to gather intelligence from multiple sources.

### UX Integration

The **Research Page** (`/research`) offers two tabs:
1. **Research Query** - Ad-hoc topic research
2. **Client Briefing** - Company-specific intelligence

```
+-------------------------------------------------------------+
|  Research                                                    |
|  ----------------------------------------------------------  |
|  [Research Query] [Client Briefing]                          |
|                                                              |
|  +--------------------------------------------------------+ |
|  | What would you like to research?                       | |
|  | ______________________________________________________ | |
|  |                                                        | |
|  +--------------------------------------------------------+ |
|                                                              |
|  [Start Research]  Sources: [Web] [News] [Company Data]     |
+-------------------------------------------------------------+
```

### Endpoints

#### Research Query

```http
POST /api/research/query
```

Executes an ad-hoc research query using the Researcher agent.

**Request Body:** `ResearchRequest`

```json
{
  "query": "Latest trends in AI for healthcare diagnostics",
  "research_type": "comprehensive",
  "sources": ["web", "news", "company"]
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | string | required | Research query |
| `research_type` | enum | "comprehensive" | "comprehensive" \| "quick" \| "deep" |
| `sources` | string[] | ["web", "news", "company"] | Data sources to search |

**Response:**

```json
{
  "query": "Latest trends in AI for healthcare diagnostics",
  "research_type": "comprehensive",
  "status": "pending",
  "message": "Research query submitted. Agent processing..."
}
```

**UX Context:** User enters a research topic, selects sources, and clicks "Start Research". Results populate in a card below the form.

---

#### Generate Briefing

```http
POST /api/research/briefing
```

Generates a comprehensive client briefing document using Researcher + Scribe agents.

**Request Body:** `BriefingRequest`

```json
{
  "company_name": "Microsoft",
  "industry": "Technology",
  "focus_areas": ["cloud", "AI", "enterprise"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company_name` | string | ✓ | Target company name |
| `industry` | string | | Industry classification |
| `focus_areas` | string[] | | Specific areas to research |

**Response:**

```json
{
  "company_name": "Microsoft",
  "status": "pending",
  "message": "Briefing generation started. Agent processing..."
}
```

**UX Context:** User enters a company name in the "Client Briefing" tab, clicks "Generate Briefing", and receives a comprehensive company analysis document.

---

## Documents API

The Documents API manages all generated documents including proposals, briefings, reports, and other artifacts created by the Scribe agent.

### UX Integration

Documents are accessed from:
- **Proposals Page** - For proposal documents
- **Export actions** throughout the app
- Direct document links

### Endpoints

#### List Documents

```http
GET /api/documents
```

Returns all documents, optionally filtered by type.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `doc_type` | string | | Filter by document type ("proposal", "briefing", "report") |
| `limit` | integer | 20 | Maximum documents to return |
| `offset` | integer | 0 | Pagination offset |

**Response:** `DocumentResponse[]`

---

#### Get Document

```http
GET /api/documents/{document_id}
```

Retrieves a specific document.

**Response:** `DocumentResponse`

```json
{
  "id": "doc-001",
  "title": "Q4 Strategy Report",
  "doc_type": "report",
  "content": "# Strategy Overview\n\nThis report outlines...",
  "format": "markdown",
  "created_at": "2026-02-04T10:30:00Z",
  "metadata": {
    "author_agent": "scribe",
    "version": 1
  }
}
```

---

#### Export Document

```http
POST /api/documents/{document_id}/export
```

Exports a document to a specified format for download.

**Request Body:** `ExportRequest`

```json
{
  "format": "pdf"
}
```

| Format | Content-Type | Description |
|--------|--------------|-------------|
| `pdf` | application/pdf | Professional PDF format (placeholder) |
| `docx` | application/vnd.openxmlformats... | Word document (placeholder) |
| `markdown` | text/markdown | Raw markdown content |
| `html` | text/html | Rendered HTML |

**Response:** File download with appropriate headers

```
Content-Disposition: attachment; filename=Document-Title.pdf
```

**UX Context:** User clicks the "Export" button on a document card, selects format, and receives a downloadable file.

---

## Knowledge API

The Knowledge API provides access to the RAG (Retrieval-Augmented Generation) knowledge base, powered by the Memory agent.

### UX Integration

The **Knowledge Page** (`/knowledge`) displays:
- Searchable grid of knowledge items
- Semantic search across the knowledge base
- Category and industry filters

```
+-------------------------------------------------------------+
|  Knowledge Base                                              |
|  ----------------------------------------------------------  |
|  🔍 [Search knowledge base...]           [Search] [Clear]    |
|                                                              |
|  +-------------+ +-------------+ +-------------+            |
|  | Framework   | | Case Study  | | Best        |            |
|  | Guide       | | Healthcare  | | Practices   |            |
|  | [Strategy]  | | [Healthcare]| | [Cloud]     |            |
|  | 95% match   | | 87% match   | | 82% match   |            |
|  +-------------+ +-------------+ +-------------+            |
+-------------------------------------------------------------+
```

### Endpoints

#### Search Knowledge

```http
POST /api/knowledge/search
```

Performs semantic search over the knowledge base using embeddings.

**Request Body:** `KnowledgeSearchRequest`

```json
{
  "query": "digital transformation methodologies for manufacturing",
  "category": "frameworks",
  "industry": "manufacturing",
  "limit": 10
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | string | required | Natural language search query |
| `category` | string | | Filter by category |
| `industry` | string | | Filter by industry |
| `limit` | integer | 10 | Maximum results (1-50) |

**Response:** `KnowledgeItemResponse[]`

```json
[
  {
    "id": "kb-001",
    "title": "Digital Transformation Framework",
    "content": "A comprehensive methodology for...",
    "category": "frameworks",
    "industry": "manufacturing",
    "tags": ["digital", "transformation", "methodology"],
    "score": 0.95
  }
]
```

**UX Context:** User types in the search bar, results appear as cards with relevance scores. Higher scores indicate better semantic matches.

---

#### Find Similar Engagements

```http
POST /api/knowledge/similar
```

Finds past client engagements similar to a query, useful for proposal preparation.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Description to match against |
| `limit` | integer | 5 | Maximum results |

**Response:**

```json
[
  {
    "id": "eng-001",
    "client_name": "TechCorp Industries",
    "client_industry": "Technology",
    "engagement_type": "Digital Transformation",
    "description": "Comprehensive cloud migration and process automation",
    "outcomes": "40% cost reduction, 60% faster deployment",
    "frameworks_used": ["Cloud Migration Framework", "Agile at Scale"],
    "score": 0.95
  }
]
```

**UX Context:** Used internally by agents when preparing proposals to reference similar past work.

---

## Analytics API

The Analytics API provides observability into agent performance, token usage, and execution traces.

### UX Integration

The **Analytics Page** (`/analytics`) shows:
- Performance metrics cards (executions, tokens, response time)
- Agent performance bar chart
- Filterable execution trace history

```
+-------------------------------------------------------------+
|  Analytics                                                   |
|  ----------------------------------------------------------  |
|  +----------+ +----------+ +----------+ +----------+        |
|  | 156      | | 7        | | 45,230   | | 2.3s     |        |
|  | Execs    | | Agents   | | Tokens   | | Avg Time |        |
|  +----------+ +----------+ +----------+ +----------+        |
|                                                              |
|  Agent Performance:                                          |
|  * Orchestrator ████████████████░░░░░░ 45 runs              |
|  * Researcher   ██████████░░░░░░░░░░░░ 28 runs              |
|  * Scribe       ████████░░░░░░░░░░░░░░ 22 runs              |
|                                                              |
|  Recent Traces:  [All] [Completed] [Failed]                  |
|  ----------------------------------------------------------  |
|  * orchestrator * task_decomposition    2.1s  1,240 ✓       |
|  * researcher   * web_search            3.4s  2,100 ✓       |
|  * scribe       * document_generation   1.8s    890 ✓       |
+-------------------------------------------------------------+
```

### Endpoints

#### List Traces

```http
GET /api/analytics/traces
```

Returns agent execution traces for debugging and monitoring.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `agent_name` | string | | Filter by agent name |
| `status` | string | | Filter by status ("completed", "failed", "running") |
| `limit` | integer | 50 | Maximum traces to return |
| `offset` | integer | 0 | Pagination offset |

**Response:** `AgentTraceResponse[]`

```json
[
  {
    "id": "trace-001",
    "agent_name": "orchestrator",
    "task_type": "task_decomposition",
    "status": "completed",
    "started_at": "2026-02-04T10:30:00Z",
    "completed_at": "2026-02-04T10:30:02Z",
    "tokens_used": 1240,
    "error": null
  }
]
```

**UX Context:** Populates the "Recent Traces" table with execution history. Users can filter by tab (All/Completed/Failed).

---

#### Get Metrics

```http
GET /api/analytics/metrics
```

Returns aggregated performance metrics for the specified time period.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | enum | "day" | Time period: "day" \| "week" \| "month" |

**Response:** `Metrics`

```json
{
  "period": "day",
  "since": "2026-02-03T10:30:00Z",
  "agent_stats": [
    {
      "agent": "orchestrator",
      "executions": 45,
      "avg_tokens": 1150.5
    },
    {
      "agent": "researcher",
      "executions": 28,
      "avg_tokens": 2340.2
    },
    {
      "agent": "scribe",
      "executions": 22,
      "avg_tokens": 1890.0
    }
  ],
  "total_executions": 156
}
```

**UX Context:** Powers the metrics cards and agent performance chart at the top of the Analytics page.

---

## WebSocket API

The WebSocket API provides real-time updates during agent processing, enabling live status indicators in the UI.

### Connection

```
WS /ws/agents/{conversation_id}
```

Connect to receive real-time events for a specific conversation.

**UX Integration:**

```tsx
// React hook automatically connects when conversation is active
useAgentWebSocket(conversationId, {
  onAgentStarted: (data) => { /* Update agent panel */ },
  onAgentThinking: (data) => { /* Show thought process */ },
  onAgentCompleted: (data) => { /* Mark complete, refetch */ },
  onStreamToken: (data) => { /* Append to message */ },
});
```

### Event Types

All events follow this structure:

```json
{
  "event_type": "agent.started",
  "timestamp": "2026-02-04T10:30:00Z",
  "data": { /* Event-specific payload */ }
}
```

---

#### `agent.started`

Fired when an agent begins processing a task.

```json
{
  "event_type": "agent.started",
  "data": {
    "agent": "researcher",
    "task": "Searching web for AI healthcare trends"
  }
}
```

**UX Effect:** Agent status panel shows "Researcher: Executing..."

---

#### `agent.thinking`

Fired while an agent is reasoning or processing.

```json
{
  "event_type": "agent.thinking",
  "data": {
    "agent": "strategist",
    "thought": "Analyzing client requirements...",
    "progress": 0.45
  }
}
```

**UX Effect:** Shows thought bubble or progress indicator next to agent.

---

#### `agent.completed`

Fired when an agent finishes its task.

```json
{
  "event_type": "agent.completed",
  "data": {
    "agent": "researcher",
    "result_summary": "Found 15 relevant articles",
    "duration_ms": 3400
  }
}
```

**UX Effect:** Agent marked as completed with checkmark, triggers message refetch.

---

#### `agent.handoff`

Fired when one agent passes control to another.

```json
{
  "event_type": "agent.handoff",
  "data": {
    "from_agent": "orchestrator",
    "to_agent": "researcher",
    "context": "Research request for market analysis"
  }
}
```

**UX Effect:** Shows workflow arrow from one agent to another in status panel.

---

#### `agent.error`

Fired when an agent encounters an error.

```json
{
  "event_type": "agent.error",
  "data": {
    "agent_name": "researcher",
    "error": "Failed to connect to search API"
  }
}
```

**UX Effect:** Agent shown in error state with red indicator.

---

#### `stream.token`

Fired for streaming LLM responses (token by token).

```json
{
  "event_type": "stream.token",
  "data": {
    "agent": "scribe",
    "token": "The "
  }
}
```

**UX Effect:** Tokens appended to the current message in real-time, creating a typewriter effect.

---

#### `document.generated`

Fired when the Scribe agent produces a document.

```json
{
  "event_type": "document.generated",
  "data": {
    "document_id": "doc-001",
    "type": "proposal",
    "title": "Acme Corp Digital Transformation Proposal"
  }
}
```

**UX Effect:** Toast notification and link to view the new document.

---

### Connection Management

The frontend WebSocket client includes:

| Feature | Behavior |
|---------|----------|
| **Auto-reconnect** | Exponential backoff up to 5 attempts |
| **Ping/Pong** | Send "ping" to receive `{"type": "pong"}` |
| **Connection pooling** | One connection per conversation |
| **Cleanup** | Disconnects when navigating away |

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| `200` | OK | Successful GET/POST |
| `201` | Created | Resource created (new conversation, proposal) |
| `400` | Bad Request | Invalid request body or parameters |
| `404` | Not Found | Resource doesn't exist |
| `422` | Validation Error | Pydantic validation failed |
| `500` | Server Error | Unexpected backend error |
| `501` | Not Implemented | Feature not yet available |

### Error Response Format

```json
{
  "detail": "Conversation not found"
}
```

### Frontend Error Handling

```typescript
try {
  const result = await chatApi.sendMessage(id, { content });
} catch (error) {
  if (error instanceof ApiError) {
    if (error.status === 404) {
      // Handle not found
    }
  }
}
```

---

## TypeScript Types Reference

### Chat Types

```typescript
interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
  message_count: number;
}

interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  metadata: Record<string, unknown>;
}
```

### Agent Types

```typescript
type AgentName =
  | "orchestrator"
  | "strategist"
  | "researcher"
  | "analyst"
  | "scribe"
  | "advisor"
  | "memory";

type AgentStatusType =
  | "idle"
  | "thinking"
  | "executing"
  | "waiting"
  | "completed"
  | "error";
```

### Document Types

```typescript
interface Document {
  id: string;
  title: string;
  doc_type: string;
  content: string;
  format: string;
  created_at: string;
  metadata: Record<string, unknown>;
}
```

### WebSocket Event Types

```typescript
type WSEventType =
  | "agent.started"
  | "agent.thinking"
  | "agent.completed"
  | "agent.handoff"
  | "agent.error"
  | "stream.token"
  | "document.generated"
  | "connection.established"
  | "connection.error";
```

---

## Quick Reference

### Frontend API Client Usage

```typescript
import { chatApi, proposalsApi, researchApi } from "@/lib/api";

// Chat
await chatApi.listConversations();
await chatApi.sendMessage(conversationId, { content: "Hello" });

// Proposals
await proposalsApi.generate({
  client_name: "Acme",
  client_industry: "Tech",
  engagement_type: "Consulting",
  scope_description: "Digital transformation",
});

// Research
await researchApi.query({
  query: "AI trends",
  research_type: "comprehensive",
});
```

### cURL Examples

```bash
# List conversations
curl http://localhost:8000/api/chat/conversations

# Send a message
curl -X POST http://localhost:8000/api/chat/conversations/{id}/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, Federation!"}'

# Generate a proposal
curl -X POST http://localhost:8000/api/proposals/generate \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Acme Corp",
    "client_industry": "Technology",
    "engagement_type": "Digital Transformation",
    "scope_description": "Cloud migration project"
  }'

# Get analytics
curl http://localhost:8000/api/analytics/metrics?period=week
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-04 | Initial API release |

---

*This documentation is auto-synchronized with the FastAPI backend. For interactive documentation, visit `/docs` (Swagger UI) or `/redoc` (ReDoc).*
