"""HTTP-only routes layered on top of the MCP server."""

from . import landing
from .landing import mount_landing_router

__all__ = [
    "landing",
    "mount_landing_router",
]
