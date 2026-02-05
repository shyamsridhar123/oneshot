# Federation

## AI-Powered Professional Services Engagement Platform

> **⚠️ POC / Art of the Possible** — This is a proof-of-concept demonstrating what's possible with multi-agent AI systems. Not production-ready. Built for demos and exploration.

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
│   │   └── data/           # Seed data definitions
│   ├── setup_db.py         # Database setup & seeding CLI
│   ├── demo_setup.py       # Demo preparation script
│   ├── tests/              # Pytest test suite
│   └── requirements.txt
├── scripts/
│   └── setup_database.sh   # Shell wrapper for DB setup
├── demo.sh                 # Main demo management script
├── .env.example            # Sample environment configuration
└── README.md
```

---

## Quick Start

### Prerequisites

- Linux, macOS, or WSL (Windows users should use WSL)
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Node.js 18+ with pnpm
- Azure OpenAI API access

### Environment Setup

Copy the example environment file and configure your Azure OpenAI credentials:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Azure OpenAI Configuration (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Model Deployments
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.2-chat           # Primary chat model
AZURE_OPENAI_GPT5_DEPLOYMENT_NAME=gpt-5.1           # Secondary model
AZURE_OPENAI_CODEX_DEPLOYMENT_NAME=gpt-5.1-codex-max # Code tasks
AZURE_OPENAI_TEXTEMBEDDING_DEPLOYMENT_NAME=text-embedding-3-small  # Embeddings for RAG

# Database (SQLite with async support)
DATABASE_URL=sqlite+aiosqlite:///./data/federation.db
```

See [.env.example](.env.example) for all available configuration options.

### Backend Setup

#### Option 1: Using uv (Recommended)

[uv](https://docs.astral.sh/uv/) is an extremely fast Python package installer and resolver.

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or on macOS: brew install uv

cd backend

# Create virtual environment and install dependencies (one command)
uv venv && source .venv/bin/activate && uv pip install -r requirements.txt

# Initialize database and seed with sample data
python setup_db.py init --seed

# Start the server
uvicorn app.main:app --reload --port 8000
```

#### Option 2: Using pip (Traditional)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Initialize database and seed with sample data
python setup_db.py init --seed

# Start the server
uvicorn app.main:app --reload --port 8000
```

> **Note**: Developed and tested on Linux/WSL. macOS works the same. Native Windows users should use WSL for best results.

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

## Database Management

Federation includes comprehensive database management scripts:

```bash
# Using the Python CLI directly
cd backend
python setup_db.py init              # Create database and tables
python setup_db.py seed              # Populate with sample data
python setup_db.py init --seed       # Initialize and seed in one step
python setup_db.py reset --seed -y   # Reset and reseed (destructive)
python setup_db.py status            # Show database statistics
python setup_db.py clear             # Clear all data (keep tables)

# Using demo.sh wrapper
./demo.sh db:init                    # Create database  
./demo.sh db:seed                    # Seed sample data
./demo.sh db:status                  # Show statistics
./demo.sh db:reset                   # Reset database
./demo.sh db:clear                   # Clear all data

# Quick seeding without embeddings (faster, works offline)
python setup_db.py seed --no-embeddings
```

Sample data includes:
- **8 past engagements** — Digital transformation, M&A, growth strategy examples
- **10 consulting frameworks** — PMI Playbook, Cloud Migration, AI/ML Implementation, etc.
- **5 expertise areas** — Healthcare, Financial Services, Supply Chain, M&A

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

## What This Demo Shows

| Capability | Demo Scenario |
|------------|---------------|
| **Multi-Agent Coordination** | Orchestrator dispatches tasks to specialist agents |
| **Rapid Content Generation** | Proposals generated in minutes vs. weeks |
| **Knowledge Retrieval** | Semantic search over past engagements |
| **Real-time Visibility** | Watch agents work via WebSocket streaming |

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

MIT License - see [LICENSE](LICENSE) for details.
