import logging

import fastmcp
import fca_api

from . import deps, types

logger = logging.getLogger(__name__)


individuals_mcp = fastmcp.FastMCP("search-individuals", on_duplicate="error")


@individuals_mcp.tool
async def get_individual(
    irn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.individual.Individual:
    """Get individual details by IRN"""
    out = await fca_client.get_individual(irn)
    return types.individual.Individual.from_api_t(out)


@individuals_mcp.tool
async def get_individual_controlled_functions(
    irn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.individual.IndividualControlledFunction]:
    """Get controlled functions for an individual"""
    out = await fca_client.get_individual_controlled_functions(irn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.individual.IndividualControlledFunction](
        items=[types.individual.IndividualControlledFunction.from_api_t(el) for el in els],
        start_index=0,
        has_next=False,
    )
    return out


@individuals_mcp.tool
async def get_individual_disciplinary_history(
    irn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.individual.IndividualDisciplinaryRecord]:
    """Get disciplinary history records for an individual"""
    out = await fca_client.get_individual_disciplinary_history(irn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.individual.IndividualDisciplinaryRecord](
        items=[types.individual.IndividualDisciplinaryRecord.from_api_t(el) for el in els],
        start_index=0,
        has_next=False,
    )
    return out


def get_server() -> fastmcp.FastMCP:
    return individuals_mcp
