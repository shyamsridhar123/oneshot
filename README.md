<p align="center">
  <img src="docs/graphics/hero-banner.svg" alt="OneShot Hero Banner" width="100%"/>
</p>

<h1 align="center">OneShot</h1>

<p align="center">
  <strong>You only get one shot. Do not miss your chance to blow.</strong><br/>
  <em>7 AI agents. Two parallel waves. One prompt. Platform-ready social content.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-16-black?logo=next.js&logoColor=white" alt="Next.js 16"/>
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black" alt="React 19"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python 3.11+"/>
  <img src="https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/Azure_OpenAI-GPT--5.x-0078D4?logo=microsoft-azure&logoColor=white" alt="Azure OpenAI"/>
  <img src="https://img.shields.io/badge/Tailwind-4-06B6D4?logo=tailwindcss&logoColor=white" alt="Tailwind 4"/>
  <img src="https://img.shields.io/badge/tests-215_passing-2ecc71?logo=pytest&logoColor=white" alt="215 tests"/>
  <img src="https://img.shields.io/badge/license-MIT-f39c12" alt="MIT License"/>
</p>

---

## The Problem

Enterprise social media teams hit the same bottleneck every day:

> Research → Strategy → Writing → Compliance → Analytics — **all sequential, all manual, all slow.**

Different people. Different tools. Handoff friction at every stage. By the time content ships, the trend is over.

## The Solution: OneShot

**OneShot** takes a single prompt — *"Write a LinkedIn post about our AI launch"* — and fires 7 specialized AI agents in two parallel waves. Research, strategy, brand context, analytics, writing, and compliance review happen **simultaneously**, not sequentially. Content comes out platform-specific, brand-compliant, data-backed, and scored.

Like a real content team — but in seconds. *You only get one shot at the first draft. Make it count.*

---

<p align="center">
  <img src="docs/graphics/stage-banner.svg" alt="OneShot — The Stage Is Set" width="100%"/>
</p>

---

## Two-Wave Parallel Architecture

<p align="center">
  <img src="docs/graphics/architecture-flow.svg" alt="Two-Wave Parallel Orchestration" width="100%"/>
</p>

```
User Prompt
     │
     ▼
 ORCHESTRATOR ──── intent classification, platform detection
     │
     ├── Wave 1: Context Gathering (parallel via asyncio.gather)
     │   ├── Researcher  [ReAct]            → trends, hashtags, competitors
     │   ├── Strategist  [Chain-of-Thought] → audience, messaging, tone
     │   ├── Memory      [RAG]             → brand guidelines, past posts
     │   └── Analyst     [Data-Driven]     → engagement benchmarks, timing
     │
     ├── Wave 1 context passed to Wave 2 via AgentContext
     │
     ├── Wave 2: Create + Review (parallel)
     │   ├── Scribe      [Template-Guided]  → platform-specific content
     │   └── Advisor     [Self-Reflection]  → compliance score (1-10)
     │
     ▼
 Brand-Compliant, Data-Backed Content
 (scored, traced, exportable to 4 formats)
```

**Key insight**: Wave 2 agents don't create blind — they receive all Wave 1 context. The Scribe writes *informed by* live trends, strategy, brand voice, and engagement data. The Advisor reviews against *actual* brand guidelines and past post patterns.

### Containerized Deployment with azd

Both services are now containerized and wired into `azd`.

1. Provision infrastructure:
    - `azd provision`
2. Deploy both application containers:
    - `azd deploy`
    - or run `azd up` for provision + deploy in one command.

The deployment flow currently excludes brand-data seeding. Continue using your team setup/bootstrap scripts for data initialization.

---

## The 7 Agents

<p align="center">
  <img src="docs/graphics/agent-roster.svg" alt="Meet the Agents" width="100%"/>
</p>

> *"This is not 7 copies of GPT with different system prompts."* — Each agent has a **named reasoning identity**.

| # | Agent | Reasoning Pattern | What It Does |
|:-:|-------|-------------------|-------------|
| 🎯 | **Orchestrator** | Step-by-Step Decomposition | Classifies intent, detects platforms, dispatches two-wave parallel execution |
| 🔍 | **Researcher** | ReAct (Reasoning + Acting) | Think → Act → Observe loops. Finds trends, analyzes hashtags, studies competitors |
| ♛ | **Strategist** | Chain-of-Thought (CoT) | Audience → Message → Tone → Calendar → CTA. Deliberate, explainable strategy |
| 🧠 | **Memory** | Retrieval-Augmented Grounding (RAG) | Retrieves brand guidelines, past post performance, content calendars. Zero hallucination |
| 📊 | **Analyst** | Data-Driven Benchmarking | Engagement predictions, optimal posting times, performance comparisons. Numbers, not guesses |
| ✍ | **Scribe** | Template-Guided Generation | Platform-specific templates: hook → body → CTA → hashtags. Saves drafts via MCP |
| 🛡 | **Advisor** | Self-Reflection | Initial review → metacognitive reflection → revised compliance score (1-10) |

