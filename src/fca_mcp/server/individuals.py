import logging
from typing import Annotated

import asyncstdlib
import fastmcp
import fca_api
import pydantic

from . import deps, types

logger = logging.getLogger(__name__)


individuals_mcp = fastmcp.FastMCP("search-individuals", on_duplicate="error")


@individuals_mcp.tool
async def get_individual(
    irn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> fca_api.types.individual.Individual:
    """Get individual details by IRN"""
    out = await fca_client.get_individual(irn)
    return out


@individuals_mcp.tool
async def get_individual_controlled_functions(
    irn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> fca_api.types.pagination.MultipageList[fca_api.types.individual.IndividualControlledFunction]:
    """Get controlled functions for an individual"""
    out = await fca_client.get_individual_controlled_functions(irn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.individual.IndividualControlledFunction](items=els)
    return out


@individuals_mcp.tool
async def get_individual_disciplinary_history(
    irn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> fca_api.types.pagination.MultipageList[fca_api.types.individual.IndividualDisciplinaryRecord]:
    """Get disciplinary history records for an individual"""
    out = await fca_client.get_individual_disciplinary_history(irn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.individual.IndividualDisciplinaryRecord](items=els)
    return out


def get_server() -> fastmcp.FastMCP:
    return individuals_mcp
