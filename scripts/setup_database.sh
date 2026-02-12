#!/bin/bash
#
# OneShot Database Setup Script
#
# Usage:
#   ./scripts/setup_database.sh init             # Initialize database
#   ./scripts/setup_database.sh seed             # Seed with sample data
#   ./scripts/setup_database.sh init --seed      # Initialize and seed
#   ./scripts/setup_database.sh reset            # Reset database (destructive)
#   ./scripts/setup_database.sh reset --seed     # Reset and reseed
#   ./scripts/setup_database.sh clear            # Clear all data
#   ./scripts/setup_database.sh status           # Show database status
#   ./scripts/setup_database.sh migrate          # Run migrations
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
}

print_status() {
    local status=$1
    local message=$2
    case $status in
        success) echo -e "  ${GREEN}✅ $message${NC}" ;;
        error)   echo -e "  ${RED}❌ $message${NC}" ;;
        warning) echo -e "  ${YELLOW}⚠️  $message${NC}" ;;
        info)    echo -e "  ${BLUE}ℹ️  $message${NC}" ;;
        pending) echo -e "  ⏳ $message" ;;
    esac
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_status error "Python 3 not found. Please install Python 3.10 or later."
        exit 1
    fi
}

setup_venv() {
    cd "$BACKEND_DIR"
    
    if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
        print_status pending "Creating Python virtual environment..."
        python3 -m venv .venv
        print_status success "Virtual environment created"
    fi
    
    # Activate venv (try .venv first, then venv)
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Check if dependencies are installed
    if ! python3 -c "import sqlalchemy" 2>/dev/null; then
        print_status pending "Installing dependencies..."
        pip install -r requirements.txt -q
        print_status success "Dependencies installed"
    fi
}

run_setup_db() {
    setup_venv
    cd "$BACKEND_DIR"
    python3 setup_db.py "$@"
}

show_help() {
    cat << 'EOF'

OneShot Database Setup Script
================================

This script manages the OneShot database including initialization,
seeding with sample data, and maintenance operations.

Usage: ./scripts/setup_database.sh <command> [options]

Commands:
  init        Create database and tables
  seed        Populate with sample data (engagements, frameworks)
  reset       Drop all tables and recreate (DESTRUCTIVE)
  clear       Delete all data but keep schema
  status      Show database statistics
  migrate     Apply schema updates

Options:
  --seed              Also seed after init/reset
  --no-embeddings     Skip embeddings generation (faster seeding)
  -y, --yes           Skip confirmation prompts
  -q, --quiet         Minimal output

Examples:
  # Fresh setup with sample data
  ./scripts/setup_database.sh init --seed

  # Reset everything and start fresh
  ./scripts/setup_database.sh reset --seed -y

  # Quick seed without embeddings (offline/faster)
  ./scripts/setup_database.sh seed --no-embeddings

  # Check current state
  ./scripts/setup_database.sh status

Environment:
  DATABASE_URL         SQLAlchemy connection string
                       Default: sqlite+aiosqlite:///./data/oneshot.db
  
  AZURE_OPENAI_*       Required for generating embeddings during seeding

Requirements:
  - Python 3.10+
  - Dependencies from backend/requirements.txt

EOF
}

# Ensure we're in the right place
if [ ! -f "$BACKEND_DIR/setup_db.py" ]; then
    print_status error "Cannot find setup_db.py in $BACKEND_DIR"
    print_status info "Make sure you're running from the project root"
    exit 1
fi

# Main command handler
case "${1:-}" in
    init|seed|reset|clear|status|migrate)
        check_python
        print_header "Database ${1^}"
        run_setup_db "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
