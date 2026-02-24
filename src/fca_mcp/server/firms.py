"""Search firms"""

from __future__ import annotations

import logging

import fastmcp
import fca_api

from . import deps, types

logger = logging.getLogger(__name__)


firms_mcp = fastmcp.FastMCP("search-firms", on_duplicate="error")


@firms_mcp.tool
async def search_frn(
    firm_name: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep
) -> types.PaginatedList[fca_api.types.search.FirmSearchResult]:
    """Search for firms by name"""
    out = await fca_client.search_frn(firm_name)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.search.FirmSearchResult](items=els)
    return out


@firms_mcp.tool
async def search_irn(individual_name: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.search.IndividualSearchResult]:
    """Search result for an individual from the FCA register"""
    out = await fca_client.search_irn(individual_name)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.search.IndividualSearchResult](items=els)
    return out


@firms_mcp.tool
async def search_prn(fund_name: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.search.FundSearchResult]:
    """Search for funds by name"""
    out = await fca_client.search_prn(fund_name)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.search.FundSearchResult](items=els)
    return out



@firms_mcp.tool
async def get_firm(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.firm.FirmDetails:
    """Get detailed firm info by FRN"""
    result = await fca_client.get_firm(frn)
    return result.model_dump(mode="json")


@firms_mcp.tool
async def get_firm_names(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.firm.FirmNameAlias]:
    """Get firm names by FRN"""
    out = await fca_client.get_firm_names(frn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.firm.FirmNameAlias](items=els)
    return out


@firms_mcp.tool
async def get_firm_adresses(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.firm.FirmAddress]:
    """Get firm addresses by FRN"""
    out = await fca_client.get_firm_addresses(frn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.firm.FirmAddress](items=els)
    return out


@firms_mcp.tool
async def get_firm_controlled_functions(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.firm.FirmControlledFunction]:
    """Get firm controlled functions by FRN"""
    out = await fca_client.get_firm_controlled_functions(frn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.firm.FirmControlledFunction](items=els)
    return out


@firms_mcp.tool
async def get_firm_individuals(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.firm.FirmIndividual]:
    """Get firm individuals by FRN"""
    out = await fca_client.get_firm_individuals(frn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.firm.FirmIndividual](items=els)
    return out


@firms_mcp.tool
async def get_firm_permissions(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.firm.FirmPermission]:
    """Get firm permissions by FRN"""
    out = await fca_client.get_firm_permissions(frn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.firm.FirmPermission](items=els)
    return out
    

@firms_mcp.tool
async def get_firm_requirements(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.firm.FirmRequirement]:
    """Get firm requirements by FRN"""
    out = await fca_client.get_firm_requirements(frn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.firm.FirmRequirement](items=els)
    return out


@firms_mcp.tool
async def get_firm_requirement_investment_types(frn:str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.firm.FirmRequirementInvestmentType]:
    """Get investment types for a specific firm requirement"""
    out = await fca_client.get_firm_requirement_invenstment_type(frn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.firm.FirmRequirementInvestmentType](items=els)
    return out


@firms_mcp.tool
async def get_firm_regulators(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.firm.FirmRegulator]:
    """Get firm regulators by FRN"""
    out = await fca_client.get_firm_regulators(frn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.firm.FirmRegulator](items=els)
    return out


@firms_mcp.tool
async def get_firm_passports(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.firm.FirmPassport]:
    """Get firm passports by FRN"""
    out = await fca_client.get_firm_passports(frn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.firm.FirmPassport](items=els)
    return out


@firms_mcp.tool
async def get_firm_passport_permissions(frn: str, country: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.firm.FirmPassportPermission]:
    """Get firm passport permissions by FRN and country"""
    out = await fca_client.get_firm_passport_permissions(frn, country)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.firm.FirmPassportPermission](items=els)
    return out


@firms_mcp.tool
async def get_firm_waivers(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.firm.FirmWaiver]:
    """Get firm waivers by FRN"""
    out = await fca_client.get_firm_waivers(frn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.firm.FirmWaiver](items=els)
    return out


@firms_mcp.tool
async def get_firm_exclusions(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.firm.FirmExclusion]:
    """"""
    out = await fca_client.get_firm_exclusions(frn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.firm.FirmExclusion](items=els)
    return out


@firms_mcp.tool
async def get_firm_disciplinary_history(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.firm.FirmDisciplinaryRecord]:
    """"""
    out = await fca_client.get_firm_disciplinary_history(frn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.firm.FirmDisciplinaryRecord](items=els)
    return out


@firms_mcp.tool
async def get_firm_appointed_representatives(frn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.firm.FirmAppointedRepresentative]:
    """Get firm appointed representatives by FRN"""
    out = await fca_client.get_firm_appointed_representatives(frn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.firm.FirmAppointedRepresentative](items=els)
    return out


@firms_mcp.tool
async def get_individual(irn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.individual.Individual:
    """Get individual details by IRN"""
    out = await fca_client.get_individual(irn)
    return out


@firms_mcp.tool
async def get_individual_controlled_functions(irn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.individual.IndividualControlledFunction]:
    """Get controlled functions for an individual"""
    out = await fca_client.get_individual_controlled_functions(irn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.individual.IndividualControlledFunction](items=els)
    return out


@firms_mcp.tool
async def get_individual_disciplinary_history(irn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.individual.IndividualDisciplinaryRecord]:
    """Get disciplinary history records for an individual"""
    out = await fca_client.get_individual_disciplinary_history(irn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.individual.IndividualDisciplinaryRecord](items=els)
    return out


@firms_mcp.tool
async def get_fund(prn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.products.ProductDetails:
    """Get fund details by PRN"""
    out = await fca_client.get_fund(prn)
    return out


@firms_mcp.tool
async def get_fund_names(prn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.products.ProductNameAlias]:
    """Get fund names by PRN"""
    out = await fca_client.get_fund_names(prn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.products.ProductNameAlias](items=els) 
    return out


@firms_mcp.tool
async def get_fund_subfunds(prn: str, fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.products.SubFundDetails]:
    """Get fund sub-funds by PRN"""
    out = await fca_client.get_fund_subfunds(prn)
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.products.SubFundDetails](items=els) 
    return out


@firms_mcp.tool
async def get_regulated_markets(fca_client: fca_api.async_api.Client = deps.FcaApiDep) -> fca_api.types.pagination.MultipageList[fca_api.types.markets.RegulatedMarket]:
    """Get regulated markets"""
    out = await fca_client.get_regulated_markets()
    els = out.local_items()
    out = types.PaginatedList[fca_api.types.markets.RegulatedMarket](items=els)
    return out


def get_server() -> fastmcp.FastMCP:
    return firms_mcp
