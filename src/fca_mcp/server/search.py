import logging
from typing import Annotated

import fastmcp
import fca_api
import pydantic

from . import deps, types

logger = logging.getLogger(__name__)


search_mcp = fastmcp.FastMCP("search-firms", on_duplicate="error")


@search_mcp.tool
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
) -> types.list_t.PaginatedList[fca_api.types.search.FirmSearchResult]:
    """
    Search firms by name (or part of name).

    Returns a paginated list of matching firms, including their FRNs.
    """
    out = await fca_client.search_frn(firm_name)
    els = out.local_items()
    out = types.list_t.PaginatedList[fca_api.types.search.FirmSearchResult](items=els)
    return out


@search_mcp.tool
async def search_irn(
    individual_name: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> fca_api.types.pagination.MultipageList[fca_api.types.search.IndividualSearchResult]:
    """Search result for an individual from the FCA register"""
    out = await fca_client.search_irn(individual_name)
    els = out.local_items()
    out = types.list_t.PaginatedList[fca_api.types.search.IndividualSearchResult](items=els)
    return out


@search_mcp.tool
async def search_prn(
    fund_name: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> fca_api.types.pagination.MultipageList[fca_api.types.search.FundSearchResult]:
    """Search for funds by name"""
    out = await fca_client.search_prn(fund_name)
    els = out.local_items()
    out = types.list_t.PaginatedList[fca_api.types.search.FundSearchResult](items=els)
    return out


def get_server() -> fastmcp.FastMCP:
    return search_mcp
