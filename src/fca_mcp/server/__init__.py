"""MCP server implementation."""

from __future__ import annotations

import asyncio
import logging

import fastmcp
import fca_api
from fastmcp.server.auth import restrict_tag
from fastmcp.server.lifespan import lifespan
from fastmcp.server.middleware import AuthMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from mcp.types import Icon

import fca_mcp

logger = logging.getLogger(__name__)

from . import app, auth, deps, firms, funds, individuals, markets, search, types


@lifespan
async def mcp_lifespan(mcp_app: fastmcp.FastMCP):
    """Open a single ``fca_api`` client for the server's lifetime.

    The client is exposed to tools via ``deps.FcaApiDep`` and closed on
    shutdown via the async-context-manager protocol.
    """
    settings = fca_mcp.settings.get_settings()
    client = fca_api.async_api.Client((settings.fca_api.username, settings.fca_api.key))
    logger.info(f"Server {mcp_app} initialized successfully")
    async with client:
        yield {"fca_app": app.FcaApp(fca_api=client)}
    logger.info("Server shutdown complete")


def get_server() -> fastmcp.FastMCP:
    """Build the composed FastMCP server.

    Mounts the five sub-servers (search, firms, funds, individuals,
    markets), wires up the middleware stack, and installs the configured
    auth provider.
    """
    main = fastmcp.FastMCP(
        "Release.art public MCP",
        lifespan=mcp_lifespan,
        website_url="https://www.release.art/",
        icons=[
            Icon(
                src="https://static.release.art/assets/icons/brandmark_blue.svg",
                type="image/svg",
                sizes=["any"],
            )
        ],
        on_duplicate="error",
        strict_input_validation=True,
        auth=auth.provider.get_auth_provider(),
        middleware=[
            AuthMiddleware(auth=restrict_tag(auth.tags.FCA_API_RO, scopes=[auth.scopes.FCA_API_RO])),
        ],
    )
    main.mount(search.get_server())
    main.mount(firms.get_server())
    main.mount(funds.get_server())
    main.mount(individuals.get_server())
    main.mount(markets.get_server())
    main.add_middleware(ErrorHandlingMiddleware())
    main.add_middleware(RateLimitingMiddleware())
    main.add_middleware(LoggingMiddleware())
    return main
