"""MCP server implementation."""
from __future__ import annotations

import fastmcp
import logging

logger = logging.getLogger(__name__)

from . import firms, deps

def get_server() -> fastmcp.FastMCP:
    main = fastmcp.FastMCP("fca-api")
    main.mount(firms.get_server())
    return main