# Technical Requirements Document (TRD)
## OneShot: AI-Powered Professional Services Engagement Platform

---

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
+-----------------------------------------------------------------------------+
|                       FRONTEND (Next.js + Shadcn)                           |
|  +-------------+  +-------------+  +-------------+  +-------------+         |
|  |   Chat UI   |  |  Dashboard  |  |  Documents  |  |  Settings   |         |
|  |  Component  |  |   Panel     |  |   Viewer    |  |    Panel    |         |
|  +-------------+  +-------------+  +-------------+  +-------------+         |
|                              |                                              |
|                    Vercel Skills Integration                                |
+------------------------------+----------------------------------------------+
                               | REST API / WebSocket
                               v
+-----------------------------------------------------------------------------+
|                         BACKEND (Python FastAPI)                            |
|  +-------------------------------------------------------------------------+|
|  |                        API Gateway Layer                                ||
|  |   /chat  /proposals  /research  /documents  /knowledge  /analytics     ||
|  +-------------------------------------------------------------------------+|
|                                  |                                          |
|  +-------------------------------------------------------------------------+|
|  |                   Microsoft Agent Framework Layer                       ||
|  |  +-----------------------------------------------------------------+   ||
|  |  |                     ORCHESTRATOR AGENT                          |   ||
|  |  |           (Task Planning, Coordination, Quality Control)        |   ||
|  |  +-----------------------------+-----------------------------------+   ||
|  |                               |                                        ||
|  |    +------------+-------------+-----------+------------+------------+  ||
|  |    |            |             |           |            |            |  ||
|  |    v            v             v           v            v            v  ||
|  | +------+   +------+   +------+   +------+   +------+   +------+       ||
|  | |STRAT |   |RESRCH|   |ANLYST|   |SCRIBE|   |ADVSR |   |MEMORY|       ||
|  | |AGENT |   |AGENT |   |AGENT |   |AGENT |   |AGENT |   |AGENT |       ||
|  | +------+   +------+   +------+   +------+   +------+   +------+       ||
|  +-------------------------------------------------------------------------+|
|                                  |                                          |
|  +-------------------------------------------------------------------------+|
|  |                         Services Layer                                  ||
|  |   LLMService  |  SearchService  |  DocService  |  KnowledgeService     ||
|  +-------------------------------------------------------------------------+|
+------------------------------+-----------------------------------------------+
                               |
         +---------------------+---------------------+
         |                     |                     |
         v                     v                     v
+----------------+    +------------------+    +------------------+
|  Azure OpenAI  |    |     SQLite       |    |  External APIs   |
|   GPT-5.x      |    |  (via aiosqlite) |    |  (Mock/Real)     |
|                |    |                  |    |                  |
| * Chat Complete|    | * Engagements    |    | * News API       |
| * Embeddings   |    | * Documents      |    | * Search API     |
| * Assistants   |    | * Knowledge      |    | * Company Data   |
+----------------+    | * Conversations  |    +------------------+
                      | * Agent Traces   |
                      +------------------+
