"""MCP tool definitions and handlers."""

import time
from typing import Any

from pydantic import BaseModel, Field

from fca_mcp.adapters.fca_async_adapter import FcaApiAdapter
from fca_mcp.server.cache.memory import InMemoryCache
from fca_mcp.server.pagination.orchestrator import PaginationMode, PaginationOrchestrator
from fca_mcp.server.toon.formatter import ToonFormatter


class SearchFirmsParams(BaseModel):
    """Parameters for search_firms tool."""

    query: str = Field(..., description="Search query for firm name")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum results to return")


class FirmGetParams(BaseModel):
    """Parameters for firm_get tool."""

    firm_id: str = Field(..., description="Firm Reference Number (FRN)")
    include: list[str] = Field(
        default_factory=list,
        description="Optional quick data to include: names, addresses",
    )
    summary: bool = Field(default=True, description="Return summary format")


class FirmRelatedParams(BaseModel):
    """Parameters for firm_related tool."""

    firm_id: str = Field(..., description="Firm Reference Number (FRN)")
    kind: str = Field(
        ...,
        description="Type of related data: names, addresses, permissions, individuals, history, passports, regulators, requirements, waivers, exclusions, appointed_representatives, controlled_functions",
    )
    mode: str = Field(
        default=PaginationMode.FULL,
        description="Pagination mode: preview or full",
    )
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=50, ge=1, le=200, description="Items per page")
    max_items: int = Field(default=1000, ge=1, le=5000, description="Maximum total items")
    summary: bool = Field(default=True, description="Return summary format")


class McpTools:
    """MCP tool implementations."""

    def __init__(
        self,
        adapter: FcaApiAdapter,
        cache: InMemoryCache | None = None,
        paginator: PaginationOrchestrator | None = None,
    ):
        """Initialize tools.

        Args:
            adapter: FCA API adapter
            cache: Optional cache
            paginator: Optional paginator
        """
        self.adapter = adapter
        self.cache = cache or InMemoryCache()
        self.paginator = paginator or PaginationOrchestrator()
        self.formatter = ToonFormatter()

    async def search_firms(self, params: SearchFirmsParams) -> dict[str, Any]:
        """Search for firms by name.

        Args:
            params: Search parameters

        Returns:
            TOON formatted search results
        """
        start_time = time.time()

        cache_key = self.cache.make_key("search_firms", params.query, params.limit)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        results = await self.adapter.search_firms(params.query, params.limit)

        execution_time = (time.time() - start_time) * 1000

        response = self.formatter.format_search_results(
            results=results,
            total=None,
            truncated=len(results) >= params.limit,
            execution_time_ms=execution_time,
        )

        response_dict = response.model_dump()
        self.cache.set(cache_key, response_dict, ttl=300)

        return response_dict

    async def firm_get(self, params: FirmGetParams) -> dict[str, Any]:
        """Get firm details.

        Args:
            params: Firm get parameters

        Returns:
            TOON formatted firm details
        """
        start_time = time.time()

        cache_key = self.cache.make_key("firm_get", params.firm_id, ",".join(params.include))
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        firm = await self.adapter.get_firm(params.firm_id)

        if params.include:
            for include_type in params.include:
                if include_type == "names":
                    firm["names"] = await self.adapter.get_firm_names(params.firm_id)
                elif include_type == "addresses":
                    firm["addresses"] = await self.adapter.get_firm_addresses(params.firm_id)

        execution_time = (time.time() - start_time) * 1000

        response = self.formatter.format_firm_details(
            firm=firm,
            execution_time_ms=execution_time,
        )

        response_dict = response.model_dump()
        self.cache.set(cache_key, response_dict, ttl=600)

        return response_dict

    async def firm_related(self, params: FirmRelatedParams) -> dict[str, Any]:
        """Get firm related data.

        Args:
            params: Firm related parameters

        Returns:
            TOON formatted related data
        """
        start_time = time.time()

        cache_key = self.cache.make_key(
            "firm_related",
            params.firm_id,
            params.kind,
            params.mode,
            params.max_items,
        )
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        kind_map = {
            "names": self.adapter.get_firm_names,
            "addresses": self.adapter.get_firm_addresses,
            "permissions": self.adapter.get_firm_permissions,
            "individuals": self.adapter.get_firm_individuals,
            "history": self.adapter.get_firm_disciplinary_history,
            "passports": self.adapter.get_firm_passports,
            "regulators": self.adapter.get_firm_regulators,
            "requirements": self.adapter.get_firm_requirements,
            "waivers": self.adapter.get_firm_waivers,
            "exclusions": self.adapter.get_firm_exclusions,
            "appointed_representatives": self.adapter.get_firm_appointed_representatives,
            "controlled_functions": self.adapter.get_firm_controlled_functions,
        }

        fetch_func = kind_map.get(params.kind)
        if not fetch_func:
            raise ValueError(f"Unknown kind: {params.kind}")

        try:
            items, pages_loaded, truncated = await self.paginator.paginate(
                fetch_func=lambda: fetch_func(params.firm_id),
                mode=params.mode,
                max_items=params.max_items,
            )
        except Exception:
            # If API returns error (e.g., data not available), return empty result
            items, pages_loaded, truncated = [], 1, False

        execution_time = (time.time() - start_time) * 1000

        response = self.formatter.format_firm_related(
            data=items,
            kind=params.kind,
            pages_loaded=pages_loaded,
            truncated=truncated,
            total_available=None,
            execution_time_ms=execution_time,
        )

        response_dict = response.model_dump()
        cache_ttl = 300 if params.mode == PaginationMode.PREVIEW else 600
        self.cache.set(cache_key, response_dict, ttl=cache_ttl)

        return response_dict
