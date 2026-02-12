# Agents League @ TechConnect — Hackathon Battle Plan

## Social Media Command Center

**Hackathon:** Agents League @ TechConnect  
**Deadline:** Feb 13, 2026 at 11:59 PM PT  
**Submission:** [Open issue using template](https://github.com/microsoft/agentsleague-techconnect/issues/new?template=project.yml)

---

## Table of Contents

1. [Deep Analysis: All Three Tracks](#1-deep-analysis-all-three-tracks)
2. [Track Recommendation & Rationale](#2-track-recommendation--rationale)
3. [What We're Building](#3-what-were-building)
4. [Judging Criteria & How We Score](#4-judging-criteria--how-we-score)
5. [Architecture Overview](#5-architecture-overview)
6. [Prerequisites & Setup](#6-prerequisites--setup)
7. [Implementation Plan](#7-implementation-plan)
8. [File-by-File Change Map](#8-file-by-file-change-map)
9. [New Files to Create](#9-new-files-to-create)
10. [Security Checklist](#10-security-checklist)
11. [Demo Script](#11-demo-script)
12. [Submission Checklist](#12-submission-checklist)
13. [Risk Mitigation](#13-risk-mitigation)
14. [Track 1 (Creative Apps) — Alternate Plan](#14-track-1-creative-apps--alternate-plan)

---

## 1. Deep Analysis: All Three Tracks

### Track 1: Creative Apps (GitHub Copilot)

| Dimension | Details |
|-----------|---------|
| **Core Tools** | GitHub Copilot, VS Code, Copilot CLI SDK, WorkIQ MCP |
| **Requirements** | (1) GitHub Copilot usage, (2) Creative application, (3) MCP integration |
| **Evaluation** | Accuracy 20%, Reasoning 20%, Creativity 15%, UX 15%, Reliability 20%, Community Vote 10% |
| **Competition** | Wide open — any app type (web, CLI, mobile, desktop). Many entries will be CLI tools. |
| **Fit with Our Codebase** | **Medium.** We'd need to add Copilot CLI SDK and WorkIQ MCP as new dependencies. Our Next.js + FastAPI stack is a creative app. But the Copilot SDK integration is an addon, not core to our architecture. |
| **Risk** | WorkIQ requires M365 admin consent, Copilot SDK is a separate billing/quota dimension. If either auth flow fails during demo, our submission loses a mandatory requirement. |

### Track 2: Reasoning Agents (Microsoft Foundry) ⭐ RECOMMENDED

| Dimension | Details |
|-----------|---------|
| **Core Tools** | Microsoft Agent Framework (`agent-framework`), Azure OpenAI reasoning models via Foundry (GPT-5.x), MCP servers |
| **Scenario** | **"Build an AI agent that can effectively assist the communication team of a company in creating social media content for various platforms."** |
| **Requirements** | (1) Design agent with Foundry, (2) Implement reasoning patterns (CoT, ReAct, Self-Reflection), (3) Ground on data sources, (4) Integrate MCP tools or APIs |
| **Milestones** | M1: Set up Foundry environment → M2: Create agent with instructions/reasoning → M3: Add grounding knowledge → M4: Add external tools via MCP |
| **Evaluation** | Accuracy 25%, Reasoning 25%, Creativity 20%, UX 15%, Technical 15% |
| **Competition** | Most entries will be Foundry Playground demos or single-agent Python scripts. **Our full-stack multi-agent app will be orders of magnitude more impressive.** |
| **Fit with Our Codebase** | **PERFECT.** The scenario IS social media content creation. We already have **Microsoft Agent Framework (MAF) installed** (`agent-framework==1.0.0b251120`) with `factory.py` providing `AzureOpenAIResponsesClient`, `create_agent()`, and `@tool` decorators. Our multi-agent orchestration with parallel `asyncio.gather` dispatch IS the "bonus" multi-agent system they describe. We already have CoT, ReAct, and Self-Reflection patterns in our agent prompts. |
| **Bonus Items (we already have)** | Multi-agent architecture, reviewer agent, evaluation/tracing, monitoring, safety layers — all described as aspirational "Going Further" items in the starter kit. |
| **Risk** | Low — MAF is already installed and factory.py is already wired to Azure OpenAI via Foundry endpoints. No new auth flows or SDKs needed. |

### Track 3: Enterprise Agents (M365 Agents Toolkit)

| Dimension | Details |
|-----------|---------|
| **Core Tools** | M365 Agents Toolkit, Copilot Studio, Teams, Declarative Agents, Custom Engine Agents |
| **Requirements** | (1) M365 Copilot Chat Agent (pass/fail gate), (2) MCP server integration (8pts), (3) OAuth (5pts), (4) Adaptive Cards (5pts), (5) Connected agents (15pts) |
| **Evaluation** | Technical 33%, Business Value 33%, Innovation 34% |
| **Fit with Our Codebase** | **Poor.** Would require completely restructuring as a Teams/Copilot extension. Different ecosystem (Bot Framework, Teams manifests, Entra ID), different deployment model (Azure App Service), different UX paradigm (Adaptive Cards in Teams). |
| **Risk** | Very High — requires M365 Copilot license, sideloading-enabled tenant, Entra ID app registration, C#/.NET or Teams JavaScript framework. Completely different architecture from what we have. |

### Head-to-Head Comparison

| Factor | Track 1 (Creative) | Track 2 (Reasoning) ⭐ | Track 3 (Enterprise) |
|--------|-------------------|----------------------|---------------------|
| Scenario alignment | Generic "build any creative app" | **Exact: "social media content for brands"** | M365 enterprise scenarios (HR, IT, legal) |
| Codebase reuse | ~60% (need to add Copilot SDK) | **~95% (MAF installed + factory.py + parallel orchestrator)** | ~10% (completely different ecosystem) |
| Competitive advantage | Polished UI vs CLI tools | **Full-stack multi-agent vs Playground demos** | Weak (not a Teams-native app) |
| Implementation effort to submit | Medium (new SDK + auth) | **Low (prompt changes + theme + seed data)** | Very High (full rebuild on M365) |
| Mandatory requirement risk | High (WorkIQ admin consent + Copilot SDK) | **Low (MAF + Azure OpenAI already deployed and working)** | High (M365 Copilot license + sideloading) |
| Reasoning pattern weight in scoring | 20% | **25% (highest single criterion)** | Not explicitly weighted |
| Multi-agent bonus scoring | Not specifically scored | **Explicitly listed as "Going Further" bonus** | 15 points for connected agents |
| Time to demo-ready state | ~4-6 hours | **~2-3 hours** | ~8+ hours (if possible at all) |

---

## 2. Track Recommendation & Rationale

### **Recommended Track: Track 2 — Reasoning Agents with Microsoft Foundry (via MAF)**

**The scenario is literally what we're building.** Track 2's project scenario reads:

> *"Build an AI agent that can effectively assist the communication team of a company in creating social media content for various platforms. Feel creative and choose a specific industry or type of brand."*

This is a 1:1 match with our Social Media Command Center. Here's why Track 2 maximizes our scoring:

#### 1. We Already Have the Architecture (Bonus Territory)

The "Going Further" section of Track 2's starter kit lists these as aspirational items that most entries won't attempt:

| Bonus Item | Track 2 Description | Our Implementation |
|------------|--------------------|--------------------|
| Multi-agent system | "Break down into specialized agents for content ideation, creation, scheduling" | **7 specialized agents** orchestrated in parallel |
| Reviewer agent | "Create a reviewer agent that checks content for quality and compliance" | **Advisor agent** with Self-Reflection pattern |
| Evaluation | "Set up evaluation metrics using Foundry's built-in tools" | **Trace service** — per-agent execution time, tokens, success/failure |
| Monitoring | "Implement monitoring to track usage and performance" | **Real-time WebSocket agent status panel** + DB trace table |
| Safety | "Add safety mitigation layers" | **Advisor agent** brand compliance review + content quality checks |

We're not just meeting requirements — we're implementing every bonus item they describe.

#### 2. Reasoning Patterns Already Embedded (25% of Score)

Our agent prompts already use all three reasoning patterns Track 2 values:

- **Chain-of-Thought (CoT)** → Strategist: "Step 1: IDENTIFY audience... Step 2: ANALYZE message... Step 3: DETERMINE tone..."
- **ReAct (Reasoning + Acting)** → Researcher: "Thought → Action → Observation → Thought..."
- **Self-Reflection** → Advisor: "Initial Review → Reflection → Revised Assessment"
- **Orchestrator decomposition** → Step-by-step task analysis and parallel dispatch

#### 3. Microsoft Agent Framework (MAF) Is Our Foundry Integration

Our `backend/app/agents/factory.py` uses MAF's `AzureOpenAIResponsesClient` to create agents that connect to Azure OpenAI via Foundry endpoints (`AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_KEY`). MAF is already installed (`agent-framework==1.0.0b251120`) with full MCP support, OpenTelemetry tracing, and `@tool` decorated functions. The `create_agent()` function returns MAF agents that call Azure OpenAI reasoning models — this IS the Foundry integration. No additional SDK (like `azure-ai-projects`) is needed.

#### 4. Full-Stack UI Is Our Unfair Advantage

Track 2 expects submissions built in the **Foundry Playground** or as **Python scripts**. We're showing up with:

- Next.js 16 + Shadcn/ui polished interface
- Real-time agent status panel via WebSocket
- Professional landing page with agent visualization
- Conversation history with chat-like UX

UX is worth 15% of the score — points most entries will entirely forfeit.

#### 5. MCP Integration Is Straightforward

Track 2 starter kit specifically suggests:
- **Microsoft Learn MCP server** for knowledge retrieval
- **Filesystem MCP server** for saving content drafts
- **DuckDuckGo Search** for web-grounded content (no API key required)

All of these integrate as npm packages spawned from our backend — no new auth flows, no admin consent required.

### Fallback: Track 1 (Creative Apps)

If we encounter Foundry-specific issues, we can pivot to Track 1. See [Section 14](#14-track-1-creative-apps--alternate-plan) for details.

---

## 3. What We're Building

**Social Media Command Center** — A multi-agent AI platform built with **Microsoft Agent Framework (MAF)** on Azure OpenAI (Foundry) that helps a brand's communication team ideate, research, write, review, and schedule social media content across platforms (LinkedIn, Twitter/X, Instagram), grounded in brand data and industry knowledge.

**Brand Focus:** TechVista Inc. — a fictional enterprise AI company (technology industry)

### Track 2 Milestones Mapping

| Milestone | Track 2 Requirement | Our Implementation |
|-----------|---------------------|-------------------|
| **M1: Set up environment** | Deploy a reasoning model in Foundry | Already done: Azure OpenAI GPT models deployed. MAF installed with `factory.py` providing `AzureOpenAIResponsesClient` + `create_agent()`. |
| **M2: Create your agent** | Define instructions, brand context, target audience, reasoning patterns | 7 MAF agents with CoT/ReAct/Self-Reflection created via `factory.py`. Orchestrator decomposes and coordinates with parallel `asyncio.gather`. |
| **M3: Add grounding knowledge** | Integrate relevant data sources (brand guidelines, industry trends) | Brand guidelines doc, past post performance data, content style guide — seeded in knowledge base + loaded as grounding files. |
| **M4: Add external tools** | Integrate MCP servers or APIs | MAF `@tool` decorators in factory.py + Microsoft Learn MCP for industry knowledge, filesystem MCP for draft persistence. |

### "Going Further" Bonus — We Already Have This

| Bonus | Their Description | Our Status |
|-------|-------------------|------------|
| Multi-agent architecture | "Break down into specialized agents" | **7 agents** with parallel orchestration |
| Reviewer agent | "Checks content for quality/compliance" | **Advisor agent** with Self-Reflection |
| Evaluation | "Foundry's built-in evaluation tools" | **Trace service** per-agent metrics |
| Monitoring | "Track usage and performance" | **WebSocket agent status panel** + DB traces |
| Safety | "Safety mitigation layers" | **Advisor** brand compliance checks |

### User Story

> "As a social media manager for TechVista (a tech company), I want to create a week of social media content based on our product announcements and industry trends, so I can maintain consistent brand presence across LinkedIn, Twitter/X, and Instagram."

### Demo Flow

1. User types: *"Create a LinkedIn post about our new AI Collaboration Suite launch, incorporating trending industry topics"*
2. **Orchestrator** analyzes intent (structured output) → `content_creation`, dispatches 6 agents in parallel
3. **Researcher** gathers trending AI topics, competitor social content, relevant hashtags (ReAct pattern)
4. **Strategist** creates per-platform strategy: audience, tone, posting schedule (Chain-of-Thought)
5. **Memory** retrieves TechVista brand guidelines, past high-performing posts, style preferences
6. **Scribe** generates platform-specific content (LinkedIn article, tweet thread, Instagram caption)
7. **Advisor** reviews for brand compliance — scores content, suggests improvements (Self-Reflection)
8. **Analyst** recommends optimal posting times based on engagement benchmarks
9. **Frontend** shows all agents working in real-time via WebSocket status panel
10. Final output: platform-specific posts + content calendar + compliance report

### Output Artifacts

- Platform-specific social media posts (LinkedIn, Twitter/X, Instagram)
- Content calendar with recommended posting schedule
- Brand compliance report with score (1-10)
- Supporting trend research brief
- Document saved to DB and surfaced in Documents page

---

## 4. Judging Criteria & How We Score

Track 2 evaluation rubric:

| Criterion | Weight | Our Strength | Target |
|-----------|--------|-------------|--------|
| **Accuracy & Relevance** | 25% | Multi-agent system directly addresses the social media content creation scenario. Brand-grounded with real guidelines and past data. | High |
| **Reasoning & Multi-step Thinking** | 25% | Orchestrator intent decomposition + explicit CoT (Strategist), ReAct (Researcher), Self-Reflection (Advisor) in prompts. Multi-agent parallel execution IS multi-step reasoning. | Very High |
| **Creativity & Originality** | 20% | Full-stack web app with 7 coordinated agents + real-time visualization — when competitors show Playground demos. Multi-agent for social media is the "Going Further" bonus. | Very High |
| **User Experience & Presentation** | 15% | Next.js 16 + Shadcn/ui + WebSocket agent panel + polished landing page + chat interface. Most entries will have no UI. | Very High |
| **Technical Implementation** | 15% | FastAPI + async agents + parallel execution + structured outputs + trace service + SQLite persistence. Production-quality patterns. | High |

**Scoring Strategy:** We are strong across all criteria but disproportionately strong on Reasoning (25%), Creativity (20%), and UX (15%). These three total 60% — areas where our multi-agent full-stack platform far exceeds what single-agent Playground entries can offer.

---

## 5. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js 16 Frontend                       │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Chat UI  │  │ Agent Status │  │  Content Dashboard   │  │
│  │ (input)  │  │   Panel (WS) │  │  (generated posts)   │  │
│  └─────┬────┘  └──────────────┘  └──────────────────────┘  │
└────────┼────────────────────────────────────────────────────┘
         │ REST API + WebSocket
┌────────▼────────────────────────────────────────────────────┐
│         FastAPI Backend + Microsoft Agent Framework (MAF)     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  MAF Factory (factory.py)                             │   │
│  │  AzureOpenAIResponsesClient → create_agent()          │   │
│  │  @tool decorators for agent capabilities               │   │
│  └──────────────────────┬────────────────────────────────┘   │
│                         │                                     │
│  ┌──────────────────────▼─────────────────────────────┐     │
│  │              Orchestrator Agent                      │     │
│  │   Intent Analysis → Parallel Dispatch → Synthesis    │     │
│  │    (asyncio.gather — Step-by-step decomposition)     │     │
│  └──┬──────┬──────┬──────┬──────┬──────┬──────────────┘     │
│     │      │      │      │      │      │                     │
│  ┌──▼──┐┌──▼──┐┌──▼──┐┌──▼──┐┌──▼──┐┌──▼──┐                │
│  │Strat││Rsrch││Anlst││Scrbe││Advsr││Memry│  ← MAF agents  │
│  │egist││cher ││     ││     ││     ││     │  via factory.py │
│  │ CoT ││ReAct││Data ││Write││Self-││Brand│                │
│  │     ││     ││     ││     ││Rflct││ RAG │                │
│  └─────┘└─────┘└─────┘└─────┘└─────┘└─────┘                │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ MS Learn MCP │  │ Filesystem   │  │  DuckDuckGo  │      │
│  │ (docs/trends)│  │ MCP (drafts) │  │ (web search) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────────────────────┐                            │
│  │     Trace Service            │                            │
│  │  (Evaluation & Monitoring)   │                            │
│  └──────────────────────────────┘                            │
│                                                              │
│  ┌──────────────────────────────┐                            │
│  │     SQLite (aiosqlite)       │                            │
│  │  conversations, messages,    │                            │
│  │  agent_traces, documents,    │                            │
│  │  knowledge_items             │                            │
│  └──────────────────────────────┘                            │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow — Content Creation Request

```
User: "Create LinkedIn post about our AI Collaboration Suite launch"
  │
  ▼
Orchestrator — structured_output() → intent: "content_creation"
  │                                   platforms: ["linkedin"]
  │
  ├── [Wave 1: PARALLEL gather context] ──────────────────────
  │   │                    │                │                  
  │   ▼                    ▼                ▼                  
  │  Researcher           Strategist       Memory             
  │  (trending AI topics, (content plan:   (brand guidelines, 
  │   competitor posts,    audience=CTOs,   past LinkedIn      
  │   hashtags — ReAct)    tone=thought     successes,         
  │                        leadership —     style prefs)       
  │                        CoT)                                
  │   │                    │                │                  
  │   └────────────────────┴────────┬───────┘                  
  │                                 │
  │                                 ▼
  │         Orchestrator (merges context for Wave 2)
  │                                 │
  ├── [Wave 2: PARALLEL create + review] ─────────────────────
  │   │                    │                │                  
  │   ▼                    ▼                ▼                  
  │  Scribe               Analyst          Advisor            
  │  (LinkedIn post with  (optimal post    (brand compliance  
  │   hook, body, CTAs,    timing, reach    review, score 1-10,
  │   hashtags)            estimate)        Self-Reflection)   
  │   │                    │                │                  
  │   └────────────────────┴────────┬───────┘                  
  │                                 │
  │                                 ▼
  │                      Orchestrator (final synthesis)
  │                      ├── Document saved to DB
  │                      ├── WS: document.generated event
  │                      └── Trace completed with metrics
  ▼
Frontend renders: post content, compliance report, agent activity timeline
```

### Reasoning Pattern Map

| Agent | Pattern | How It Works |
|-------|---------|-------------|
| **Orchestrator** | Step-by-step decomposition | "Step 1: Identify platforms... Step 2: Gather context... Step 3: Generate content..." |
| **Strategist** | Chain-of-Thought (CoT) | Explicit numbered steps: identify audience → analyze message → determine tone → plan calendar → recommend CTAs |
| **Researcher** | ReAct (Reasoning + Acting) | Thought → Action → Observation → Thought → Action loops for trend discovery |
| **Advisor** | Self-Reflection | Initial Review → "Is this on-brand?" → Reflection → Revised Assessment with scoring |
| **Scribe** | Template-guided generation | Platform-specific rules (LinkedIn: 1300 chars, hook first; Twitter: 280 chars, punchy) |
| **Analyst** | Data-driven benchmarking | Compare against engagement baselines, recommend based on evidence |
| **Memory** | Retrieval-augmented grounding | Semantic search over brand guidelines + past successful posts |

---

## 6. Prerequisites & Setup

### Required Accounts & Access

- [x] **Azure OpenAI access** — Already configured in `.env` (endpoint + key + deployment)
- [x] **Python 3.10+** — Already in use with venv
- [x] **Node.js 18+** — Already used for Next.js frontend
- [x] **Microsoft Agent Framework** — Already installed (`agent-framework==1.0.0b251120`) in `requirements.txt`
- [ ] **Azure subscription with model quota** — Need 100k-300k TPM for reasoning models
- [ ] **Azure CLI installed** — For `DefaultAzureCredential` (optional: we use API key auth)

### Installation Steps

```bash
# 1. Backend — MAF already installed via requirements.txt
cd backend
source .venv/bin/activate
pip install -r requirements.txt  # agent-framework is already listed

# 2. Verify MAF + Azure OpenAI connectivity
python -c "from app.agents.factory import create_agent; print('MAF + Azure OpenAI OK')"

# 3. Install MCP servers (for tool integration)
npm install -g @modelcontextprotocol/server-filesystem

# 4. Frontend — Already set up
cd frontend && pnpm install

# 5. Verify Azure OpenAI connectivity
cd backend
python -c "from app.services.llm_service import get_llm_service; print('LLM OK')"

# 6. Seed brand data
python -c "from app.data.seed import seed_social_media_data; import asyncio; asyncio.run(seed_social_media_data())"

# 7. Start backend
uvicorn app.main:app --reload --port 8000

# 8. Start frontend (new terminal)
cd frontend && pnpm dev
```

### Key Dependency (already in requirements.txt)

```
# MAF — Microsoft Agent Framework (already listed in requirements.txt)
agent-framework  # Includes: mcp, openai, azure-identity, opentelemetry
```

No additional SDK installations are needed. MAF's `AzureOpenAIResponsesClient` connects directly to Azure OpenAI via Foundry endpoints.

---

## 7. Implementation Plan

### Phase 1: Retheme Agent Prompts with Reasoning Patterns (P0)

**Goal:** Transform all agent prompts from "consulting proposals" to "social media content creation" with explicit reasoning patterns.

**File:** `backend/app/agents/prompts.py` — Full replacement

Key changes:
- Orchestrator: Step-by-step decomposition for content creation workflows
- Strategist: Chain-of-Thought for platform strategy (Step 1... Step 2... Step 3...)
- Researcher: ReAct pattern for trend discovery (Thought → Action → Observation)
- Scribe: Platform-specific writing rules (LinkedIn 1300 chars, Twitter 280 chars, Instagram visual-first)
- Advisor: Self-Reflection for brand compliance (Initial Review → Reflection → Revised Assessment)
- Memory: Brand knowledge retrieval + past post performance
- Analyst: Engagement benchmarking + posting time optimization

All three reasoning patterns (CoT, ReAct, Self-Reflection) are explicitly named and structured in prompts to maximize the **Reasoning & Multi-step Thinking (25%)** criterion.

### Phase 2: Wire Agents Through MAF Factory (P0)

**Goal:** Ensure all agents are created via MAF's `create_agent()` in `factory.py` so the submission demonstrates Microsoft Agent Framework as the orchestration layer.

**File:** `backend/app/agents/factory.py` — Expand agent definitions

Key changes:
1. Update `AGENT_TOOLS` to include social-media-specific tools (search_trends, analyze_hashtags, etc.)
2. Add social-media-themed `@tool` decorated functions for each agent's capabilities
3. Ensure each agent is instantiated via `create_agent(name, instructions, tools)` with its prompts from Phase 1

**File:** `backend/app/agents/orchestrator.py` — Bridge MAF into parallel dispatch

Key changes:
1. Import `create_agent` from `factory.py` to create MAF agent instances
2. Use MAF agents within the existing `asyncio.gather` parallel dispatch pattern
3. Maintain WebSocket status updates and trace service integration alongside MAF

The existing parallel `asyncio.gather` orchestrator pattern is preserved — MAF agents execute within it.

### Phase 3: Update Intent Schema & Routing (P0)

**Goal:** Update orchestrator to understand social media intents and route agents appropriately.

**File:** `backend/app/agents/orchestrator.py`

Changes:
1. New intent types: `content_creation`, `content_strategy`, `content_review`, `trend_research`
2. Add `target_platforms` field to intent schema (`linkedin`, `twitter`, `instagram`, `all`)
3. Update routing: content_creation dispatches all 6 agents; trend_research dispatches researcher + analyst + memory
4. Save generated content as Document with `doc_type="social_post"`

### Phase 4: Grounding Data — Brand Guidelines + Synthetic Data (P0)

**Goal:** Create synthetic brand data that grounds the agents in a realistic social media context.

Files to create:
- `backend/data/brand_guidelines.md` — TechVista brand voice, tone per platform, hashtag strategy, DOs/DON'Ts
- `backend/data/past_posts.json` — 5-10 sample high-performing posts with engagement metrics
- `backend/data/content_calendar.json` — Sample weekly content plan

The Memory agent reads these files at query time. The seed script loads them into the `knowledge_items` table with embeddings for semantic search.

### Phase 5: MCP Tool Integration (P1)

**Goal:** Connect external tools via MCP as Track 2 milestone 4 requires. MAF has **built-in MCP support** (`mcp` is a core dependency of `agent-framework`).

Options (pick one or more):
1. **Microsoft Learn MCP** (`@microsoftdocs/mcp`) — Query official Microsoft docs for industry-relevant technical content to reference in posts
2. **Filesystem MCP** (`@modelcontextprotocol/server-filesystem`) — Save generated content drafts to `./data/drafts/` for persistence
3. **DuckDuckGo Search** (`duckduckgo-search` Python package) — Free web search with no API key required, for real-time trend grounding

Implementation: MAF agents can connect to MCP servers natively. The `agent-framework` package includes `mcp` support — MCP servers are spawned as subprocesses and tools are registered on MAF agents automatically.

### Phase 6: Frontend — Generate UI with GitHub Copilot + Vercel Skills (P1)

**Goal:** Build/update the Next.js frontend using **GitHub Copilot** with **Vercel agent skills** — the development process itself is part of the demo.

**Development Workflow:**
1. Use GitHub Copilot in VS Code with Vercel agent skills loaded (`.agents/skills/vercel-composition-patterns`, `.agents/skills/vercel-react-best-practices`)
2. Prompt Copilot to generate/refactor each component following Vercel composition patterns (compound components, explicit variants, no boolean prop sprawl)
3. Copilot generates Next.js 16 + React 19 + Shadcn/ui code that follows best practices from the skills
4. Record the Copilot-driven generation process for the demo video

**Components to generate/update via Copilot:**
- Landing page: Prompt Copilot to retheme hero, agents section, capabilities for social media
- Chat interface: Prompt Copilot to update placeholder text and welcome message with social media examples
- Sidebar: Prompt Copilot to update navigation labels (Proposals → Content, Research → Trends)
- Agent status panel: Prompt Copilot to add social-media-themed task descriptions per agent
- Types/Store: Agent names remain the same (no type changes needed since agent roles are prompt-driven)

**Why this matters for scoring:**
- Shows GitHub Copilot as a first-class development tool (appealing to judges across all tracks)
- Vercel skills ensure generated code follows production React patterns
- The Copilot-driven workflow is itself a compelling demo moment — "We used AI agents to build an AI agent platform"

### Phase 7: Evaluation & Monitoring — Bonus (P2)

**Goal:** Showcase the tracing/evaluation capabilities that Track 2 lists as "Going Further" bonus.

What we already have:
- `agent_traces` table with per-agent execution time, tokens, success/failure
- `trace_service.py` for programmatic trace creation
- Agent status panel showing real-time execution via WebSocket

Enhancement: Add a simple `/api/analytics/social` endpoint that returns:
- Average content generation time
- Agent utilization per content type
- Token usage breakdown by agent
- Content compliance scores over time

### Phase 8: Demo & Submission (P0)

See [Section 11: Demo Script](#11-demo-script) and [Section 12: Submission Checklist](#12-submission-checklist).

---

## 8. File-by-File Change Map

### Files to Modify

| File | Change | Priority |
|------|--------|----------|
| `backend/app/agents/prompts.py` | Replace all prompts with social media theme + explicit reasoning patterns (CoT, ReAct, Self-Reflection) | **P0** |
| `backend/app/agents/orchestrator.py` | Update intent schema (add `content_creation`, `target_platforms`), update routing logic for social media, wire parallel dispatch through MAF `create_agent()` | **P0** |
| `backend/app/agents/factory.py` | Expand `AGENT_TOOLS` with social-media-specific `@tool` functions, update `create_agent()` calls for all 7 agents | **P0** |
| `backend/requirements.txt` | Already has `agent-framework` — add `duckduckgo-search` for web grounding | **P0** |
| `backend/app/data/seed.py` | Add `seed_social_media_data()` function to load brand guidelines + past posts into knowledge_items | **P0** |
| `frontend/src/components/landing/hero-section.tsx` | Update headline, description, sample prompts to social media theme | **P1** |
| `frontend/src/components/landing/agents-section.tsx` | Update agent roles/descriptions to match social media focus | **P1** |
| `frontend/src/components/landing/capabilities-section.tsx` | Replace capabilities with Content Creation / Trend Research / Brand Intelligence | **P1** |
| `frontend/src/components/chat/chat-interface.tsx` | Update placeholder text and welcome message | **P1** |
| `frontend/src/components/sidebar.tsx` | Update nav labels (Proposals→Content, Research→Trends) | **P1** |
| `frontend/src/components/landing/paradigm-shift-section.tsx` | Update before/after to reflect social media workflow transformation | **P2** |
| `frontend/src/components/landing/roadmap-section.tsx` | Update phases to social media platform roadmap | **P2** |
| `frontend/src/components/landing/footer-section.tsx` | Update branding and links | **P2** |
| `frontend/src/components/landing/landing-nav.tsx` | Update nav text | **P2** |
| `README.md` | Rewrite for hackathon submission (what, architecture, screenshots, how to run, technologies) | **P0** |

### Files to Create

| File | Purpose | Priority |
|------|---------|----------|
| `backend/data/brand_guidelines.md` | TechVista brand voice, tone per platform, hashtag strategy | **P0** |
| `backend/data/past_posts.json` | Synthetic past post performance data (5-10 examples) | **P0** |
| `backend/data/content_calendar.json` | Sample weekly content plan template | **P1** |
| `backend/data/drafts/.gitkeep` | Directory for filesystem MCP to save content drafts | **P1** |

### Files to NOT Touch

| File | Reason |
|------|--------|
| `backend/app/main.py` | No changes needed — agents integrate through orchestrator |
| `backend/app/services/llm_service.py` | Existing Azure OpenAI service used alongside MAF for streaming/embeddings. No major changes — MAF agents handle completions via factory.py |
| `backend/app/api/websocket.py` | WebSocket events already support any agent name |
| `backend/app/models/database.py` | Schema already supports documents with any `doc_type` |
| `backend/app/services/trace_service.py` | Already traces all agents generically |
| `backend/app/models/schemas.py` | Existing schemas work for social media content |
| `frontend/src/lib/websocket.ts` | Already handles all agent event types |
| `frontend/src/lib/api.ts` | API client already supports all needed endpoints |
| `frontend/src/lib/store.ts` | Agent names are prompt-driven, no store changes needed |
| `frontend/src/lib/types.ts` | Agent type union already covers our 7 agents |

---

## 9. New Files to Create

### `backend/data/brand_guidelines.md`

```markdown
# TechVista Inc. — Brand & Social Media Guidelines

## Brand Voice
- **Professional yet approachable** — We're experts who don't talk down to anyone
- **Innovation-forward** — We always lead with what's new and what's next
- **Human-centered** — Technology serves people, not the other way around

## Tone by Platform
- **LinkedIn:** Thought leadership, professional insights, team celebrations
- **Twitter/X:** Quick takes, tech humor, community engagement, announcements
- **Instagram:** Behind-the-scenes, team culture, product visuals, stories

## Key Messages
1. "AI that works with you, not instead of you"
2. "Building the future of intelligent collaboration"
3. "Enterprise AI, made simple"

## Hashtag Strategy
- Always use: #TechVista #AIInnovation
- LinkedIn: #EnterpriseAI #FutureOfWork #DigitalTransformation
- Twitter: #AI #TechTuesday #BuildInPublic
- Instagram: #TechLife #TeamTechVista #BTS

## DOs and DON'Ts
### DO:
- Share team achievements and milestones
- Reference customer success stories (with permission)
- Engage with industry conversations
- Use data and metrics to support claims

### DON'T:
- Make unsubstantiated claims about competitors
- Use overly technical jargon without explanation
- Post about unannounced features
- Use stock photos — prefer authentic team images

## Audience Personas
1. **Tech Leaders** (LinkedIn): CTOs, VPs of Engineering, IT Directors
2. **Developers** (Twitter): Software engineers, ML practitioners
3. **Culture Seekers** (Instagram): Potential hires, tech community members
```

### `backend/data/past_posts.json`

```json
[
  {
    "platform": "linkedin",
    "content": "Excited to announce TechVista's new AI Collaboration Suite! After 18 months...",
    "engagement_rate": 4.2,
    "impressions": 15000,
    "likes": 630,
    "comments": 85,
    "shares": 120,
    "date": "2026-01-15",
    "performance": "high"
  },
  {
    "platform": "twitter",
    "content": "Just shipped v3.0 🚀 New features: → Real-time AI collaboration...",
    "engagement_rate": 3.8,
    "impressions": 8500,
    "likes": 323,
    "retweets": 145,
    "date": "2026-01-20",
    "performance": "high"
  },
  {
    "platform": "instagram",
    "content": "Meet the team behind our latest breakthrough! 🎉...",
    "engagement_rate": 5.1,
    "impressions": 12000,
    "likes": 612,
    "comments": 94,
    "date": "2026-02-01",
    "performance": "very_high"
  },
  {
    "platform": "linkedin",
    "content": "The biggest myth in enterprise AI? That it replaces people...",
    "engagement_rate": 5.8,
    "impressions": 22000,
    "likes": 1276,
    "comments": 203,
    "shares": 340,
    "date": "2025-12-10",
    "performance": "viral"
  },
  {
    "platform": "twitter",
    "content": "Hot take: The best AI product is the one your team actually uses...",
    "engagement_rate": 4.5,
    "impressions": 11000,
    "likes": 495,
    "retweets": 210,
    "date": "2025-11-28",
    "performance": "high"
  }
]
```

---

## 10. Security Checklist

Before submission, verify (per Track 2 security requirements):

- [ ] **No API keys in code** — All keys in `.env`, `.env` is in `.gitignore`
- [ ] **No Azure subscription IDs** — Use environment variables (`AZURE_OPENAI_ENDPOINT`)
- [ ] **No Azure resource names** — Connection strings use env vars
- [ ] **No tenant IDs or domain names** — Not hardcoded anywhere
- [ ] **No PII** — Brand data is synthetic (TechVista is fictional), no real employee names
- [ ] **No Microsoft Confidential info** — Only general-level content
- [ ] **`.env.example` has placeholders** — Not real values
- [ ] **No screenshots with sensitive data** — Review all images before submitting
- [ ] **Use `DefaultAzureCredential` or env vars** — No hardcoded credentials in MAF or Azure OpenAI calls
- [ ] **Git history clean** — Run `git log --diff-filter=A -- '*.env' '*.key'` to verify
- [ ] **Scan for secrets** — Run `git grep -i "key\|secret\|password\|token\|subscription"` before push
- [ ] **Enable GitHub Secret Protection** — On the repository settings

---

## 11. Demo Script

### Primary Demo Prompt
> "Create a week of social media content for TechVista's AI Collaboration Suite launch. Target LinkedIn, Twitter, and Instagram. Use our brand guidelines and trending AI topics."

### Quick Demo Prompt (shorter path)
> "Write a LinkedIn post announcing our new AI-powered meeting insights feature. Make it thought-leadership focused."

### Research-Focused Prompt
> "What are the trending AI topics on social media this week? How should we position our content strategy?"

### Review Prompt (shows Self-Reflection pattern)
> "Review this draft tweet for brand alignment: 'Our new AI tool is the best thing ever! Buy it now! #AI #Amazing'"

### Expected Agent Activity Timeline

```
0s    Orchestrator: Analyzing intent... (structured output)
0.5s  Orchestrator: Intent=content_creation, platforms=[linkedin,twitter,instagram]
      Dispatching 6 agents in parallel...

1s    [WAVE 1: Context Gathering — PARALLEL]
      Researcher:  Searching trending AI topics... (ReAct: Thought → Action → Observation)
      Strategist:  Building content strategy... (CoT: Step 1 → Step 2 → Step 3)
      Memory:      Loading brand guidelines + past posts...
      Analyst:     Analyzing engagement benchmarks...

3-5s  [WAVE 1 COMPLETE]

5s    [WAVE 2: Content Creation + Review — PARALLEL]
      Scribe:      Writing LinkedIn post... Twitter thread... Instagram caption...
      Advisor:     Reviewing for brand compliance... (Self-Reflection: Review → Reflect → Revise)

7-9s  [WAVE 2 COMPLETE]

9s    Orchestrator: Synthesizing final output...
10s   → Document saved to DB (doc_type: "social_post")
      → WebSocket: document.generated event
      → Response rendered with posts, calendar, compliance score
```

### Demo Video Structure (5 minutes)

**Part 1: Build It — GitHub Copilot + Vercel Skills (2 min)**

1. **0:00-0:20** — Show VS Code with Copilot + Vercel agent skills loaded in the workspace
2. **0:20-0:50** — Prompt Copilot to generate a social media content dashboard component using Vercel composition patterns: "Create a content calendar component with compound pattern using Shadcn/ui..." Show Copilot generating Next.js 16 / React 19 code
3. **0:50-1:20** — Prompt Copilot to refactor the agent status panel for social media theme: "Update agent descriptions to show social media content creation tasks..." Show the code being generated in real-time
4. **1:20-2:00** — Run `pnpm dev`, show the generated UI rendering in the browser — landing page, chat interface, agent panel all themed for social media

**Part 2: Use It — Multi-Agent Content Creation (3 min)**

5. **2:00-2:20** — Landing page tour: "This is Social Media Command Center, built with Microsoft Agent Framework on Azure OpenAI, UI generated with GitHub Copilot"
6. **2:20-2:40** — Show the agent panel: "7 specialized agents, each with a specific reasoning pattern"
7. **2:40-3:30** — Type the primary demo prompt, show agents activating in real-time via WebSocket
8. **3:30-4:15** — Walk through the generated content: LinkedIn post, tweet thread, Instagram caption, compliance score
9. **4:15-4:40** — Highlight reasoning: "Strategist used Chain-of-Thought, Researcher used ReAct, Advisor used Self-Reflection"
10. **4:40-5:00** — Architecture slide: "7 MAF agents, 3 reasoning patterns, Microsoft Agent Framework + Azure OpenAI (Foundry), GitHub Copilot + Vercel skills for UI, real-time WebSocket monitoring"

---

## 12. Submission Checklist

- [ ] Code is in a **public GitHub repository**
- [ ] Repository has a **clear README** with:
  - [ ] What it does (2-3 sentences)
  - [ ] Architecture diagram (the ASCII diagram from Section 5)
  - [ ] Screenshots of: (a) landing page, (b) chat with agents working, (c) generated content
  - [ ] Screenshots/GIFs of GitHub Copilot generating UI components with Vercel skills
  - [ ] Video link (optional but strongly recommended) — show Copilot building the UI + agents running
  - [ ] How to run it (`setup_db.py`, uvicorn, pnpm dev)
  - [ ] Technologies: Microsoft Agent Framework (`agent-framework`), Azure OpenAI (Foundry), FastAPI, Next.js 16, Shadcn/ui, SQLite, GitHub Copilot, Vercel Agent Skills, MCP
  - [ ] Development workflow: GitHub Copilot + Vercel skills → Next.js component generation
  - [ ] Reasoning patterns used: CoT, ReAct, Self-Reflection (with specific examples)
  - [ ] MCP integration explanation
- [ ] [DISCLAIMER.md](https://github.com/microsoft/agentsleague-techconnect/blob/main/DISCLAIMER.md) reviewed
- [ ] [Code of Conduct](https://github.com/microsoft/agentsleague-techconnect/blob/main/CODE_OF_CONDUCT.md) reviewed
- [ ] Security checklist (Section 10) complete
- [ ] All brand data is synthetic (TechVista = fictional company)
- [ ] Submit via [project submission template](https://github.com/microsoft/agentsleague-techconnect/issues/new?template=project.yml)
- [ ] **Microsoft alias included** in submission
- [ ] Submitted **before Feb 13, 2026, 11:59 PM PT**

---

## 13. Risk Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| **Azure OpenAI quota exceeded** | Agents can't generate responses | Low | Reduce `max_tokens` for non-critical agents. Use `gpt-4o-mini` for lighter agents (Analyst, Memory). |
| **MAF agent creation fails** | Agents can't execute via MAF | Very Low | MAF is already installed and `factory.py` works. If MAF `create_agent()` fails, we fall back to `llm_service.py` direct Azure OpenAI calls — same endpoints, same models. |
| **MCP server spawn fails** | Tool integration doesn't work | Medium | MCP is an enhancement, not core. Agents work without it. Gracefully catch subprocess errors. |
| **WebSocket disconnects during demo** | Agent panel goes stale | Low | Frontend already has reconnection logic with exponential backoff. Status panel shows last known state. |
| **Rate limiting on Azure** | Slow or failed responses | Medium | Agents already run in `asyncio.gather` for parallelism. Add retry with backoff. Pre-warm models before demo. |
| **Model hallucinations in content** | Brand-inappropriate content generated | Medium | **Advisor agent** specifically reviews for brand compliance. Self-Reflection pattern catches issues. |
| **Time pressure** | Can't finish all phases | Medium | Priority order: P0 (prompts + orchestrator + seed data + README) first. P1 (frontend polish) second. P2 (landing page updates) only if time permits. |
| **Judges don't run the app** | Only see README/screenshots | High | Invest in README quality: clear screenshots, architecture diagram, video link. The README IS the submission for many judges. |

### Minimum Viable Submission (P0 Only)

If time is extremely tight, here's the absolute minimum to submit:

1. Update `prompts.py` — Social media theme + explicit reasoning patterns
2. Update `factory.py` — Expand MAF agents with social-media-specific `@tool` functions
3. Update `orchestrator.py` — Intent schema with `content_creation` + `target_platforms` + MAF dispatch
4. Create `brand_guidelines.md` + `past_posts.json` — Grounding data
4. Update seed script — Load brand data into `knowledge_items`
5. Write README — What, architecture, screenshots, how to run
6. Take screenshots of the running app
7. Submit via template

Everything else (frontend polish, MCP integration, analytics endpoint) is bonus that scores extra points but isn't blocking.

---

## 14. Track 1 (Creative Apps) — Alternate Plan

If we pivot to Track 1 instead, here are the additional changes needed on top of the Track 2 plan:

### Additional Requirements for Track 1

| Requirement | Implementation |
|------------|----------------|
| **GitHub Copilot Usage** | (1) Document how Copilot was used during development (screenshots of chat + suggestions). (2) Optionally add `github-copilot-sdk` to create a Copilot-powered agent or CLI tool. |
| **MCP Integration** | Add WorkIQ MCP (`@microsoft/workiq`) for M365 data or use Microsoft Learn MCP / Filesystem MCP. At least one MCP server integration is mandatory. |
| **Creative Application** | Already satisfied — our full-stack web app with real-time agent visualization is highly creative. |

### Additional Files for Track 1

| File | Purpose |
|------|---------|
| `backend/app/services/copilot_service.py` | Copilot CLI SDK wrapper with MCP server config |
| `backend/app/agents/copilot_agent.py` | New agent that queries M365 via Copilot SDK + WorkIQ |

### Additional Dependencies for Track 1

```
pip install github-copilot-sdk
npm install -g @microsoft/workiq
```

### Risk Assessment for Track 1

| Risk | Severity |
|------|----------|
| WorkIQ M365 admin consent not granted | **HIGH** — blocks a mandatory requirement |
| Copilot CLI SDK auth fails | **HIGH** — blocks a mandatory requirement |
| WorkIQ EULA acceptance requirement | **MEDIUM** — interactive step, must be done in advance |

### Track 1 Evaluation Differences

| Criterion | Track 1 Weight | Track 2 Weight | Notes |
|-----------|---------------|---------------|-------|
| Accuracy & Relevance | 20% | 25% | Track 2 weighs this higher |
| Reasoning & Multi-step Thinking | 20% | 25% | Track 2 explicitly rewards reasoning |
| Creativity & Originality | 15% | 20% | Track 2 weighs creativity higher |
| UX & Presentation | 15% | 15% | Same |
| Reliability & Safety | 20% | 15% | Track 1 weighs reliability higher |
| Community Vote | 10% | N/A | Track 1 has Discord voting, Track 2 doesn't |

**Bottom line:** Track 1 is viable but carries higher auth/dependency risk and rewards reasoning patterns less. Track 2 is the stronger choice.

---

## Summary: Why We Win

1. **Scenario Match:** Track 2 asks for a social media content creation agent. We built a social media content creation platform with 7 specialized MAF agents.

2. **Architecture Depth:** Where competitors show a Foundry Playground demo, we show a production-quality multi-agent system built on **Microsoft Agent Framework (MAF)** with `AzureOpenAIResponsesClient`, `@tool` decorators, parallel orchestration via `asyncio.gather`, real-time monitoring, and structured output parsing.

3. **Reasoning Patterns (25%):** We explicitly implement all three patterns the rubric values — Chain-of-Thought, ReAct, Self-Reflection — in named, documented MAF agents.

4. **UX (15%):** A polished Next.js 16 app with Shadcn/ui components, real-time WebSocket agent panel, and professional landing page — **generated using GitHub Copilot with Vercel agent skills**. Most entries will have zero frontend.

5. **AI-Built AI:** We used AI agents (GitHub Copilot + Vercel skills) to build an AI agent platform. The development workflow itself is a compelling demo moment.

6. **Bonus Items Already Built:** Multi-agent architecture, reviewer agent, evaluation/tracing, monitoring, safety — every "Going Further" item Track 2 describes as aspirational, we already have.

7. **Zero New Dependencies:** MAF (`agent-framework`) is already installed and wired in `factory.py`. Azure OpenAI models are already deployed and configured. No new SDK installations, no new auth flows. We enhance what we have with better prompts, social media data, and MCP tools.
