import logging

import fastmcp
import fca_api

from . import deps, types

logger = logging.getLogger(__name__)

markets_mcp = fastmcp.FastMCP("search-markets", on_duplicate="error")


@markets_mcp.tool
async def get_regulated_markets(
    fca_client: fca_api.async_api.Client = deps.FcaApiDep,
) -> fca_api.types.pagination.MultipageList[fca_api.types.markets.RegulatedMarket]:
    """Get regulated markets"""
    out = await fca_client.get_regulated_markets()
    els = out.local_items()
    out = types.list_t.PaginatedList[fca_api.types.markets.RegulatedMarket](items=els)
    return out
