#!/usr/bin/env python3
"""
Federation Demo Test and Cleanup Script

This script prepares the demo environment by:
- Cleaning up existing conversation history
- Seeding the knowledge base with sample data
- Testing API endpoints
- Testing WebSocket connectivity
- Testing Azure OpenAI connectivity

Usage:
    python demo_setup.py cleanup     # Clear all conversations
    python demo_setup.py seed        # Seed knowledge base
    python demo_setup.py test        # Run all tests
    python demo_setup.py full        # Full demo prep (cleanup + seed + test)
    python demo_setup.py status      # Quick health check
"""

import asyncio
import sys
import json
import time
from datetime import datetime

import httpx
import websockets


# Configuration
BACKEND_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/agents/demo-test"
FRONTEND_URL = "http://localhost:3000"


def print_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_status(message: str, status: str = "info"):
    """Print a status message with appropriate formatting."""
    icons = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "pending": "⏳",
    }
    icon = icons.get(status, "•")
    print(f"  {icon} {message}")


async def check_backend_health() -> bool:
    """Check if the backend server is running."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print_status(f"Backend healthy - Version: {data.get('version', 'unknown')}", "success")
                return True
    except httpx.ConnectError:
        print_status("Backend not running at http://localhost:8000", "error")
    except Exception as e:
        print_status(f"Backend health check failed: {e}", "error")
    return False


async def check_frontend_health() -> bool:
    """Check if the frontend server is running."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(FRONTEND_URL, timeout=5.0)
            if response.status_code == 200:
                print_status("Frontend running at http://localhost:3000", "success")
                return True
    except httpx.ConnectError:
        print_status("Frontend not running at http://localhost:3000", "error")
    except Exception as e:
        print_status(f"Frontend health check failed: {e}", "error")
    return False


async def test_websocket_connection() -> bool:
    """Test WebSocket connectivity."""
    try:
        async with websockets.connect(WS_URL, ping_timeout=5) as ws:
            # Wait briefly for any initial message
            await asyncio.sleep(0.5)
            print_status("WebSocket connection successful", "success")
            return True
    except websockets.exceptions.InvalidStatusCode as e:
        print_status(f"WebSocket connection failed: {e}", "error")
    except ConnectionRefusedError:
        print_status("WebSocket connection refused - is backend running?", "error")
    except Exception as e:
        print_status(f"WebSocket test failed: {e}", "error")
    return False


async def test_azure_openai() -> bool:
    """Test Azure OpenAI connectivity by making a simple completion request."""
    print_status("Testing Azure OpenAI connectivity...", "pending")
    
    try:
        # Use the LLM service directly
        sys.path.insert(0, ".")
        from app.services.llm_service import get_llm_service
        
        llm = get_llm_service()
        
        # Simple test completion
        start = time.time()
        response = await llm.complete(
            prompt="Say 'Hello, Federation!' in exactly those words.",
            system_prompt="You are a helpful assistant. Respond only with the exact phrase requested.",
            max_tokens=50,
        )
        elapsed = time.time() - start
        
        print_status(f"Azure OpenAI responding ({elapsed:.2f}s)", "success")
        print_status(f"  Response: \"{response.strip()[:50]}...\"", "info")
        
        # Test embeddings
        start = time.time()
        embedding = await llm.embed("Test embedding for Federation demo")
        elapsed = time.time() - start
        print_status(f"Embeddings working ({len(embedding)} dimensions, {elapsed:.2f}s)", "success")
        
        return True
        
    except Exception as e:
        print_status(f"Azure OpenAI test failed: {e}", "error")
        print_status("  Check AZURE_OPENAI_* environment variables in .env", "warning")
        return False


