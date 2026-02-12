from __future__ import annotations

import fastapi

from .. import types as fca_mcp_types
from . import tools

router = fastapi.APIRouter(prefix="/api/fca", tags=["mcp"])


@router.get("/search_firms")
async def search_firms(params: tools.handlers.SearchFirmsParams, app: fca_mcp_types.FcaAppT) -> fastapi.Response:
    out = await app.tools.search_firms(params)
    return out


def get_router() -> fastapi.APIRouter:
    """Create and initialize MCP server.

    Args:
        fca_email: FCA API email
        fca_key: FCA API key
        enable_auth: Enable OAuth

    Returns:
        Initialized server
    """
    return router
