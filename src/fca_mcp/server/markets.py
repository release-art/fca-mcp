import logging

import fastmcp
import fca_api

from . import deps, types

logger = logging.getLogger(__name__)

markets_mcp = fastmcp.FastMCP("search-markets", on_duplicate="error")


@markets_mcp.tool
async def get_regulated_markets(
    fca_client: fca_api.async_api.Client = deps.FcaApiDep,
) -> types.list_t.PaginatedList[types.markets.RegulatedMarket]:
    """Get regulated markets"""
    out = await fca_client.get_regulated_markets()
    els = out.local_items()
    out = types.list_t.PaginatedList[types.markets.RegulatedMarket](
        items=[types.markets.RegulatedMarket.from_api_t(el) for el in els],
        start_index=0,
        has_next=False,
    )
    return out

def get_server() -> fastmcp.FastMCP:
    return markets_mcp
