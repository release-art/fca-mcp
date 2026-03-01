import logging

import fastmcp
import fca_api

from . import deps, types

logger = logging.getLogger(__name__)
funds_mcp = fastmcp.FastMCP("search-funds", on_duplicate="error")


@funds_mcp.tool
async def get_fund(prn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> types.products.ProductDetails:
    """Get fund details by PRN"""
    out = await fca_client.get_fund(prn)
    return types.products.ProductDetails.from_api_t(out)


@funds_mcp.tool
async def get_fund_names(
    prn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.products.ProductNameAlias]:
    """Get fund names by PRN"""
    out = await fca_client.get_fund_names(prn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.products.ProductNameAlias](
        items=[types.products.ProductNameAlias.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


@funds_mcp.tool
async def get_fund_subfunds(
    prn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.products.SubFundDetails]:
    """Get fund sub-funds by PRN"""
    out = await fca_client.get_fund_subfunds(prn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.products.SubFundDetails](
        items=[types.products.SubFundDetails.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


def get_server() -> fastmcp.FastMCP:
    return funds_mcp
