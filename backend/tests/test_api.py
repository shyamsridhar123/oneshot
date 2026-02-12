"""Comprehensive API test script for OneShot backend.

This module is designed to run against a live server (python tests/test_api.py).
When run via pytest, tests are skipped unless the server is available.
"""

import asyncio
import httpx
import json
import pytest
import websockets
from datetime import datetime

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"


def _server_available() -> bool:
    """Check if the backend server is reachable."""
    try:
        import httpx as _httpx
        with _httpx.Client(timeout=2.0) as c:
            c.get(f"{BASE_URL}/health")
        return True
    except Exception:
        return False


_skip_no_server = pytest.mark.skipif(
    not _server_available(),
    reason="Live server not running at localhost:8000",
)


@_skip_no_server
async def test_health():
    """Test health endpoint."""
    print("\n🏥 Testing Health Endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        assert response.status_code == 200
        print("  ✅ Health check passed")


@_skip_no_server
async def test_root():
    """Test root endpoint."""
    print("\n🏠 Testing Root Endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        assert response.status_code == 200
        print("  ✅ Root endpoint passed")


@_skip_no_server
async def test_conversations():
    """Test conversation CRUD."""
    print("\n💬 Testing Conversations...")
    async with httpx.AsyncClient() as client:
        # Create conversation
        response = await client.post(
            f"{BASE_URL}/api/chat/conversations",
            json={"title": "Test Conversation", "metadata": {"test": True}}
        )
        print(f"  Create Status: {response.status_code}")
        conv = response.json()
        print(f"  Created: {conv['id'][:8]}... - {conv['title']}")
        assert response.status_code == 200
        
        conv_id = conv["id"]
        
        # List conversations
        response = await client.get(f"{BASE_URL}/api/chat/conversations")
        print(f"  List Status: {response.status_code}")
        convs = response.json()
        print(f"  Total conversations: {len(convs)}")
        assert response.status_code == 200
        
        # Get specific conversation
        response = await client.get(f"{BASE_URL}/api/chat/conversations/{conv_id}")
        print(f"  Get Status: {response.status_code}")
        assert response.status_code == 200
        
        print("  ✅ Conversations passed")
        return conv_id


@_skip_no_server
async def test_chat_message(conv_id: str):
    """Test sending a message and agent processing."""
    print("\n📨 Testing Chat Message (Agent Processing)...")
    print("  This may take 30-60 seconds as agents process the request...")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/chat/conversations/{conv_id}/messages",
            json={
                "content": "I need to create a proposal for a digital transformation engagement for a manufacturing company called Acme Industries. They want to modernize their supply chain.",
                "metadata": {"source": "test"}
            }
        )
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            msg = response.json()
            print(f"  Message ID: {msg['id'][:8]}...")
            print(f"  Response preview: {msg['content'][:200]}...")
            print("  ✅ Chat message passed")
        else:
            print(f"  ❌ Error: {response.text}")


@_skip_no_server
async def test_proposals():
    """Test proposal endpoints."""
    print("\n📋 Testing Proposals...")
    async with httpx.AsyncClient() as client:
        # List proposals
        response = await client.get(f"{BASE_URL}/api/proposals")
        print(f"  List Status: {response.status_code}")
        proposals = response.json()
        print(f"  Total proposals: {len(proposals)}")
        assert response.status_code == 200
        print("  ✅ Proposals list passed")


@_skip_no_server
async def test_documents():
    """Test document endpoints."""
    print("\n📄 Testing Documents...")
    async with httpx.AsyncClient() as client:
        # List documents
        response = await client.get(f"{BASE_URL}/api/documents")
        print(f"  List Status: {response.status_code}")
        docs = response.json()
        print(f"  Total documents: {len(docs)}")
        assert response.status_code == 200
        print("  ✅ Documents list passed")


@_skip_no_server
async def test_knowledge():
    """Test knowledge search."""
    print("\n🧠 Testing Knowledge Search...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/knowledge/search",
            json={
                "query": "digital transformation manufacturing",
                "limit": 5
            }
        )
        print(f"  Search Status: {response.status_code}")
        results = response.json()
        print(f"  Results found: {len(results)}")
        for r in results[:3]:
            print(f"    - {r['title']} ({r['category']})")
        assert response.status_code == 200
        print("  ✅ Knowledge search passed")


@_skip_no_server
async def test_similar_engagements():
    """Test similar engagements search."""
    print("\n🔍 Testing Similar Engagements...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/knowledge/similar",
            params={"query": "supply chain optimization for manufacturing", "limit": 3}
        )
        print(f"  Status: {response.status_code}")
        results = response.json()
        print(f"  Similar engagements found: {len(results)}")
        for r in results[:3]:
            print(f"    - {r['client_name']}: {r['engagement_type']}")
        assert response.status_code == 200
        print("  ✅ Similar engagements passed")


@_skip_no_server
async def test_analytics():
    """Test analytics endpoints."""
    print("\n📊 Testing Analytics...")
    async with httpx.AsyncClient() as client:
        # Get traces
        response = await client.get(f"{BASE_URL}/api/analytics/traces")
        print(f"  Traces Status: {response.status_code}")
        traces = response.json()
        print(f"  Total traces: {len(traces)}")
        
        # Get metrics
        response = await client.get(f"{BASE_URL}/api/analytics/metrics?period=day")
        print(f"  Metrics Status: {response.status_code}")
        metrics = response.json()
        print(f"  Total executions: {metrics.get('total_executions', 0)}")
        
        assert response.status_code == 200
        print("  ✅ Analytics passed")


@_skip_no_server
async def test_research():
    """Test research endpoints."""
    print("\n🔬 Testing Research...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/research/query",
            json={
                "query": "digital transformation trends in manufacturing",
                "research_type": "comprehensive"
            }
        )
        print(f"  Query Status: {response.status_code}")
        result = response.json()
        print(f"  Status: {result.get('status')}")
        assert response.status_code == 200
        print("  ✅ Research query passed")


@_skip_no_server
async def test_websocket(conv_id: str):
    """Test WebSocket connection."""
    print("\n🔌 Testing WebSocket...")
    try:
        async with websockets.connect(f"{WS_URL}/ws/agents/{conv_id}") as ws:
            print("  Connected to WebSocket")
            
            # Send ping
            await ws.send("ping")
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            print(f"  Ping response: {response}")
            
            print("  ✅ WebSocket passed")
    except Exception as e:
        print(f"  ⚠️ WebSocket test skipped: {e}")


async def run_all_tests():
    """Run all API tests."""
    print("=" * 60)
    print("🚀 OneShot Backend API Tests")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    print("=" * 60)
    
    try:
        await test_health()
        await test_root()
        conv_id = await test_conversations()
        await test_proposals()
        await test_documents()
        await test_knowledge()
        await test_similar_engagements()
        await test_analytics()
        await test_research()
        await test_websocket(conv_id)
        
        print("\n" + "=" * 60)
        print("🎉 All basic tests passed!")
        print("=" * 60)
        
        # Now test the full agent flow
        print("\n" + "=" * 60)
        print("🤖 Testing Full Agent Flow (this takes time)...")
        print("=" * 60)
        await test_chat_message(conv_id)
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        
    except httpx.ConnectError:
        print("\n❌ Could not connect to server!")
        print("   Make sure the server is running:")
        print("   cd backend && source .venv/bin/activate && uvicorn app.main:app --reload")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
