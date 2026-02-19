from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime

import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastmcp.utilities.lifespan import combine_lifespans

import fca_mcp

logger = logging.getLogger(__name__)

healthchecks = fastapi.APIRouter(prefix="/_container", tags=["Health"])


@asynccontextmanager
async def http_lifespan(app: fastapi.FastAPI):
    logger.debug("Starting up the HTTP app...")
    yield {}
    logger.debug("Shutting down the HTTP app...")


@healthchecks.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "FCA MCP Server",
        "version": fca_mcp.__version__.__version__,
        "timestamp": datetime.now().isoformat(),
        "features": {"mcp_tools": True, "ai_analysis": True, "nl_interface": True},
    }


def get_fastapi_app() -> fastapi.FastAPI:
    """Get the FastAPI application instance."""
    mcp = fca_mcp.server.get_server()
    mcp_app = mcp.http_app(path="/")
    app = fastapi.FastAPI(
        title="FCA MCP Server API",
        description="HTTP API for FCA regulatory data with AI analysis",
        version=fca_mcp.version,
        lifespan=combine_lifespans(
            http_lifespan,
            mcp_app.lifespan,
        ),
    )
    app.include_router(healthchecks)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/mcp", mcp_app)
    return app