async def list_conversations() -> list:
    """List all existing conversations."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/api/chat/conversations")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print_status(f"Failed to list conversations: {e}", "error")
    return []


async def cleanup_conversations():
    """Clear all conversation history from the database."""
    print_header("Cleaning Up Conversation History")
    
    if not await check_backend_health():
        print_status("Cannot cleanup - backend not running", "error")
        return False
    
    try:
        # Direct database cleanup
        sys.path.insert(0, ".")
        from app.models.database import AsyncSessionLocal, init_db, Conversation, Message
        from sqlalchemy import delete
        
        await init_db()
        
        async with AsyncSessionLocal() as db:
            # Count existing records
            from sqlalchemy import select, func
            msg_count = await db.execute(select(func.count(Message.id)))
            conv_count = await db.execute(select(func.count(Conversation.id)))
            
            msg_total = msg_count.scalar() or 0
            conv_total = conv_count.scalar() or 0
            
            print_status(f"Found {conv_total} conversations with {msg_total} messages", "info")
            
            if conv_total == 0:
                print_status("No conversations to clean up", "success")
                return True
            
            # Delete messages first (foreign key constraint)
            await db.execute(delete(Message))
            await db.execute(delete(Conversation))
            await db.commit()
            
            print_status(f"Deleted {conv_total} conversations and {msg_total} messages", "success")
        
        return True
        
    except Exception as e:
        print_status(f"Cleanup failed: {e}", "error")
        return False


async def count_knowledge_items():
    """Count existing knowledge items and engagements."""
    try:
        sys.path.insert(0, ".")
        from app.models.database import AsyncSessionLocal, init_db, KnowledgeItem, Engagement
        from sqlalchemy import select, func
        
        await init_db()
        
        async with AsyncSessionLocal() as db:
            knowledge_count = await db.execute(select(func.count(KnowledgeItem.id)))
            engagement_count = await db.execute(select(func.count(Engagement.id)))
            
            return {
                "knowledge_items": knowledge_count.scalar() or 0,
                "engagements": engagement_count.scalar() or 0,
            }
    except Exception as e:
        print_status(f"Failed to count knowledge items: {e}", "error")
        return {"knowledge_items": 0, "engagements": 0}


async def clear_knowledge_base():
    """Clear all knowledge items and engagements."""
    try:
        sys.path.insert(0, ".")
        from app.models.database import AsyncSessionLocal, init_db, KnowledgeItem, Engagement
        from sqlalchemy import delete
        
        await init_db()
        
        async with AsyncSessionLocal() as db:
            await db.execute(delete(KnowledgeItem))
            await db.execute(delete(Engagement))
            await db.commit()
            print_status("Cleared existing knowledge base", "success")
            return True
    except Exception as e:
        print_status(f"Failed to clear knowledge base: {e}", "error")
        return False


async def seed_knowledge_base():
    """Seed the knowledge base with sample data."""
    print_header("Seeding Knowledge Base")
    
    # Check current state
    counts = await count_knowledge_items()
    
    if counts["knowledge_items"] > 0 or counts["engagements"] > 0:
        print_status(
            f"Existing data: {counts['knowledge_items']} items, {counts['engagements']} engagements",
            "warning"
        )
        print_status("Clearing existing data before re-seeding...", "pending")
        await clear_knowledge_base()
    
    print_status("Running seed script (this may take a minute)...", "pending")
    
    try:
        sys.path.insert(0, ".")
        from app.data.seed import seed_database
        
        await seed_database()
        
        # Verify
        counts = await count_knowledge_items()
        print_status(
            f"Seeded: {counts['knowledge_items']} knowledge items, {counts['engagements']} engagements",
            "success"
        )
        return True
        
    except Exception as e:
        print_status(f"Seeding failed: {e}", "error")
        return False


async def test_api_endpoints():
    """Test key API endpoints."""
    print_header("Testing API Endpoints")
    
    if not await check_backend_health():
        return False
    
    tests_passed = 0
    tests_total = 0
    
    async with httpx.AsyncClient() as client:
        # Test 1: List conversations
        tests_total += 1
        try:
            response = await client.get(f"{BACKEND_URL}/api/chat/conversations")
            if response.status_code == 200:
                print_status("GET /api/chat/conversations", "success")
                tests_passed += 1
            else:
                print_status(f"GET /api/chat/conversations - {response.status_code}", "error")
        except Exception as e:
            print_status(f"GET /api/chat/conversations - {e}", "error")
        
        # Test 2: List knowledge items
        tests_total += 1
        try:
            response = await client.get(f"{BACKEND_URL}/api/knowledge")
            if response.status_code == 200:
                data = response.json()
                print_status(f"GET /api/knowledge ({len(data)} items)", "success")
                tests_passed += 1
            else:
                print_status(f"GET /api/knowledge - {response.status_code}", "error")
        except Exception as e:
            print_status(f"GET /api/knowledge - {e}", "error")
        
        # Test 3: API docs
        tests_total += 1
        try:
            response = await client.get(f"{BACKEND_URL}/docs")
            if response.status_code == 200:
                print_status("GET /docs (OpenAPI)", "success")
                tests_passed += 1
            else:
                print_status(f"GET /docs - {response.status_code}", "error")
        except Exception as e:
            print_status(f"GET /docs - {e}", "error")
        
        # Test 4: Proposals endpoint
        tests_total += 1
        try:
            response = await client.get(f"{BACKEND_URL}/api/proposals")
            if response.status_code == 200:
                print_status("GET /api/proposals", "success")
                tests_passed += 1
            else:
                print_status(f"GET /api/proposals - {response.status_code}", "error")
        except Exception as e:
            print_status(f"GET /api/proposals - {e}", "error")
        
        # Test 5: Research endpoint
        tests_total += 1
        try:
            response = await client.get(f"{BACKEND_URL}/api/research")
            if response.status_code == 200:
                print_status("GET /api/research", "success")
                tests_passed += 1
            else:
                print_status(f"GET /api/research - {response.status_code}", "error")
        except Exception as e:
            print_status(f"GET /api/research - {e}", "error")
    
    print_status(f"Passed {tests_passed}/{tests_total} API tests", 
                 "success" if tests_passed == tests_total else "warning")
    return tests_passed == tests_total


async def run_full_test():
    """Run all connectivity and functionality tests."""
    print_header("Running Full Demo Test Suite")
    
    results = {
        "backend": False,
        "frontend": False,
        "websocket": False,
        "azure_openai": False,
        "api_endpoints": False,
        "knowledge_base": False,
    }
    
    # Backend health
    results["backend"] = await check_backend_health()
    
    # Frontend health
    results["frontend"] = await check_frontend_health()
    
    # WebSocket
    if results["backend"]:
        results["websocket"] = await test_websocket_connection()
    
    # Azure OpenAI
    results["azure_openai"] = await test_azure_openai()
    
    # API endpoints
    if results["backend"]:
        results["api_endpoints"] = await test_api_endpoints()
    
    # Knowledge base
    counts = await count_knowledge_items()
    if counts["knowledge_items"] > 0 and counts["engagements"] > 0:
        print_status(
            f"Knowledge base loaded: {counts['knowledge_items']} items, {counts['engagements']} engagements",
            "success"
        )
        results["knowledge_base"] = True
    else:
        print_status("Knowledge base is empty - run 'seed' command", "warning")
    
    # Summary
    print_header("Test Summary")
    
    for test, passed in results.items():
        status = "success" if passed else "error"
        print_status(test.replace("_", " ").title(), status)
    
    passed = sum(results.values())
    total = len(results)
    
    print()
    if passed == total:
        print_status(f"All {total} tests passed! Demo environment is ready.", "success")
    else:
        print_status(f"{passed}/{total} tests passed. Review failures above.", "warning")
    
    return passed == total


async def quick_status():
    """Quick health check for demo readiness."""
    print_header("Federation Demo Status Check")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Quick checks
    backend_ok = await check_backend_health()
    frontend_ok = await check_frontend_health()
    
    if backend_ok:
        await test_websocket_connection()
        
        # Knowledge base status
        counts = await count_knowledge_items()
        if counts["knowledge_items"] > 0:
            print_status(
                f"Knowledge base: {counts['knowledge_items']} items, {counts['engagements']} engagements",
                "success"
            )
        else:
            print_status("Knowledge base empty - run: python demo_setup.py seed", "warning")
        
        # Conversation count
        convs = await list_conversations()
        if len(convs) > 0:
            print_status(f"Active conversations: {len(convs)} (run 'cleanup' for clean demo)", "warning")
        else:
            print_status("No existing conversations - clean state", "success")
    
    print()
    if backend_ok and frontend_ok:
        print_status("Demo environment ready! Open http://localhost:3000", "success")
    else:
        print_status("Fix issues above before proceeding", "error")


async def full_demo_prep():
    """Full demo preparation: cleanup + seed + test."""
    print_header("Full Demo Preparation")
    print("  This will clean up conversations, seed the knowledge base,")
    print("  and run all tests to verify the demo environment.")
    print()
    
    # Step 1: Cleanup
    await cleanup_conversations()
    
    # Step 2: Seed
    await seed_knowledge_base()
    
    # Step 3: Test
    success = await run_full_test()
    
    print()
    if success:
        print_header("Demo Ready!")
        print("  ✅ Open browser: http://localhost:3000")
        print("  ✅ Agent status panel should show 'Connected'")
        print("  ✅ Try: 'Create a proposal for Acme Corp digital transformation'")
        print()
    else:
        print_header("Demo Preparation Incomplete")
        print("  Review the test failures above and fix before demo.")
        print()
    
    return success


def print_usage():
    """Print script usage information."""
    print(__doc__)


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "cleanup":
        await cleanup_conversations()
    elif command == "seed":
        await seed_knowledge_base()
    elif command == "test":
        await run_full_test()
    elif command == "full":
        await full_demo_prep()
    elif command == "status":
        await quick_status()
    elif command == "help" or command == "-h" or command == "--help":
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    asyncio.run(main())
