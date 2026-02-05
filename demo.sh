#!/bin/bash
#
# Federation Demo Setup Script
#
# Usage:
#   ./demo.sh start      - Start backend and frontend servers
#   ./demo.sh stop       - Stop all servers
#   ./demo.sh status     - Check demo environment status
#   ./demo.sh cleanup    - Clear conversation history
#   ./demo.sh seed       - Seed knowledge base
#   ./demo.sh test       - Run all tests
#   ./demo.sh full       - Full demo prep (start + cleanup + seed + test)
#   ./demo.sh reset      - Full reset and fresh start
#
# Database commands:
#   ./demo.sh db:init    - Initialize database (create tables)
#   ./demo.sh db:seed    - Seed database with sample data  
#   ./demo.sh db:reset   - Reset database (drop and recreate)
#   ./demo.sh db:clear   - Clear all data (keep tables)
#   ./demo.sh db:status  - Show database status
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

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

check_requirements() {
    local missing=0
    
    if ! command -v python3 &> /dev/null; then
        print_status error "Python 3 not found"
        missing=1
    fi
    
    if ! command -v pnpm &> /dev/null; then
        print_status error "pnpm not found"
        missing=1
    fi
    
    if ! command -v curl &> /dev/null; then
        print_status error "curl not found"
        missing=1
    fi
    
    if [ $missing -eq 1 ]; then
        exit 1
    fi
}

is_backend_running() {
    curl -s http://localhost:8000/health > /dev/null 2>&1
}

is_frontend_running() {
    curl -s http://localhost:3000 > /dev/null 2>&1
}

start_backend() {
    print_status pending "Starting backend server..."
    
    cd "$BACKEND_DIR"
    
    # Activate venv if exists, or create it
    if [ ! -d "venv" ]; then
        print_status info "Creating Python virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt -q
    else
        source venv/bin/activate
    fi
    
    # Start in background
    nohup uvicorn app.main:app --reload --port 8000 > /tmp/federation-backend.log 2>&1 &
    echo $! > /tmp/federation-backend.pid
    
    # Wait for startup
    for i in {1..30}; do
        if is_backend_running; then
            print_status success "Backend started on http://localhost:8000"
            return 0
        fi
        sleep 1
    done
    
    print_status error "Backend failed to start. Check /tmp/federation-backend.log"
    return 1
}

start_frontend() {
    print_status pending "Starting frontend server..."
    
    cd "$FRONTEND_DIR"
    
    # Install deps if needed
    if [ ! -d "node_modules" ]; then
        print_status info "Installing frontend dependencies..."
        pnpm install --silent
    fi
    
    # Start in background
    nohup pnpm dev > /tmp/federation-frontend.log 2>&1 &
    echo $! > /tmp/federation-frontend.pid
    
    # Wait for startup
    for i in {1..60}; do
        if is_frontend_running; then
            print_status success "Frontend started on http://localhost:3000"
            return 0
        fi
        sleep 1
    done
    
    print_status error "Frontend failed to start. Check /tmp/federation-frontend.log"
    return 1
}