```

### 1.2 Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Frontend** | Next.js | 14.x | React framework with App Router |
| **UI Components** | Shadcn/ui | Latest | Accessible, customizable components |
| **UI Skills** | Vercel Agent Skills | Latest | Pre-built agent UI patterns |
| **Styling** | Tailwind CSS | 3.x | Utility-first CSS |
| **Backend** | Python | 3.11+ | Runtime |
| **API Framework** | FastAPI | 0.109+ | Async REST API |
| **Agent Framework** | Microsoft Agent Framework | Latest | Multi-agent orchestration |
| **LLM** | Azure OpenAI GPT-5.x | Latest | Language model |
| **Database** | SQLite | 3.x | Lightweight persistence |
| **ORM** | SQLAlchemy + aiosqlite | 2.x | Async database access |
| **WebSocket** | FastAPI WebSocket | - | Real-time streaming |

---

## 2. Frontend Architecture

### 2.1 Project Structure

```
frontend/
├── app/
│   ├── layout.tsx                 # Root layout with providers
│   ├── page.tsx                   # Landing/chat page
│   ├── dashboard/
│   │   └── page.tsx               # Agent activity dashboard
│   ├── proposals/
│   │   └── [id]/page.tsx          # Proposal viewer/editor
│   ├── knowledge/
│   │   └── page.tsx               # Knowledge base browser
│   └── api/
│       └── [...proxy]/route.ts    # API proxy to backend
├── components/
│   ├── ui/                        # Shadcn components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── input.tsx
│   │   └── ...
│   ├── chat/
│   │   ├── ChatContainer.tsx      # Main chat interface
│   │   ├── MessageList.tsx        # Message history
│   │   ├── MessageBubble.tsx      # Individual message
│   │   ├── AgentThinking.tsx      # Agent activity indicator
│   │   └── InputBar.tsx           # User input with attachments
│   ├── agents/
│   │   ├── AgentStatusPanel.tsx   # Real-time agent status
│   │   ├── AgentCard.tsx          # Individual agent display
│   │   └── TaskProgress.tsx       # Task completion tracking
│   ├── documents/
│   │   ├── DocumentViewer.tsx     # Preview generated docs
│   │   ├── DocumentEditor.tsx     # Edit capabilities
│   │   └── ExportMenu.tsx         # Export options
│   └── shared/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── LoadingStates.tsx
├── lib/
│   ├── api.ts                     # API client
│   ├── websocket.ts               # WebSocket handler
│   ├── store.ts                   # Zustand state management
│   └── utils.ts                   # Utilities
├── hooks/
│   ├── useChat.ts                 # Chat state management
│   ├── useAgents.ts               # Agent status subscription
│   └── useDocuments.ts            # Document operations
└── types/
    └── index.ts                   # TypeScript definitions
```

### 2.2 Key UI Components

#### Chat Interface (Primary)

```tsx
// components/chat/ChatContainer.tsx
interface ChatContainerProps {
  conversationId: string;
  onAgentActivity: (activity: AgentActivity) => void;
}

// Features:
// - Streaming message display
// - Rich content rendering (markdown, code, tables)
// - Inline document previews
// - Agent activity sidebar
// - Context-aware suggestions
```

#### Agent Activity Dashboard

```tsx
// components/agents/AgentStatusPanel.tsx
interface AgentStatus {
  agentId: string;
  agentType: 'orchestrator' | 'strategist' | 'researcher' | 'analyst' | 'scribe' | 'advisor' | 'memory';
  status: 'idle' | 'thinking' | 'executing' | 'waiting';
  currentTask?: string;
  progress?: number;
  lastActivity: Date;
}

// Visual representation:
// - Agent avatars with status indicators
// - Current task descriptions
// - Progress bars for long operations
// - Expandable trace logs
```

### 2.3 Vercel Agent Skills Integration

```typescript
// lib/agentSkills.ts
import { createAgentSkill } from '@vercel-labs/agent-skills';

export const proposalSkill = createAgentSkill({
  name: 'proposal-generator',
  description: 'Generate client proposals',
  parameters: {
    clientName: { type: 'string', required: true },
    industry: { type: 'string', required: true },
    scope: { type: 'string', required: true },
  },
  render: (result) => <ProposalPreview data={result} />,
});

export const researchSkill = createAgentSkill({
  name: 'client-research',
  description: 'Research client background',
  parameters: {
    companyName: { type: 'string', required: true },
  },
  render: (result) => <ResearchBriefing data={result} />,
});
```

### 2.4 State Management

```typescript
// lib/store.ts
import { create } from 'zustand';

interface AppState {
  // Conversation
  conversations: Conversation[];
  activeConversationId: string | null;
  messages: Message[];
  
  // Agents
  agentStatuses: Record<string, AgentStatus>;
  activeAgents: string[];
  
  // Documents
  documents: Document[];
  selectedDocument: string | null;
  
