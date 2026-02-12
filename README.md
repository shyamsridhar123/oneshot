# Social Media Command Center

## Multi-Agent AI Platform for Social Media Content Creation

A multi-agent AI system that coordinates 7 specialized agents — each with distinct reasoning patterns — to create brand-aligned social media content for LinkedIn, Twitter/X, and Instagram. Built on Microsoft Agent Framework and Azure OpenAI with DefaultAzureCredential.

![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript)
![Azure OpenAI](https://img.shields.io/badge/Azure_OpenAI-GPT--5.x-0078D4?logo=microsoft-azure)

---

## What It Does

**Social Media Command Center** takes a content request (e.g., "Write a LinkedIn post about our AI launch") and orchestrates 7 AI agents in two parallel waves to produce platform-specific, brand-compliant social media content — complete with trend research, engagement benchmarks, and compliance scoring.

### Architecture

```
+----------------------------------------------------------------------+
|                               FRONTEND                               |
|                    Next.js 14 · Shadcn/ui · Tailwind                 |
|                        Zustand State Management                      |
+----------------------------------+-----------------------------------+
                                   |
                          REST API / WebSocket
                                   |
+----------------------------------v-----------------------------------+
|                               BACKEND                                |
|                         FastAPI · Python 3.11                        |
|                                                                      |
|                      +--------------------+                          |
|                      |    ORCHESTRATOR    |                          |
|                      | Intent: content_   |                          |
|                      |   creation,        |                          |
|                      |   strategy,        |                          |
|                      |   review, trends   |                          |
|                      +---------+----------+                          |
|                                |                                     |
|              Two-wave parallel dispatch                               |
|                                |                                     |
|  Wave 1: Context Gathering (parallel)                                |
|  +----------+----------+---------+---------+                         |
|  |Researcher|Strategist| Memory  | Analyst |                         |
|  |  (ReAct) |  (CoT)   |  (RAG)  | (Data)  |                         |
|  | trends & | audience | brand   | engage- |                         |
|  | hashtags | planning | context | ment    |                         |
|  +----+-----+----+-----+---+-----+---+-----+                         |
|       |          |         |         |                               |
|       +----------+---------+---------+                               |
|                       |                                              |
|  Wave 2: Create + Review (parallel, with Wave 1 context)            |
|  +-------------------+-------------------+                           |
|  |      Scribe       |     Advisor       |                           |
|  |  (Template-guided)|  (Self-Reflection)|                           |
|  | platform-specific | brand compliance  |                           |
|  | content writing   | scoring (1-10)    |                           |
|  +-------------------+-------------------+                           |
|                       |                                              |
|              +--------v--------+                                     |
|              |    SERVICES     |                                     |
|              | LLM (Azure GPT) |                                     |
|              | Knowledge (RAG)  |                                     |
|              | Documents        |                                     |
|              | Traces           |                                     |
|              +--------+--------+                                     |
|                       |                                              |
|              +--------v--------+                                     |
|              |   DATA LAYER    |                                     |
|              | SQLite+aiosqlite|                                     |
|              +-----------------+                                     |
+----------------------------------------------------------------------+
```

---

## Reasoning Patterns

Each agent uses an explicit reasoning pattern, demonstrating advanced prompt engineering:

| Agent | Reasoning Pattern | Description |
|-------|-------------------|-------------|
| **Orchestrator** | Step-by-Step Decomposition | Classifies intent, determines platforms, dispatches two-wave parallel execution |
| **Strategist** | Chain-of-Thought (CoT) | Walks through audience → message → tone → calendar → CTA for each platform |
| **Researcher** | ReAct (Reasoning + Acting) | Loops through Thought → Action → Observation to discover and validate trends |
| **Analyst** | Data-Driven Benchmarking | Provides engagement benchmarks, optimal timing, and performance predictions |
| **Scribe** | Template-Guided Generation | Follows platform-specific templates (hook → body → CTA → hashtags) |
| **Advisor** | Self-Reflection | Initial review → metacognitive reflection → revised compliance score (1-10) |
| **Memory** | Retrieval-Augmented Grounding | Grounds content in brand guidelines, past post performance, and content calendars |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14, React 19, Shadcn/ui, Tailwind CSS, Zustand |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.x, aiosqlite |
| **AI** | Azure OpenAI GPT-5.x, Microsoft Agent Framework |
| **Auth** | Azure Identity (DefaultAzureCredential) |
| **Database** | SQLite with async support |
| **Real-time** | WebSocket for agent status streaming |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (with pnpm recommended)
- Azure OpenAI resource with deployed models
- Azure CLI logged in (`az login`) for DefaultAzureCredential

### Environment Setup

```bash
cp .env.example .env
```

Edit `.env` with your Azure OpenAI endpoint:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.2-chat
```

> **Note:** API key is optional. The app uses `DefaultAzureCredential` by default — just run `az login` first.

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Initialize database
python setup_db.py

# Seed with sample data (engagements + frameworks)
python -c "from app.data.seed import seed_database; import asyncio; asyncio.run(seed_database())"

# Seed with social media brand data (brand guidelines + past posts + content calendar)
python -c "from app.data.seed import seed_social_media_data; import asyncio; asyncio.run(seed_social_media_data())"

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

## Demo Scenarios

1. **Content Creation** — "Write a LinkedIn post about our AI Collaboration Suite launch"
2. **Multi-Platform Campaign** — "Create content for all platforms about our healthcare deployment"
3. **Trend Research** — "What AI topics are trending on social media this week?"
4. **Content Review** — "Review this draft tweet for brand alignment"

---

## Pages & Features

| Page | Route | Features |
|------|-------|----------|
| **Chat** | `/chat` | Multi-agent conversation, real-time agent status panel |
| **Content** | `/proposals` | Generated social media content library |
| **Trends** | `/research` | Trend research and competitor analysis |
| **Brand** | `/knowledge` | Brand guidelines, past post performance, content calendar |
| **Analytics** | `/analytics` | Agent metrics, execution traces, token usage |

---

## Project Structure

```
social-media-command-center/
├── frontend/                  # Next.js application
│   └── src/
│       ├── app/               # App router pages
│       ├── components/        # React components (landing, chat, sidebar)
│       └── lib/               # API client, store, utilities
├── backend/                   # FastAPI application
│   ├── app/
│   │   ├── agents/            # 7 AI agents with reasoning patterns
│   │   │   ├── orchestrator.py  # Two-wave parallel dispatch
│   │   │   ├── prompts.py       # All agent prompts with patterns
│   │   │   └── factory.py       # MAF agent factory + tools
│   │   ├── api/               # REST endpoints + WebSocket
│   │   ├── models/            # Database models & schemas
│   │   ├── services/          # LLM, documents, knowledge, traces
│   │   └── data/              # Seed data
│   ├── data/                  # Brand data files
│   │   ├── brand_guidelines.md
│   │   ├── past_posts.json
│   │   └── content_calendar.json
│   └── requirements.txt
├── .env.example
└── README.md
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
