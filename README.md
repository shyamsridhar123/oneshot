# Federation

## AI-Powered Professional Services Engagement Platform

A demonstration platform showcasing how AI agents can transform professional services delivery. Built on Microsoft Agent Framework and Azure OpenAI GPT-5.x.

![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript)

---

## Overview

**Federation** deploys a coordinated team of specialized AI agents that mirror a consulting firm's operating model, enabling rapid proposal generation, intelligent research, and automated document creation.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│               Next.js 14 • Shadcn/ui • Tailwind                 │
│                     Zustand State Management                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST API / WebSocket
┌───────────────────────────▼─────────────────────────────────────┐
│                          BACKEND                                 │
│                    FastAPI • Python 3.11                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │Strategist│  │Researcher│  │ Analyst  │  │ Advisor  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       └─────────────┴──────┬──────┴─────────────┘              │
│                   ┌────────▼────────┐                           │
│                   │  ORCHESTRATOR   │                           │
│                   └────────┬────────┘                           │
│       ┌─────────────┬──────┴─────────────┐                      │
│  ┌────▼─────┐  ┌────▼─────┐  ┌───────────▼───┐                 │
│  │  Scribe  │  │  Memory  │  │ SQLite + RAG  │                 │
│  └──────────┘  └──────────┘  └───────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Roles

| Agent | Role | Key Capabilities |
|-------|------|------------------|
| **Orchestrator** | Coordinator | Task decomposition, agent dispatch, quality control |
| **Strategist** | Strategy | Engagement scoping, proposal generation, framework selection |
| **Researcher** | Intelligence | Web search, news synthesis, company research |
| **Analyst** | Analysis | Data visualization, financial modeling, benchmarking |
| **Scribe** | Documents | Document generation, formatting, branding |
| **Advisor** | Communications | Client comms, executive summaries, recommendations |
| **Memory** | Knowledge | RAG retrieval, past work discovery, semantic search |

---

## Demo Scenarios

1. **Rapid Proposal Generation** (Primary) — Generate client proposals in minutes, not weeks
2. **Client Intelligence Briefing** — Comprehensive briefings before client meetings
3. **Deliverable Quality Assurance** — Automated QA against firm standards
4. **Knowledge Discovery** — Find relevant past work, frameworks, and expertise

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14, React 19, Shadcn/ui, Tailwind CSS, Zustand |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.x, aiosqlite |
| **AI** | Azure OpenAI GPT-5.x, Microsoft Agent Framework |
| **Database** | SQLite with async support |
| **Real-time** | WebSocket for agent status streaming |

---

## Project Structure

```
federation/
├── docs/
│   ├── API.md              # Complete API documentation
│   ├── PRD.md              # Product Requirements Document
│   ├── TRD.md              # Technical Requirements Document
│   └── DEMO_PLAN.md        # Demo scenarios and walkthrough
├── frontend/               # Next.js application
│   ├── src/
│   │   ├── app/            # App router pages
│   │   ├── components/     # React components
│   │   └── lib/            # API client, store, utilities
│   └── package.json
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── agents/         # 7 AI agents
│   │   ├── api/            # REST endpoints + WebSocket
│   │   ├── models/         # Database models & schemas
│   │   ├── services/       # LLM, documents, knowledge
│   │   └── data/           # Seed data
│   ├── tests/              # Pytest test suite
│   └── requirements.txt
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (with pnpm recommended)
- Azure OpenAI API access

### Environment Setup

Create a `.env` file in the project root:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/federation.db
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Seed the database with sample data
python -c "from app.data.seed import seed_database; import asyncio; asyncio.run(seed_database())"

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
pnpm install  # or npm install
pnpm dev      # or npm run dev
```

Open http://localhost:3000 to access the application.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/conversations` | GET/POST | List or create conversations |
| `/api/chat/conversations/{id}/messages` | GET/POST | Get or send messages |
| `/api/proposals` | GET | List all proposals |
| `/api/proposals/generate` | POST | Generate new proposal |
| `/api/research/query` | POST | Execute research query |
| `/api/research/briefing` | POST | Generate client briefing |
| `/api/knowledge/search` | POST | Semantic search knowledge base |
| `/api/documents/{id}/export` | POST | Export document (PDF, DOCX, etc.) |
| `/api/analytics/metrics` | GET | Performance metrics |
| `/ws/agents/{conversation_id}` | WS | Real-time agent updates |

Full API documentation: [docs/API.md](docs/API.md) or visit `/docs` when running.

---

## Testing

```bash
cd backend
pytest                      # Run all tests
pytest -v                   # Verbose output
pytest tests/test_chat.py   # Run specific test file
```

---

## Pages & Features

| Page | Route | Features |
|------|-------|----------|
| **Chat** | `/` | Multi-agent conversation, real-time status panel |
| **Proposals** | `/proposals` | Generate & export client proposals |
| **Research** | `/research` | Ad-hoc research queries, client briefings |
| **Knowledge** | `/knowledge` | Semantic search, browse knowledge base |
| **Analytics** | `/analytics` | Agent metrics, execution traces |

---

## Documentation

- [API Reference](docs/API.md) — Complete REST & WebSocket API documentation
- [Product Requirements](docs/PRD.md) — Business context, user stories, success criteria
- [Technical Requirements](docs/TRD.md) — Architecture, implementation details
- [Demo Plan](docs/DEMO_PLAN.md) — Demo scenarios and walkthrough guide

---

## Key Value Propositions

| Metric | Projected Impact |
|--------|------------------|
| **Proposal Win Rate** | +15-20% (faster response, better quality) |
| **Senior Time Recapture** | 20-30% reduction in research/drafting |
| **Knowledge Reuse** | 3x improvement in finding past work |
| **Revenue per Consultant** | 25-40% increase |

---

## Development

### Code Conventions

- **Backend**: Async everywhere, use `AgentContext` for agent communication
- **Frontend**: Compound components, Zustand for state, Shadcn/ui patterns
- **Testing**: Pytest for backend, comprehensive API coverage

### Adding a New Agent

1. Create `backend/app/agents/{name}.py` inheriting from base
2. Define `name`, `description`, `capabilities`
3. Implement `async def process(self, ctx, message)`
4. Register in `backend/app/agents/factory.py`

---

## License

Internal Demo — Not for Distribution
