"""FastAPI application entry point."""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.database import init_db
from app.api.routes import chat, proposals, research, documents, knowledge, analytics
from app.api.websocket import websocket_router

logger = logging.getLogger(__name__)


def _install_mcp_cleanup_filter():
    """Suppress harmless MCP stdio client teardown errors.

    The MCP stdio_client async generator sometimes gets finalized in a
    different task than the one that opened it, triggering a RuntimeError
    from anyio's cancel-scope checks.  This is cosmetic — the agent run
    has already completed successfully — so we filter it out.
    """
    loop = asyncio.get_running_loop()
    _default_handler = loop.get_exception_handler()

    def _handler(loop, context):
        asyncgen = context.get("asyncgen")
        if asyncgen and "stdio_client" in getattr(asyncgen, "__qualname__", ""):
            logger.debug("Suppressed MCP stdio cleanup error (harmless)")
            return
        if _default_handler:
            _default_handler(loop, context)
        else:
            loop.default_exception_handler(context)

    loop.set_exception_handler(_handler)


def _enable_otel_tracing():
    """Enable OpenTelemetry tracing for MAF agents if configured."""
    if os.environ.get("ENABLE_INSTRUMENTATION", "").lower() in ("true", "1"):
        try:
            from agent_framework.observability import configure_otel_providers
            configure_otel_providers()
            logger.info("OpenTelemetry tracing enabled for MAF agents")
        except ImportError:
            logger.debug("agent_framework.observability not available, skipping OTel setup")
        except Exception as e:
            logger.warning("Failed to enable OpenTelemetry: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    _install_mcp_cleanup_filter()
    _enable_otel_tracing()
    await init_db()
    print("✓ Database initialized")
    yield
    # Shutdown
    print("✓ Shutting down")


app = FastAPI(
    title="OneShot API",
    description="AI-Powered Professional Services Engagement Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST Routes
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(proposals.router, prefix="/api/proposals", tags=["proposals"])
app.include_router(research.router, prefix="/api/research", tags=["research"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

# WebSocket
app.include_router(websocket_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "OneShot API",
        "description": "AI-Powered Professional Services Platform",
        "docs": "/docs",
    }
