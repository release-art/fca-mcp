"""MCP server implementation."""

from __future__ import annotations

import contextlib
import logging
import os
import weakref

import fastmcp
import fca_api
from fastmcp.server.lifespan import lifespan
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware

import fca_mcp

logger = logging.getLogger(__name__)

from . import deps, firms, types


@lifespan
async def mcp_lifespan(app: fastmcp.FastMCP):
    fca_email = os.environ["FCA_API_USERNAME"]
    fca_key = os.environ["FCA_API_KEY"]
    client = fca_api.async_api.Client((fca_email, fca_key))
    logger.info(f"Server {app} initialized successfully")
    async with client:
        yield {"fca_app": fca_mcp.types.FcaApp(fca_api=client)}
    logger.info("Server shutdown complete")


def get_server() -> fastmcp.FastMCP:
    main = fastmcp.FastMCP(
        "fca-api",
        lifespan=mcp_lifespan,
        website_url="https://www.release.art/",
        on_duplicate="error",
        strict_input_validation=True,
    )
    main.mount(firms.get_server())

    main.add_middleware(ErrorHandlingMiddleware())
    main.add_middleware(RateLimitingMiddleware())
    main.add_middleware(LoggingMiddleware())
    return main
