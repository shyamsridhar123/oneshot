# Federation - AI Coding Agent Instructions

## Project Overview

**Federation** is a multi-agent AI platform for professional services, demonstrating coordinated AI agents that mirror a consulting firm's operating model.

### Architecture (Dual-Stack)

```
Frontend (Next.js 14)         Backend (Python FastAPI)
     ↓                              ↓
Shadcn/ui + Tailwind          Microsoft Agent Framework
Vercel Agent Skills           7 Specialized Agents
Zustand state                 Azure OpenAI GPT-5.x
     ↓                              ↓
     └──── REST API / WebSocket ────┘
                  ↓
            SQLite (aiosqlite)
```

### Agent Roles
| Agent | Purpose | Key File |
|-------|---------|----------|
| **Orchestrator** | Task decomposition, coordination | `backend/app/agents/orchestrator.py` |
| **Strategist** | Proposals, engagement scoping | `backend/app/agents/strategist.py` |
| **Researcher** | Web search, news, company intel | `backend/app/agents/researcher.py` |
| **Analyst** | Data viz, financial modeling | `backend/app/agents/analyst.py` |
| **Scribe** | Document generation, branding | `backend/app/agents/scribe.py` |
| **Advisor** | Client comms, exec summaries | `backend/app/agents/advisor.py` |
| **Memory** | Knowledge retrieval, RAG | `backend/app/agents/memory.py` |

## Developer Workflows

### Running Locally
```bash
# Backend (Terminal 1)
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend && npm install && npm run dev
```

### Environment Setup
Copy `.env.example` to `.env` and configure:
- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_OPENAI_DEPLOYMENT`
- `DATABASE_URL=sqlite+aiosqlite:///./data/federation.db`

### Docker Alternative
```bash
cp .env.example .env && docker-compose up
```

## Code Conventions

### Backend (Python)
- **Agent pattern**: Inherit from `Agent` base class in `backend/app/agents/base.py`
- **Async everywhere**: Use `async/await` for all I/O operations (FastAPI, aiosqlite, Azure OpenAI)
- **Structured outputs**: Use `llm_service.structured_output()` for reliable JSON from GPT
- **Agent communication**: Use `AgentContext` for passing state between agents, not direct calls

### Frontend (React/Next.js)
- **Compound components**: Follow patterns in `.github/skills/vercel-composition-patterns/AGENTS.md`
- **State**: Zustand for global state, lift component state into Providers
- **React 19**: Use `use()` instead of `useContext()`, ref as regular prop (no `forwardRef`)
- **Components**: Shadcn/ui in `frontend/components/ui/`, compose explicit variants (no boolean prop sprawl)
- **Agent Skills**: Integrate via `@vercel-labs/agent-skills` in `frontend/lib/agentSkills.ts`

### Database
- SQLite with SQLAlchemy 2.x + aiosqlite for async access
- Models in `backend/app/models/database.py`
- Key tables: `conversations`, `messages`, `agent_traces`, `documents`, `knowledge_items`, `engagements`

## Key Patterns

### Adding a New Agent
1. Create `backend/app/agents/{name}.py` inheriting from `Agent`
2. Define `name`, `description`, `capabilities` 
3. Implement `async def process(self, ctx: AgentContext, message: Message)`
4. Register in agent registry used by Orchestrator
5. Add prompts to `backend/app/agents/prompts.py`

### Real-time Agent Updates
WebSocket at `/ws/agents/{conversation_id}` streams events:
- `agent.started`, `agent.thinking`, `agent.completed`, `agent.handoff`
- `stream.token` for streaming LLM responses
- `document.generated` when Scribe produces output

### Knowledge/RAG Flow
1. User query → Orchestrator dispatches to Memory Agent
2. Memory Agent embeds query via `llm_service.embed()`
3. Semantic search over `knowledge_items` table
4. Results passed via `AgentContext` to other agents

## Important Files

| Path | Purpose |
|------|---------|
| `docs/PRD.md` | Product requirements, demo scenarios |
| `docs/TRD.md` | Full technical architecture, API specs |
| `backend/app/main.py` | FastAPI entry point |
| `backend/app/services/llm_service.py` | Azure OpenAI wrapper |
| `frontend/app/page.tsx` | Main chat page |
| `frontend/lib/store.ts` | Zustand state management |
| `frontend/lib/websocket.ts` | WebSocket handler for agent updates |

## Testing

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

Demo validation: proposals < 5 min, research accuracy > 95%, real-time agent status streaming.

## What NOT to Do

- Don't add boolean props to components (use composition/variants)
- Don't call agents directly—go through Orchestrator
- Don't use sync database calls (always `async` with aiosqlite)
- Don't hardcode API keys (use `.env`)
- Don't create production security features (this is a demo/POC)
