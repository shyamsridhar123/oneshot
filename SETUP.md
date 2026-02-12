# Setup & Run Guide

Step-by-step instructions to get the OneShot running locally.

---

## Prerequisites

| Requirement | Version | Check |
|------------|---------|-------|
| Python | 3.11+ | `python3 --version` |
| Node.js | 18+ | `node --version` |
| npm or pnpm | any | `npm --version` |
| Azure CLI | latest | `az --version` |
| Git | any | `git --version` |

**Optional** (for MCP tool integration):
- npx (bundled with npm) -- enables Filesystem MCP and Fetch MCP servers

---

## 1. Clone the Repository

```bash
git clone https://github.com/shyamsridhar123/oneshot.git social-media-command-center
cd social-media-command-center
```

---

## 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set your Azure OpenAI endpoint:

```env
# Required -- your Azure OpenAI resource URL
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com

# Required -- your deployed chat model name
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Required -- your deployed embedding model name
AZURE_OPENAI_TEXTEMBEDDING_DEPLOYMENT_NAME=text-embedding-3-small

# Optional -- API version (defaults to 2024-12-01-preview)
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### Authentication

The app uses **Azure Identity** (`DefaultAzureCredential`) -- no API key needed. Just log in:

```bash
az login
```

This works automatically with:
- `az login` for local development
- Managed Identity for Azure deployments
- Service principals for CI/CD

> **Fallback**: If you can't use `az login`, uncomment `AZURE_OPENAI_API_KEY` in `.env` and set your key.

---

## 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

### Initialize the Database

```bash
# Create tables and seed with sample data
python setup_db.py init --seed
```

This creates:
- `data/oneshot.db` -- SQLite database
- Sample engagements, frameworks, and expertise items
- Semantic embeddings for RAG search (requires Azure OpenAI)

> **Without Azure creds**: Use `python setup_db.py init --seed --no-embeddings` to skip embedding generation.

### Seed Social Media Brand Data

```bash
python -c "from app.data.seed import seed_social_media_data; import asyncio; asyncio.run(seed_social_media_data())"
```

This loads:
- `data/brand_guidelines.md` -- NotContosso brand voice and style rules
- `data/past_posts.json` -- Historical post performance data
- `data/content_calendar.json` -- Weekly content schedule template

### Start the Backend

```bash
uvicorn app.main:app --reload --port 8000
```

Verify it's running:

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

**API docs** are available at http://localhost:8000/docs (Swagger UI).

---

## 4. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
pnpm install        # or: npm install

# Start development server
pnpm dev            # or: npm run dev
```

Open http://localhost:3000 in your browser.

---

## 5. Verify Everything Works

### Run the Test Suite

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. .venv/bin/pytest tests/ -v
```

Expected result: **208 passed, 13 skipped** (skips are live-server integration tests).

### Run the E2E Demo

```bash
cd backend
PYTHONPATH=. python demo_e2e.py
```

Expected result: **85 checks, all passing**.

---

## Quick Reference

### Backend Commands

| Command | Description |
|---------|-------------|
| `uvicorn app.main:app --reload` | Start backend (dev mode) |
| `python setup_db.py init --seed` | Initialize DB with sample data |
| `python setup_db.py reset --seed` | Reset DB and reseed |
| `python setup_db.py status` | Show database statistics |
| `python setup_db.py clear` | Delete all data (keep tables) |
| `PYTHONPATH=. pytest tests/ -v` | Run test suite |
| `PYTHONPATH=. python demo_e2e.py` | Run E2E demo script |

### Frontend Commands

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start dev server (port 3000) |
| `pnpm build` | Production build |
| `pnpm start` | Start production server |
| `pnpm lint` | Run ESLint |

### Using demo.sh (Alternative)

The project includes a convenience script:

```bash
./demo.sh full      # Start backend + frontend, seed DB, run tests
./demo.sh start     # Start backend and frontend servers
./demo.sh stop      # Stop all servers
./demo.sh status    # Check if servers are running
./demo.sh reset     # Full reset (delete DB, restart, reseed)
./demo.sh seed      # Seed knowledge base
./demo.sh test      # Run connectivity tests
```

---

## API Endpoints

Once the backend is running, these endpoints are available:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |
| `/api/chat/conversations` | GET/POST | List/create conversations |
| `/api/chat/conversations/{id}/messages` | GET/POST | List/send messages (triggers agents) |
| `/api/proposals` | GET | List generated social content |
| `/api/proposals/generate` | POST | Generate content via agents |
| `/api/documents` | GET | List all documents |
| `/api/documents/{id}/export` | POST | Export to PDF/DOCX/HTML/Markdown |
| `/api/analytics/traces` | GET | Agent execution traces |
| `/api/analytics/metrics` | GET | Performance metrics |
| `/api/analytics/social` | GET | Social media analytics |
| `/api/knowledge/search` | POST | Search knowledge base |
| `/api/research/query` | POST | Research queries |
| `/ws/agents/{conversation_id}` | WebSocket | Real-time agent status streaming |

---

## Troubleshooting

### "DefaultAzureCredential failed to retrieve a token"

You need to authenticate with Azure:

```bash
az login
```

Or set `AZURE_OPENAI_API_KEY` in your `.env` file.

### "ModuleNotFoundError: No module named 'app'"

Make sure you're running from the `backend/` directory with `PYTHONPATH` set:

```bash
cd backend
PYTHONPATH=. python -m uvicorn app.main:app --reload
```

### "npx: command not found" (MCP tools unavailable)

MCP tools require Node.js. Install Node.js 18+ and verify:

```bash
npx --version
```

Agents will still work without MCP -- they fall back to direct LLM calls.

### Frontend can't connect to backend

Check that CORS is configured. The default `.env` allows `localhost:3000`:

```env
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Database errors after code changes

Reset the database:

```bash
cd backend
python setup_db.py reset --seed
```
