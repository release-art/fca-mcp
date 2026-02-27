import logging
from typing import Annotated

import asyncstdlib
import fastmcp
import fca_api
import pydantic

from . import deps, types

logger = logging.getLogger(__name__)
funds_mcp = fastmcp.FastMCP("search-funds", on_duplicate="error")


@funds_mcp.tool
async def get_fund(
    prn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> fca_api.types.products.ProductDetails:
    """Get fund details by PRN"""
    out = await fca_client.get_fund(prn)
    return out


@funds_mcp.tool
async def get_fund_names(
    prn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> fca_api.types.pagination.MultipageList[fca_api.types.products.ProductNameAlias]:
    """Get fund names by PRN"""
    out = await fca_client.get_fund_names(prn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.products.ProductNameAlias](items=els)
    return out


@funds_mcp.tool
async def get_fund_subfunds(
    prn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> fca_api.types.pagination.MultipageList[fca_api.types.products.SubFundDetails]:
    """Get fund sub-funds by PRN"""
    out = await fca_client.get_fund_subfunds(prn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.products.SubFundDetails](items=els)
    return out


def get_server() -> fastmcp.FastMCP:
    return funds_mcp
