"""Search firms"""

from __future__ import annotations

import logging

import fastmcp
import fca_api

from . import deps, types

logger = logging.getLogger(__name__)


firms_mcp = fastmcp.FastMCP("search-firms", on_duplicate="error")


@firms_mcp.tool
async def search_frn(
    firm_name: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.PaginatedList[fca_api.types.search.FirmSearchResult]:
    """Search for firms by name"""
    out = await fca_client.search_frn(firm_name)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.search.FirmSearchResult](items=els)
    return out.model_dump(mode="json")


@firms_mcp.tool
async def get_firm(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.firm.FirmDetails:
    """Get detailed firm info by FRN"""
    result = await fca_client.get_firm(frn)
    return result.model_dump(mode="json")


def get_server() -> fastmcp.FastMCP:
    return firms_mcp
