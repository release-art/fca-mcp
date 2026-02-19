"""Search firms"""

import logging
from typing import Annotated

import asyncstdlib
import fastmcp
import fca_api
import pydantic

from . import deps, types

logger = logging.getLogger(__name__)


firms_mcp = fastmcp.FastMCP("search-firms", on_duplicate="error")


@firms_mcp.tool
async def search_frn(
    firm_name: Annotated[
        str,
        pydantic.Field(
            description="The name of the firm to search for",
            min_length=3,
        ),
    ],
    start_index: Annotated[
        int,
        pydantic.Field(
            description="The index of the first item in `items` within the full list of items that could be returned by the API",
            ge=0,
        ),
    ] = 0,
    size: Annotated[
        int,
        pydantic.Field(
            description="The maximum number of items to return in `items`. The API may return fewer than this if there are not enough matching items.",
            ge=1,
            le=100,
        ),
    ] = 20,
    fca_client: fca_api.async_api.Client = deps.FcaApiDep,
) -> types.PaginatedList[fca_api.types.search.FirmSearchResult]:
    """
    Search firms by name (or part of name).

    Returns a paginated list of matching firms, including their FRNs.
    """
    out = await fca_client.search_frn(firm_name)
    els = []
    async for item in asyncstdlib.islice(out, start_index, start_index + size):
        els.append(item)

    return types.PaginatedList[fca_api.types.search.FirmSearchResult].model_validate(
        {
            "items": els,
            "start_index": start_index,
            "has_next": len(out) >= (start_index + size),
        }
    )


@firms_mcp.tool
async def get_firm(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.firm.FirmDetails:
    """Get detailed firm info by FRN"""
    result = await fca_client.get_firm(frn)
    return result


def get_server() -> fastmcp.FastMCP:
    return firms_mcp
