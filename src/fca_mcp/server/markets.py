import logging

import fastmcp
import fca_api
from mcp.types import ToolAnnotations

from . import deps, types

logger = logging.getLogger(__name__)

markets_mcp = fastmcp.FastMCP("search-markets", on_duplicate="error")

_TOOL_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)


@markets_mcp.tool(annotations=_TOOL_ANNOTATIONS)
async def get_regulated_markets(
    fca_client: fca_api.async_api.Client = deps.FcaApiDep,
) -> types.list_t.PaginatedList[types.markets.RegulatedMarket]:
    """Retrieve the complete list of FCA-recognised regulated markets (exchanges and trading venues).

    Regulated markets are multilateral trading venues where financial instruments are
    traded under regulated conditions, such as the London Stock Exchange. Use this tool
    when the user asks about UK-regulated exchanges, trading venues, or wants to verify
    if a specific market is FCA-recognised. Takes no parameters and returns all regulated
    markets.
    """
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
