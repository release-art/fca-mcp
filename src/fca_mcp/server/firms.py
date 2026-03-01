"""Search firms"""

import logging

import fastmcp
import fca_api

from . import deps, types

logger = logging.getLogger(__name__)


firms_mcp = fastmcp.FastMCP("search-firms", on_duplicate="error")


@firms_mcp.tool
async def get_firm(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> types.firm.FirmDetails:
    """Get detailed firm info by FRN"""
    result = await fca_client.get_firm(frn)
    return types.firm.FirmDetails.from_api_t(result)


@firms_mcp.tool
async def get_firm_names(
    frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[fca_api.types.firm.FirmNameAlias]:
    """Get firm names by FRN"""
    out = await fca_client.get_firm_names(frn)
    els = out.local_items()
    return types.list_t.PaginatedList[types.firm.FirmNameAlias](
        items=[types.firm.FirmNameAlias.from_api_t(el) for el in els], start_index=0, has_next=False
    )


@firms_mcp.tool
async def get_firm_adresses(
    frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.firm.FirmAddress]:
    """Get firm addresses by FRN"""
    out = await fca_client.get_firm_addresses(frn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.firm.FirmAddress](
        items=[types.firm.FirmAddress.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


@firms_mcp.tool
async def get_firm_controlled_functions(
    frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.firm.FirmControlledFunction]:
    """Get firm controlled functions by FRN"""
    out = await fca_client.get_firm_controlled_functions(frn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.firm.FirmControlledFunction](
        items=[types.firm.FirmControlledFunction.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


@firms_mcp.tool
async def get_firm_individuals(
    frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.firm.FirmIndividual]:
    """Get firm individuals by FRN"""
    out = await fca_client.get_firm_individuals(frn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.firm.FirmIndividual](
        items=[types.firm.FirmIndividual.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


@firms_mcp.tool
async def get_firm_permissions(
    frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.firm.FirmPermission]:
    """Get firm permissions by FRN"""
    out = await fca_client.get_firm_permissions(frn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.firm.FirmPermission](
        items=[types.firm.FirmPermission.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


@firms_mcp.tool
async def get_firm_requirements(
    frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.firm.FirmRequirement]:
    """Get firm requirements by FRN"""
    out = await fca_client.get_firm_requirements(frn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.firm.FirmRequirement](
        items=[types.firm.FirmRequirement.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


@firms_mcp.tool
async def get_firm_requirement_investment_types(
    frn: str, req_ref: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.firm.FirmRequirementInvestmentType]:
    """Get investment types for a specific firm requirement"""
    out = await fca_client.get_firm_requirement_investment_types(frn, req_ref)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.firm.FirmRequirementInvestmentType](
        items=[types.firm.FirmRequirementInvestmentType.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


@firms_mcp.tool
async def get_firm_regulators(
    frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.firm.FirmRegulator]:
    """Get firm regulators by FRN"""
    out = await fca_client.get_firm_regulators(frn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.firm.FirmRegulator](
        items=[types.firm.FirmRegulator.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


@firms_mcp.tool
async def get_firm_passports(
    frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.firm.FirmPassport]:
    """Get firm passports by FRN"""
    out = await fca_client.get_firm_passports(frn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.firm.FirmPassport](
        items=[types.firm.FirmPassport.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


@firms_mcp.tool
async def get_firm_passport_permissions(
    frn: str, country: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.firm.FirmPassportPermission]:
    """Get firm passport permissions by FRN and country"""
    out = await fca_client.get_firm_passport_permissions(frn, country)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.firm.FirmPassportPermission](
        items=[types.firm.FirmPassportPermission.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


@firms_mcp.tool
async def get_firm_waivers(
    frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.firm.FirmWaiver]:
    """Get firm waivers by FRN"""
    out = await fca_client.get_firm_waivers(frn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.firm.FirmWaiver](
        items=[types.firm.FirmWaiver.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


@firms_mcp.tool
async def get_firm_exclusions(
    frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.firm.FirmExclusion]:
    """"""
    out = await fca_client.get_firm_exclusions(frn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.firm.FirmExclusion](
        items=[types.firm.FirmExclusion.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


@firms_mcp.tool
async def get_firm_disciplinary_history(
    frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.firm.FirmDisciplinaryRecord]:
    """"""
    out = await fca_client.get_firm_disciplinary_history(frn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.firm.FirmDisciplinaryRecord](
        items=[types.firm.FirmDisciplinaryRecord.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


@firms_mcp.tool
async def get_firm_appointed_representatives(
    frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.list_t.PaginatedList[types.firm.FirmAppointedRepresentative]:
    """Get firm appointed representatives by FRN"""
    out = await fca_client.get_firm_appointed_representatives(frn)
    els = out.local_items()
    out = types.list_t.PaginatedList[types.firm.FirmAppointedRepresentative](
        items=[types.firm.FirmAppointedRepresentative.from_api_t(el) for el in els], start_index=0, has_next=False
    )
    return out


def get_server() -> fastmcp.FastMCP:
    return firms_mcp