stop_servers() {
    print_header "Stopping Servers"
    
    # Stop backend
    if [ -f /tmp/federation-backend.pid ]; then
        PID=$(cat /tmp/federation-backend.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID 2>/dev/null || true
            print_status success "Backend stopped"
        fi
        rm -f /tmp/federation-backend.pid
    fi
    
    # Kill any remaining uvicorn
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    
    # Stop frontend
    if [ -f /tmp/federation-frontend.pid ]; then
        PID=$(cat /tmp/federation-frontend.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID 2>/dev/null || true
            print_status success "Frontend stopped"
        fi
        rm -f /tmp/federation-frontend.pid
    fi
    
    # Kill any remaining next dev
    pkill -f "next dev" 2>/dev/null || true
    
    print_status info "All servers stopped"
}

start_servers() {
    print_header "Starting Demo Environment"
    
    check_requirements
    
    # Check if already running
    if is_backend_running; then
        print_status info "Backend already running"
    else
        start_backend
    fi
    
    if is_frontend_running; then
        print_status info "Frontend already running"
    else
        start_frontend
    fi
    
    echo ""
    print_status success "Demo environment started!"
    print_status info "Open: http://localhost:3000"
}

run_demo_setup() {
    local command=$1
    
    cd "$BACKEND_DIR"
    
    if [ ! -d "venv" ]; then
        print_status error "Virtual environment not found. Run './demo.sh start' first."
        exit 1
    fi
    
    source venv/bin/activate
    python demo_setup.py $command
}

show_status() {
    print_header "Demo Environment Status"
    
    echo ""
    echo "  Servers:"
    if is_backend_running; then
        print_status success "Backend: http://localhost:8000"
    else
        print_status error "Backend: Not running"
    fi
    
    if is_frontend_running; then
        print_status success "Frontend: http://localhost:3000"
    else
        print_status error "Frontend: Not running"
    fi
    
    # Check .env
    if [ -f "$SCRIPT_DIR/.env" ]; then
        if grep -q "AZURE_OPENAI_API_KEY" "$SCRIPT_DIR/.env"; then
            print_status success ".env file configured"
        else
            print_status warning ".env file may be incomplete"
        fi
    else
        print_status error ".env file not found"
    fi
    
    # Run full status check if backend is up
    if is_backend_running; then
        echo ""
        run_demo_setup status
    fi
}

full_prep() {
    print_header "Full Demo Preparation"
    
    # Start servers if needed
    start_servers
    
    # Run full demo prep
    if is_backend_running; then
        run_demo_setup full
    else
        print_status error "Backend not running - cannot complete setup"
        exit 1
    fi
}

reset_demo() {
    print_header "Full Demo Reset"
    
    print_status pending "Stopping existing servers..."
    stop_servers
    
    print_status pending "Removing database..."
    rm -f "$BACKEND_DIR/data/federation.db"
    
    print_status pending "Starting fresh environment..."
    start_servers
    
    print_status pending "Seeding database..."
    sleep 3  # Wait for backend to fully start
    run_demo_setup seed
    
    print_status pending "Running tests..."
    run_demo_setup test
    
    echo ""
    print_status success "Demo environment reset complete!"
    print_status info "Open: http://localhost:3000"
}

show_help() {
    echo ""
    echo "Federation Demo Script"
    echo ""
    echo "Usage: ./demo.sh <command>"
    echo ""
    echo "Commands:"
    echo "  start     Start backend and frontend servers"
    echo "  stop      Stop all servers"
    echo "  status    Check demo environment status"
    echo "  cleanup   Clear all conversation history"
    echo "  seed      Seed knowledge base with sample data"
    echo "  test      Run all connectivity tests"
    echo "  full      Full demo prep (start + cleanup + seed + test)"
    echo "  reset     Complete reset (delete DB, restart, reseed)"
    echo "  help      Show this help message"
    echo ""
    echo "Database Commands:"
    echo "  db:init   Initialize database (create tables only)"
    echo "  db:seed   Seed database with sample data"
    echo "  db:reset  Reset database (drop and recreate tables)"
    echo "  db:clear  Clear all data (keep tables)"  
    echo "  db:status Show database statistics"
    echo ""
    echo "Quick Start:"
    echo "  ./demo.sh full"
    echo ""
    echo "Before Demo:"
    echo "  1. Ensure .env file is configured with Azure OpenAI credentials"
    echo "  2. Run: ./demo.sh full"
    echo "  3. Open: http://localhost:3000"
    echo "  4. Verify agent status panel shows 'Connected'"
    echo ""
}

# Database operations using setup_db.py
run_db_command() {
    local command=$1
    shift
    
    cd "$BACKEND_DIR"
    
    # Activate venv (try .venv first, then venv)
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    else
        print_status error "Virtual environment not found. Run './demo.sh start' first."
        exit 1
    fi
    
    python setup_db.py $command "$@"
}

# Main command handler
case "${1:-}" in
    start)
        start_servers
        ;;
    stop)
        stop_servers
        ;;
    status)
        show_status
        ;;
    cleanup)
        run_demo_setup cleanup
        ;;
    seed)
        run_demo_setup seed
        ;;
    test)
        run_demo_setup test
        ;;
    full)
        full_prep
        ;;
    reset)
        reset_demo
        ;;
    db:init)
        shift
        run_db_command init "$@"
        ;;
    db:seed)
        shift
        run_db_command seed "$@"
        ;;
    db:reset)
        shift
        run_db_command reset "$@"
        ;;
    db:clear)
        shift
        run_db_command clear "$@"
        ;;
    db:status)
        run_db_command status
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
