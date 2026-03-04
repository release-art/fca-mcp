from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime

import fastapi
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware
from fastmcp.utilities.lifespan import combine_lifespans
from starlette.middleware import Middleware as StarletteMiddleware
from starlette.middleware.cors import CORSMiddleware as StarletteCORSMiddleware

import fca_mcp

logger = logging.getLogger(__name__)

healthchecks = fastapi.APIRouter(prefix="/.container", tags=["Health"])


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
async def http_lifespan(app: fastapi.FastAPI):
    logger.debug("Starting up the HTTP app...")
    yield
    logger.debug("Shutting down the HTTP app...")


MCP_PATH = "/mcp"


def get_fastapi_app() -> fastapi.FastAPI:
    """Get the FastAPI application instance."""
    logger.info("Creating FastAPI application...")
    mcp = fca_mcp.server.get_server()
    mcp_app = mcp.http_app(
        path=MCP_PATH,
        middleware=[
            StarletteMiddleware(
                StarletteCORSMiddleware,
                allow_origins=["*"],  # Allow all origins; use specific origins for security
                allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
                allow_headers=[
                    "mcp-protocol-version",
                    "mcp-session-id",
                    "Authorization",
                    "Content-Type",
                ],
                expose_headers=["mcp-session-id"],
            )
        ],
        stateless_http=True,
    )
    app = fastapi.FastAPI(
        title="FCA MCP Server API",
        description="HTTP API for FCA regulatory data with AI analysis",
        version=fca_mcp.version,
        lifespan=combine_lifespans(
            http_lifespan,
            mcp_app.lifespan,
        ),
    )
    app.my_app_ctx = fca_mcp.app.FcaMcpApp(
        fastmcp_server=mcp,
        fastmcp_http_app=mcp_app,
    )
    app.include_router(healthchecks)
    if mcp.auth is not None:
        logger.info("Auth provider is set, including auth routes")
        well_known_router = fastapi.APIRouter(prefix="", tags=["Well-Known"])
        for route in mcp.auth.get_well_known_routes(mcp_path=MCP_PATH):
            logger.info(f"Adding well-known route: {route.path}")
            well_known_router.add_api_route(
                route.path,
                route.endpoint,
                methods=route.methods,
                name=route.name,
            )
        app.include_router(well_known_router)
    app.add_middleware(
        FastAPICORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("", mcp_app)
    return app
