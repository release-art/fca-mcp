"""HTTP app factory for the uvicorn entrypoint."""

from __future__ import annotations

import logging
import time
from datetime import datetime

from starlette.applications import Starlette
from starlette.middleware import Middleware as StarletteMiddleware
from starlette.middleware.cors import CORSMiddleware as StarletteCORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

import fca_mcp

logger = logging.getLogger(__name__)
START_T = time.monotonic()

# Canonical MCP endpoint path, plus any aliases that point at the same ASGI
# handler. Clients that hard-code one path or the other both work.
MCP_PATH = "/"
MCP_ALIASES: tuple[str, ...] = ("/mcp",)


async def health(request: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        {
            "status": "healthy",
            "service": "FCA MCP Server",
            "version": fca_mcp.__version__.__version__,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.monotonic() - START_T,
        }
    )


def get_http_app() -> Starlette:
    """Compose the Starlette app: MCP plus any enabled HTTP side-routes."""
    logger.info("Creating FastAPI application...")
    mcp = fca_mcp.server.get_server()
    mcp.custom_route("/.container/health", methods=["GET"], include_in_schema=False)(health)
    fca_mcp.http.mount_landing_router(mcp)

    app = mcp.http_app(
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
    _install_mcp_aliases(app, canonical=MCP_PATH, aliases=MCP_ALIASES)
    return app


def _install_mcp_aliases(app: Starlette, *, canonical: str, aliases: tuple[str, ...]) -> None:
    """Expose the MCP endpoint at multiple paths simultaneously.

    FastMCP's ``http_app(path=...)`` only accepts a single canonical path,
    but returns a stock Starlette app. We locate the canonical MCP route
    and append a fresh ``Route`` for each alias that reuses the same ASGI
    endpoint and HTTP-method set — no redirects, both paths serve the MCP
    session manager directly.
    """
    canonical_route: Route | None = next(
        (r for r in app.routes if isinstance(r, Route) and r.path == canonical),
        None,
    )
    if canonical_route is None:
        raise RuntimeError(f"Canonical MCP route {canonical!r} not found on Starlette app")

    for alias in aliases:
        app.routes.append(
            Route(
                alias,
                endpoint=canonical_route.endpoint,
                methods=list(canonical_route.methods or []),
            )
        )
        logger.info("Mounted MCP endpoint alias %s → %s", alias, canonical)
