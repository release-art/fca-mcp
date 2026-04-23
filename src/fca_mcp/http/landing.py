"""Static HTML landing page served on ``GET /``.

The MCP ``streamable-http`` endpoint also lives at ``/`` but only accepts
``POST``/``DELETE``. Starlette's router treats path and method
independently, so a ``GET`` ``Route`` at the same path coexists cleanly —
``POST`` flows to the MCP session manager, ``GET`` flows to this landing
handler.
"""

from __future__ import annotations

import functools
import logging
import pathlib

import fastmcp
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.requests import Request
from starlette.responses import HTMLResponse

import fca_mcp

logger = logging.getLogger(__name__)

_RESOURCES_DIR = pathlib.Path(__file__).parent / "resources"


@functools.cache
def _jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(_RESOURCES_DIR),
        autoescape=select_autoescape(("html", "htm")),
    )


async def _landing(request: Request) -> HTMLResponse:
    template = _jinja_env().get_template("landing.html")
    body = template.render(
        version=fca_mcp.__version__.__version__,
        website_url="https://www.release.art/",
        icon_url="https://static.release.art/assets/icons/brandmark_blue.svg",
    )
    return HTMLResponse(body)


def mount_landing_router(mcp: fastmcp.FastMCP) -> None:
    """Attach ``GET /`` — a small human-readable landing page."""
    mcp.custom_route("/", methods=["GET"], include_in_schema=False)(_landing)
