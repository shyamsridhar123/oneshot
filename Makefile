# OneShot - Social Media Command Center
# Run 'make setup' for first-time installation

.PHONY: setup setup-backend setup-frontend db-init db-seed db-reset db-status \
        run run-backend run-frontend test test-backend clean help

BACKEND_DIR := backend
FRONTEND_DIR := frontend
VENV := $(BACKEND_DIR)/.venv
# Use absolute path for python so it works from any CWD in sub-shells
PYTHON := $(CURDIR)/$(VENV)/bin/python
PIP := $(CURDIR)/$(VENV)/bin/pip

# ============ First-Time Setup ============

setup: check-env setup-backend setup-frontend db-init ## Full first-time setup (backend + frontend + database)
	@echo ""
	@echo "✅ Setup complete! Run 'make run' to start the app."

check-env:
	@if [ ! -f .env ]; then \
		echo ""; \
		echo "⚠️  No .env file found. Creating from .env.example..."; \
		cp .env.example .env; \
		echo "✅ Created .env — edit it with your Azure OpenAI settings before running."; \
		echo "   See SETUP.md for details."; \
		echo ""; \
	fi

setup-backend: $(VENV)/bin/activate ## Install backend dependencies
	@echo "Installing backend dependencies..."
	@$(PIP) install -r $(BACKEND_DIR)/requirements.txt -q
	@echo "✅ Backend dependencies installed"

$(VENV)/bin/activate:
	@echo "Creating Python virtual environment..."
	@python3 -m venv $(VENV)
	@echo "✅ Virtual environment created at $(VENV)"

setup-frontend: ## Install frontend dependencies
	@echo "Installing frontend dependencies..."
	@cd $(FRONTEND_DIR) && pnpm install --silent 2>/dev/null || npm install --silent
	@echo "✅ Frontend dependencies installed"

# ============ Database ============

db-init: ## Initialize database schema and seed with sample data
	@cd $(BACKEND_DIR) && APP_DEBUG=false $(PYTHON) setup_db.py init --seed --no-embeddings -y

db-seed: ## Seed database with sample data (with embeddings if Azure configured)
	@cd $(BACKEND_DIR) && APP_DEBUG=false $(PYTHON) setup_db.py seed

db-reset: ## Reset database and reseed (destructive)
	@cd $(BACKEND_DIR) && APP_DEBUG=false $(PYTHON) setup_db.py reset --seed --no-embeddings -y

db-status: ## Show database statistics
	@cd $(BACKEND_DIR) && APP_DEBUG=false $(PYTHON) setup_db.py status

# ============ Run ============

run: ## Start both backend and frontend (use two terminals instead for logs)
	@echo "Start in separate terminals:"
	@echo "  Terminal 1: make run-backend"
	@echo "  Terminal 2: make run-frontend"

run-backend: ## Start backend server (port 8000)
	@cd $(BACKEND_DIR) && $(PYTHON) -m uvicorn app.main:app --reload --port 8000

run-frontend: ## Start frontend dev server (port 3000)
	@cd $(FRONTEND_DIR) && pnpm dev 2>/dev/null || npm run dev

# ============ Test ============

test: test-backend ## Run all tests

test-backend: ## Run backend test suite
	@cd $(BACKEND_DIR) && PYTHONPATH=. $(PYTHON) -m pytest tests/ -v

# ============ Clean ============

clean: ## Remove generated files (venv, node_modules, db)
	@echo "This will remove .venv, node_modules, and database files."
	@echo "Run 'make clean-confirm' to proceed."

clean-confirm:
	rm -rf $(VENV)
	rm -rf $(FRONTEND_DIR)/node_modules
	rm -f $(BACKEND_DIR)/data/oneshot.db
	rm -f $(BACKEND_DIR)/data/test_oneshot.db
	@echo "✅ Cleaned"

# ============ Help ============

help: ## Show this help
	@echo "OneShot - Social Media Command Center"
	@echo ""
	@echo "Quick Start:"
	@echo "  make setup        Full first-time setup"
	@echo "  make run-backend  Start backend (terminal 1)"
	@echo "  make run-frontend Start frontend (terminal 2)"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
