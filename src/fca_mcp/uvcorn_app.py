from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

import fastapi
import toon
from fastapi.middleware.cors import CORSMiddleware

import fca_mcp

logger = logging.getLogger(__name__)

healthchecks = fastapi.APIRouter(prefix="/_container", tags=["Health"])


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


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    """Manage application lifespan - startup and shutdown."""

    fca_email = os.environ["FCA_API_USERNAME"]
    fca_key = os.environ["FCA_API_KEY"]

    logger.info("Server initialized successfully")
    adapter = fca_mcp.adapters.fca_async_adapter.FcaApiAdapter((fca_email, fca_key))
    app.my_app_ctx = my_app = fca_mcp.types.FcaApp(fca_api_adapter=adapter)

    async with my_app.fca_api_adapter:
        yield


async def toon_middleware(request: fastapi.Request, call_next):
    print(request.headers, request.method)
    is_mcp = any(header.startswith("mcp-") for header in request.keys())
    response = await call_next(request)
    logger.info(f"{is_mcp=!r}")
    if is_mcp:
        response.headers["Content-Type"] = "text/plain"
        if isinstance(response.content, dict):
            response.content = toon.encode(response.content)
    return response


def get_fastapi_app() -> FastAPI:
    """Get the FastAPI application instance."""
    app = fastapi.FastAPI(
        title="FCA MCP Server API",
        description="HTTP API for FCA regulatory data with AI analysis",
        version=fca_mcp.version,
        lifespan=lifespan,
    )
    app.include_router(healthchecks)
    mcp_router = fca_mcp.server.api.get_router()
    app.include_router(mcp_router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    mcp = fca_mcp.server.get_server()
    app.mount("/mcp", mcp.http_app(path="/"))
    return app