---

## MCP & Tool Integration

Agents extend beyond pure language generation via [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers and direct tool integrations — spawned as subprocesses and auto-registered on MAF agents at runtime.

| Integration | Type | Agent | Purpose |
|-------------|------|-------|---------|
| **Filesystem MCP** (`@modelcontextprotocol/server-filesystem`) | MCP Server | Scribe | Saves generated content drafts to `./data/drafts/` |
| **DuckDuckGo Search** (`ddgs`) | Python Tool | Researcher | Live web search and news search for trend grounding |

```python
from agent_framework import MCPStdioTool

fs_mcp = MCPStdioTool(
    name="filesystem",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "./data/drafts"],
)
agent = client.create_agent(name="scribe", instructions=SCRIBE_PROMPT, tools=[fs_mcp])
```

> **Note:** The Fetch MCP server (`@anthropic-ai/mcp-server-fetch`) was originally included but has been disabled — the npm package was removed upstream. The Researcher agent uses DuckDuckGo live search (`ddgs` Python package) as a direct tool integration instead, which is faster and requires no API key.

MCP is optional — agents gracefully fall back to direct LLM calls when servers are unavailable.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 16, React 19, Shadcn/ui, Tailwind CSS 4, Zustand 5, Recharts |
| **Backend** | Python 3.11+, FastAPI 0.115, SQLAlchemy 2.x, aiosqlite |
| **AI** | Azure OpenAI GPT-5.x, Microsoft Agent Framework (MAF) |
| **Auth** | Azure Identity (`DefaultAzureCredential`) — zero secrets in config |
| **MCP** | Filesystem MCP (draft persistence) |
| **Search** | DuckDuckGo Search (`ddgs`) — live web and news search, no API key required |
| **Database** | SQLite with async support |
| **Real-time** | WebSocket agent status streaming (6 event types) |
| **Testing** | pytest + pytest-asyncio (215 tests) |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (pnpm recommended)
- Azure OpenAI resource with deployed models
- Azure CLI logged in (`az login`) for DefaultAzureCredential

### 1. Environment Setup

```bash
cp .env.example .env
```

Edit `.env`:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_VERSION=2025-03-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.2-chat
```

> **No API key needed.** The app uses `DefaultAzureCredential` — just `az login` first.

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Initialize database + seed data
python setup_db.py
python -c "from app.data.seed import seed_database; import asyncio; asyncio.run(seed_database())"
python -c "from app.data.seed import seed_social_media_data; import asyncio; asyncio.run(seed_social_media_data())"

# Start
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

Open **http://localhost:3000** → you're in.

### Docker Alternative

```bash
cp .env.example .env
docker-compose up
```

---

## Demo Scenarios

| Scenario | Prompt | What Fires |
|----------|--------|------------|
| **Content Creation** 🔥 | *"Write a LinkedIn post about our AI Collaboration Suite v3.0 launch"* | All 7 agents, both waves |
| **Multi-Platform Campaign** | *"Create content for all platforms about our healthcare deployment"* | Orchestrator detects 3 platforms, dispatches per-platform |
| **Trend Research** | *"What AI topics are trending on social media this week?"* | Researcher (ReAct loops with live web search) |
| **Content Review** | *"Review this draft tweet for brand alignment"* | Advisor (Self-Reflection pattern) + Memory (RAG) |

---

## Pages & Features

| Page | Route | What You See |
|------|-------|-------------|
| **Landing** | `/` | Project overview, agent showcase |
| **Chat** | `/chat` | Multi-agent conversation, real-time agent status panel |
| **Content** | `/proposals` | Generated social media content library, export |
| **Trends** | `/research` | Trend research, competitor analysis, hashtag data |
| **Brand** | `/knowledge` | Brand guidelines, past post performance, content calendar |
| **Analytics** | `/analytics` | Agent metrics, execution traces, token usage, charts |

---

## Real-Time Agent Streaming

WebSocket at `/ws/agents/{conversation_id}` streams live as agents work:

```
agent.started      → "Orchestrator: Analyzing request"
agent.thinking     → "Researcher: Searching AI trends..." (progress: 0.3)
agent.handoff      → "Orchestrator → Scribe: Generate content"
agent.completed    → "Advisor: Brand score 9/10" (duration: 600ms)
stream.token       → Token-by-token LLM streaming
document.generated → "Social Post: AI Launch Campaign"
```

6 event types. Full visibility into multi-agent execution.

---

## By The Numbers

| Metric | Value |
|--------|:-----:|
| Specialized AI agents | **7** |
| Named reasoning patterns | **7** |
| Agent tool functions | **14** |
| MCP server integrations | **1** (Filesystem) |
| Supported platforms | **3** (LinkedIn, Twitter/X, Instagram) |
| Export formats | **4** (Markdown, HTML, PDF, DOCX) |
| WebSocket event types | **6** |
| REST API endpoints | **15+** |
| Automated tests | **215** |
| Intent types | **4** (creation, strategy, review, research) |
| Brand data files | **3** (guidelines, past posts, content calendar) |
| Hardcoded secrets | **0** |

---

## Project Structure

```
oneshot/
├── frontend/                    # Next.js 16 + React 19
│   └── src/
│       ├── app/                 # App Router pages (chat, proposals, research, knowledge, analytics)
│       ├── components/          # Shadcn/ui components (landing, chat, sidebar, agent panel)
│       └── lib/                 # API client, Zustand store, WebSocket, types
├── backend/                     # FastAPI + Python 3.11
│   ├── app/
│   │   ├── agents/              # 7 AI agents with named reasoning patterns
│   │   │   ├── orchestrator.py  # Two-wave parallel dispatch
│   │   │   ├── prompts.py       # All agent prompts with reasoning patterns
│   │   │   └── factory.py       # MAF agent factory + MCP tool registration
│   │   ├── api/                 # REST endpoints + WebSocket handler
│   │   ├── models/              # SQLAlchemy models + Pydantic schemas
│   │   ├── services/            # LLM, documents, knowledge, traces
│   │   └── data/                # Seed data
│   ├── data/                    # Brand data (guidelines, posts, calendar, drafts/)
│   └── tests/                   # 215 tests across 12 modules
├── docs/
│   ├── graphics/                # SVG artwork (hero, agents, architecture, logo, stage)
│   ├── TRD.md                   # Technical Requirements Document
│   └── API.md                   # API documentation
├── .env.example                 # Environment template (zero secrets)
├── DEMO.md                      # Demo presentation script
├── SETUP.md                     # Detailed setup guide
└── Makefile                     # Common commands
```

---

## Testing

```bash
cd backend
source .venv/bin/activate
pytest                    # 215 tests, 12 modules, 100% pass rate
python demo_e2e.py        # 85 E2E demo checks
```

| Category | Count |
|----------|------:|
| Agent & tool tests | 53 |
| API endpoint tests | 37 |
| Analytics & trace tests | 26 |
| Document & proposal tests | 37 |
| WebSocket tests | 15 |
| Core & seed tests | 47 |
| **Total** | **215** |

---

## What Makes This Different

**It's not a chatbot — it's a team.** Most AI demos show one model answering one question. OneShot shows 7 agents with different specialties collaborating in parallel.

**Every agent has a reasoning identity.** ReAct for research. Chain-of-Thought for strategy. Self-Reflection for review. RAG for memory. These are the same patterns from academic AI research, implemented as production prompts.

**Two-wave architecture mirrors real workflows.** Wave 1 gathers context. Wave 2 creates with that context. Research and strategy happen before writing. Review happens after. We automated the workflow, not just the writing.

**Agents interact with the real world.** The Scribe saves files via MCP. The Researcher searches live web content via DuckDuckGo. Tool integrations turn language models into agents that act, not just generate.

**Zero secrets.** `DefaultAzureCredential` everywhere. `az login` for dev, Managed Identity for prod, service principals for CI — same code, no API keys.

**The AI reviews its own AI.** The Advisor uses Self-Reflection: generate an initial review, reflect on whether the review was thorough enough, then produce a revised score. Metacognition applied to content compliance.

---

<p align="center">
  <img src="docs/graphics/logo-badge.svg" alt="OneShot Logo" width="200"/>
</p>

<p align="center">
  <em>"Look — if you had one shot, or one opportunity, to seize everything you ever wanted, in one moment — would you capture it, or just let it slip?"</em>
</p>

<p align="center">
  <strong>We didn't let it slip.</strong>
</p>

---

## License

MIT License — see [LICENSE](LICENSE) for details.