  // Actions
  sendMessage: (content: string, attachments?: File[]) => Promise<void>;
  selectConversation: (id: string) => void;
  subscribeToAgentUpdates: () => void;
}
```

---

## 3. Backend Architecture

### 3.1 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry
│   ├── config.py                  # Configuration management
│   ├── dependencies.py            # Dependency injection
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── chat.py            # Chat endpoints
│   │   │   ├── proposals.py       # Proposal operations
│   │   │   ├── research.py        # Research queries
│   │   │   ├── documents.py       # Document management
│   │   │   ├── knowledge.py       # Knowledge base
│   │   │   └── analytics.py       # Metrics & traces
│   │   └── websocket.py           # WebSocket handlers
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py        # Main coordinator
│   │   ├── strategist.py          # Strategy & scoping
│   │   ├── researcher.py          # Research & intelligence
│   │   ├── analyst.py             # Data analysis
│   │   ├── scribe.py              # Document generation
│   │   ├── advisor.py             # Client communications
│   │   ├── memory.py              # Knowledge retrieval
│   │   └── base.py                # Base agent class
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py         # Azure OpenAI wrapper
│   │   ├── search_service.py      # Web/news search
│   │   ├── document_service.py    # Doc generation
│   │   ├── knowledge_service.py   # Vector search
│   │   └── trace_service.py       # Observability
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py            # SQLAlchemy models
│   │   └── schemas.py             # Pydantic schemas
│   │
│   └── data/
│       ├── templates/             # Document templates
│       ├── knowledge_base/        # Sample knowledge
│       └── mock_data/             # Demo data
│
├── tests/
│   ├── test_agents/
│   ├── test_api/
│   └── test_services/
│
├── alembic/                       # Database migrations
├── requirements.txt
├── pyproject.toml
└── Dockerfile
```

### 3.2 FastAPI Application

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import chat, proposals, research, documents, knowledge, analytics
from app.api.websocket import websocket_router
from app.config import settings
from app.models.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="OneShot API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST Routes
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(proposals.router, prefix="/api/proposals", tags=["proposals"])
app.include_router(research.router, prefix="/api/research", tags=["research"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

# WebSocket
app.include_router(websocket_router)
```

### 3.3 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat/conversations` | GET | List conversations |
| `/api/chat/conversations` | POST | Create conversation |
| `/api/chat/conversations/{id}/messages` | POST | Send message (triggers agents) |
| `/api/proposals` | GET | List generated proposals |
| `/api/proposals/{id}` | GET | Get proposal details |
| `/api/proposals/generate` | POST | Trigger proposal generation |
| `/api/research/briefing` | POST | Generate client briefing |
| `/api/research/query` | POST | Ad-hoc research query |
| `/api/documents` | GET | List documents |
| `/api/documents/{id}` | GET | Get document |
| `/api/documents/{id}/export` | POST | Export to format |
| `/api/knowledge/search` | POST | Semantic search |
| `/api/knowledge/similar` | POST | Find similar engagements |
| `/api/analytics/traces` | GET | Agent execution traces |
| `/api/analytics/metrics` | GET | Performance metrics |
| `/ws/agents` | WebSocket | Real-time agent updates |

### 3.4 Microsoft Agent Framework Integration

```python
# app/agents/orchestrator.py
from agent_framework import Agent, AgentContext, Message
from agent_framework.orchestration import Orchestrator as BaseOrchestrator

class OrchestratorAgent(BaseOrchestrator):
    """
    Central coordinator that decomposes tasks and manages agent execution.
    """
    
    def __init__(self, llm_service, agent_registry):
        super().__init__()
        self.llm = llm_service
        self.agents = agent_registry
        self.system_prompt = ORCHESTRATOR_PROMPT
    
    async def process(self, ctx: AgentContext, message: Message) -> Message:
        # 1. Analyze intent
        intent = await self._analyze_intent(message)
        
        # 2. Create execution plan
        plan = await self._create_plan(intent)
        
        # 3. Execute plan with agent coordination
        results = await self._execute_plan(ctx, plan)
        
        # 4. Synthesize response
        response = await self._synthesize_response(results)
        
        return response
    
    async def _create_plan(self, intent: Intent) -> ExecutionPlan:
        """Use LLM to decompose request into agent tasks."""
        planning_prompt = f"""
        Analyze this request and create an execution plan.
        Available agents: {list(self.agents.keys())}
        
        Request: {intent.description}
        
        Output a JSON plan with:
        - tasks: list of {{"agent": str, "task": str, "depends_on": [task_ids]}}
        - parallel_groups: tasks that can run concurrently
        """
        
        response = await self.llm.complete(planning_prompt)
        return ExecutionPlan.parse(response)
```

```python
# app/agents/strategist.py
from agent_framework import Agent, AgentContext, Message

class StrategistAgent(Agent):
    """
    Handles engagement scoping, proposal strategy, framework selection.
    """
    
    name = "strategist"
    description = "Expert in engagement scoping and proposal strategy"
    
    capabilities = [
        "proposal_generation",
        "engagement_scoping",
        "framework_selection",
        "approach_design"
    ]
    
    async def process(self, ctx: AgentContext, message: Message) -> Message:
        task_type = message.metadata.get("task_type")
        
        if task_type == "proposal_generation":
            return await self._generate_proposal(ctx, message)
        elif task_type == "scoping":
            return await self._scope_engagement(ctx, message)
        elif task_type == "framework":
            return await self._select_framework(ctx, message)
        
        return await self._general_strategy(ctx, message)
    
    async def _generate_proposal(self, ctx: AgentContext, message: Message):
        # Gather inputs from other agents via context
        research = ctx.get("research_results")
        past_work = ctx.get("similar_engagements")
        
        prompt = PROPOSAL_GENERATION_PROMPT.format(
            client_info=message.content,
            research=research,
            past_work=past_work,
            templates=self._get_templates()
        )
        
        proposal_content = await self.llm.complete(prompt)
        
        return Message(
            content=proposal_content,
            metadata={
                "type": "proposal_draft",
                "format": "markdown",
                "requires_review": True
            }
        )
```

```python
# app/agents/researcher.py
class ResearcherAgent(Agent):
    """
    Gathers external intelligence: web search, news, company data.
    """
    
    name = "researcher"
    tools = ["web_search", "news_search", "company_lookup", "document_analysis"]
    
    async def process(self, ctx: AgentContext, message: Message) -> Message:
        research_type = message.metadata.get("research_type", "comprehensive")
        
        if research_type == "comprehensive":
            # Parallel research across multiple sources
            results = await asyncio.gather(
                self._web_search(message.content),
                self._news_search(message.content),
                self._company_data(message.content),
            )
            
            synthesis = await self._synthesize_research(results)
            return Message(content=synthesis, metadata={"sources": self._sources})
        
        # ... other research types
```

```python
# app/agents/memory.py
class MemoryAgent(Agent):
    """
    Manages knowledge base: past engagements, templates, expertise mapping.
    """
    
    name = "memory"
    
    def __init__(self, knowledge_service, embedding_service):
        self.knowledge = knowledge_service
        self.embeddings = embedding_service
    
    async def process(self, ctx: AgentContext, message: Message) -> Message:
        query = message.content
        
        # Semantic search over knowledge base
        embedding = await self.embeddings.embed(query)
        results = await self.knowledge.search(
            embedding=embedding,
            filters=message.metadata.get("filters"),
            limit=10
        )
        
        # Augment with metadata
        enriched = await self._enrich_results(results)
        
        return Message(
            content=self._format_results(enriched),
            metadata={
                "result_count": len(results),
                "sources": [r.source for r in results]
            }
        )
```

---

## 4. Database Schema

### 4.1 SQLite Tables

```python
# app/models/database.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# ============ Core Entities ============

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    conversation = relationship("Conversation", back_populates="messages")
    agent_traces = relationship("AgentTrace", back_populates="message")

# ============ Agent Tracing ============

class AgentTrace(Base):
    __tablename__ = "agent_traces"
    
    id = Column(String, primary_key=True)
    message_id = Column(String, ForeignKey("messages.id"))
    agent_name = Column(String)
    task_type = Column(String)
    input_data = Column(JSON)
    output_data = Column(JSON)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    status = Column(String)  # running, completed, failed
    error = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0)
    
    message = relationship("Message", back_populates="agent_traces")

# ============ Documents ============

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=True)
    title = Column(String)
    doc_type = Column(String)  # proposal, briefing, analysis, presentation
    content = Column(Text)  # Markdown or structured content
    format = Column(String)  # markdown, html, json
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})

# ============ Knowledge Base ============

class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"
    
    id = Column(String, primary_key=True)
    title = Column(String)
    content = Column(Text)
    category = Column(String)  # engagement, framework, template, expertise
    industry = Column(String, nullable=True)
    tags = Column(JSON, default=[])
    embedding = Column(JSON)  # Stored as list of floats
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})

class Engagement(Base):
    __tablename__ = "engagements"
    
    id = Column(String, primary_key=True)
    client_name = Column(String)
    client_industry = Column(String)
    engagement_type = Column(String)
    description = Column(Text)
    outcomes = Column(Text)
    team_members = Column(JSON, default=[])
    frameworks_used = Column(JSON, default=[])
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    status = Column(String)
    embedding = Column(JSON)
    metadata = Column(JSON, default={})

# ============ Analytics ============

class Metric(Base):
    __tablename__ = "metrics"
    
    id = Column(String, primary_key=True)
    metric_type = Column(String)
    value = Column(Float)
    dimensions = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.utcnow)
```

### 4.2 Sample Data Structure

```python
# app/data/mock_data/sample_knowledge.py

SAMPLE_ENGAGEMENTS = [
    {
        "id": "eng-001",
        "client_name": "Global Manufacturing Inc",
        "client_industry": "Manufacturing",
        "engagement_type": "Digital Transformation",
        "description": "End-to-end supply chain digitization including IoT integration, predictive analytics, and digital twin implementation.",
        "outcomes": "30% reduction in inventory costs, 25% improvement in delivery times",
        "frameworks_used": ["Digital Maturity Assessment", "Supply Chain 4.0 Framework"],
        "team_members": ["John Partner", "Sarah Manager", "Mike Analyst"],
    },
    {
        "id": "eng-002",
        "client_name": "HealthCare Partners",
        "client_industry": "Healthcare",
        "engagement_type": "Post-Merger Integration",
        "description": "Integration of two regional healthcare systems including IT consolidation, process harmonization, and culture integration.",
        "outcomes": "$50M synergies captured in year 1, 95% staff retention",
        "frameworks_used": ["PMI Playbook", "Healthcare Synergy Model"],
        "team_members": ["Lisa Partner", "Tom Manager", "Amy Analyst"],
    },
    # ... more sample engagements
]

SAMPLE_FRAMEWORKS = [
    {
        "id": "fw-001",
        "title": "Digital Maturity Assessment",
        "category": "framework",
        "content": "A structured approach to evaluating an organization's digital capabilities across 6 dimensions: Strategy, Culture, Organization, Technology, Data, and Customer Experience.",
        "industry": None,  # Cross-industry
    },
    # ... more frameworks
]
```

---

## 5. Azure OpenAI Integration

### 5.1 Service Configuration

```python
# app/services/llm_service.py
from openai import AsyncAzureOpenAI
from typing import AsyncIterator
import json

class LLMService:
    def __init__(self, config):
        self.client = AsyncAzureOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_KEY,
            api_version="2024-12-01-preview"  # GPT-5.x compatible
        )
        self.deployment = config.AZURE_OPENAI_DEPLOYMENT
        self.embedding_deployment = config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    
    async def complete(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    async def stream(
        self,
        prompt: str,
        system_prompt: str = None,
        **kwargs
    ) -> AsyncIterator[str]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        stream = await self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            stream=True,
            **kwargs
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def embed(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            model=self.embedding_deployment,
            input=text
        )
        return response.data[0].embedding
    
    async def structured_output(
        self,
        prompt: str,
        output_schema: dict,
        system_prompt: str = None
    ) -> dict:
        """Use GPT-5.x structured output for reliable JSON."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": output_schema
            }
        )
        
        return json.loads(response.choices[0].message.content)
```

### 5.2 Agent Prompts

```python
# app/agents/prompts.py

ORCHESTRATOR_PROMPT = """
You are the Orchestrator Agent for OneShot, a professional services AI platform.
Your role is to coordinate specialized agents to fulfill user requests.

Available Agents:
- strategist: Engagement scoping, proposal strategy, framework selection
- researcher: Web search, news analysis, company intelligence
- analyst: Data analysis, financial modeling, benchmarking
- scribe: Document generation, formatting, branding
- advisor: Executive summaries, client communications
- memory: Knowledge base search, past engagement retrieval

For each request:
1. Analyze the user's intent and requirements
2. Identify which agents are needed
3. Plan the execution sequence (parallel where possible)
4. Coordinate handoffs between agents
5. Quality-check the final output

Respond with a JSON execution plan.
"""

STRATEGIST_PROMPT = """
You are the Strategist Agent, a senior consulting expert.
Your expertise: engagement scoping, proposal development, strategic frameworks.

When generating proposals:
- Structure: Executive Summary, Situation, Approach, Team, Timeline, Investment
- Be specific about methodologies and deliverables
- Reference relevant past work when available
- Quantify expected outcomes where possible

Maintain a professional, confident tone appropriate for C-suite audiences.
"""

RESEARCHER_PROMPT = """
You are the Researcher Agent, an expert research analyst.
Your role: Gather and synthesize information from multiple sources.

Research principles:
- Always cite sources
- Distinguish facts from opinions/analysis
- Identify potential biases in sources
- Highlight conflicting information
- Note confidence levels for findings

Organize research into clear sections: Company Overview, Industry Context, 
Recent Developments, Competitive Landscape, Potential Opportunities/Risks.
"""
```

---

## 6. WebSocket Real-Time Updates

### 6.1 WebSocket Handler

```python
# app/api/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio

websocket_router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, conversation_id: str):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = set()
        self.active_connections[conversation_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, conversation_id: str):
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].discard(websocket)
    
    async def broadcast_agent_update(self, conversation_id: str, update: dict):
        if conversation_id in self.active_connections:
            message = json.dumps(update)
            for connection in self.active_connections[conversation_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@websocket_router.websocket("/ws/agents/{conversation_id}")
async def agent_updates(websocket: WebSocket, conversation_id: str):
    await manager.connect(websocket, conversation_id)
    try:
        while True:
            # Keep connection alive, receive any client messages
            data = await websocket.receive_text()
            # Handle ping/pong or client commands
    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
```

### 6.2 Agent Update Events

```python
# Event types
AGENT_EVENTS = {
    "agent.started": {
        "agent": str,
        "task": str,
        "timestamp": str
    },
    "agent.thinking": {
        "agent": str,
        "thought": str,  # Current reasoning step
        "progress": float  # 0-1
    },
    "agent.tool_call": {
        "agent": str,
        "tool": str,
        "input": dict
    },
    "agent.completed": {
        "agent": str,
        "result_summary": str,
        "duration_ms": int
    },
    "agent.handoff": {
        "from_agent": str,
        "to_agent": str,
        "context": str
    },
    "stream.token": {
        "token": str,
        "agent": str
    },
    "document.generated": {
        "document_id": str,
        "type": str,
        "title": str
    }
}
```

---

## 7. Local Development Setup

### 7.1 Docker Compose (Recommended)

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./data:/app/data
    environment:
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_KEY=${AZURE_OPENAI_KEY}
      - AZURE_OPENAI_DEPLOYMENT=${AZURE_OPENAI_DEPLOYMENT}
      - DATABASE_URL=sqlite+aiosqlite:///./data/oneshot.db
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7.2 Local Development Setup (Without Docker)

```bash
# Terminal 1: Start Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2: Start Frontend
cd frontend
npm install
npm run dev
```

### 7.3 Local Architecture

```
+-----------------------------------------------------------------+
|                    Local Development                            |
|                                                                 |
|  +-----------------+      +-----------------+                   |
|  |   Next.js Dev   |      |   FastAPI Dev   |                   |
|  |   Server        |------|   Server        |                   |
|  |   :3000         |      |   :8000         |                   |
|  +-----------------+      +--------+--------+                   |
|                                    |                            |
|                           +--------+--------+                   |
|                           |                 |                   |
|                    +------v-----+   +-------v------+            |
|                    |Azure OpenAI|   |    SQLite    |            |
|                    |  (Remote)  |   |   (Local)    |            |
|                    |  GPT-5.x   |   | oneshot.db|            |
|                    +------------+   +--------------+            |
+-----------------------------------------------------------------+
```

---

## 8. Security Considerations (Local POC)

| Area | Implementation |
|------|----------------|
| **Authentication** | None (local demo) |
| **Authorization** | None (local demo) |
| **Data Storage** | SQLite file in ./data |
| **Secrets** | .env file (gitignored) |
| **API Security** | CORS configured for localhost |
| **Audit Logging** | Console output |

---

## 9. Testing Strategy

### 9.1 Test Structure

```
tests/
├── unit/
│   ├── test_agents/
│   │   ├── test_orchestrator.py
│   │   ├── test_strategist.py
│   │   └── ...
│   ├── test_services/
│   │   ├── test_llm_service.py
│   │   └── test_knowledge_service.py
│   └── test_models/
│
├── integration/
│   ├── test_agent_coordination.py
│   ├── test_api_endpoints.py
│   └── test_websocket.py
│
└── e2e/
    ├── test_proposal_flow.py
    ├── test_research_flow.py
    └── test_knowledge_flow.py
```

### 9.2 Demo Validation Checklist

- [ ] Proposal generation completes in < 5 minutes
- [ ] Generated proposal contains all required sections
- [ ] Research includes accurate, cited information
- [ ] Agent status updates stream in real-time
- [ ] Documents export correctly to PDF/DOCX
- [ ] Knowledge search returns relevant results
- [ ] UI responsive across all demo scenarios
- [ ] Error handling graceful and informative

---

## 10. Dependencies

### 10.1 Backend Requirements

```txt
# requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
sqlalchemy==2.0.25
aiosqlite==0.19.0
openai==1.12.0
httpx==0.26.0
python-multipart==0.0.6
python-dotenv==1.0.0
jinja2==3.1.3
markdown==3.5.2
weasyprint==60.2  # PDF generation
python-docx==1.1.0  # DOCX generation

# Microsoft Agent Framework
agent-framework @ git+https://github.com/microsoft/agent-framework.git

# Vector search (optional, can use embeddings directly)
numpy==1.26.3
scikit-learn==1.4.0

# Testing
pytest==8.0.0
pytest-asyncio==0.23.0
httpx==0.26.0  # For test client
```

### 10.2 Frontend Dependencies

```json
{
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-scroll-area": "^1.0.5",
    "@radix-ui/react-tabs": "^1.0.4",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "lucide-react": "^0.321.0",
    "tailwind-merge": "^2.2.0",
    "tailwindcss-animate": "^1.0.7",
    "zustand": "^4.5.0",
    "react-markdown": "^9.0.1",
    "react-syntax-highlighter": "^15.5.0",
    "@vercel-labs/agent-skills": "latest"
  },
  "devDependencies": {
    "typescript": "^5.3.3",
    "tailwindcss": "^3.4.1",
    "@types/react": "^18.2.48",
    "@types/node": "^20.11.5"
  }
}
```

---

## 11. Development Milestones

### Phase 1: Foundation
- Project scaffolding (FastAPI + Next.js)
- Database schema and models
- Azure OpenAI integration
- Basic chat API

### Phase 2: Agent Core
- Microsoft Agent Framework integration
- Orchestrator agent implementation
- Researcher agent with mock search
- Memory agent with knowledge base

### Phase 3: Agent Specialists
- Strategist agent (proposal generation)
- Analyst agent (data synthesis)
- Scribe agent (document generation)
- Advisor agent (communications)

### Phase 4: UI/UX
- Chat interface with Shadcn
- Agent status panel
- Document viewer/exporter
- Dashboard views

### Phase 5: Demo Polish
- Sample data population
- Demo script optimization
- Error handling refinement
- Performance tuning

---

## 12. Appendix

### A. Environment Variables

```bash
# .env.example

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-5-deployment
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/oneshot.db

# API
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000

# Feature Flags
ENABLE_AGENT_TRACING=true
DEMO_MODE=true
```

### B. External API Mocks (Demo Mode)

For demo stability, external APIs (news, web search) are mocked with realistic responses stored in `backend/app/data/mock_data/`.

### C. References

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Vercel Agent Skills](https://github.com/vercel-labs/agent-skills)
- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Shadcn/ui Documentation](https://ui.shadcn.com/)

---

*Document Version: 1.0*
*Classification: Technical / Internal*
