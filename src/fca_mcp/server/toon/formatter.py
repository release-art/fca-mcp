"""TOON formatter for MCP responses."""

from typing import Any

from fca_mcp.models.meta import ResponseMeta
from fca_mcp.models.toon import ToonResponse


class ToonFormatter:
    """Formats responses in TOON (Type-Object-Object-Namespace) format."""

    @staticmethod
    def format_response(
        data: Any,
        response_type: str,
        pages_loaded: int = 1,
        items_returned: int = 0,
        truncated: bool = False,
        total_available: int | None = None,
        execution_time_ms: float | None = None,
        version: str = "1.0",
    ) -> ToonResponse:
        """Format data in TOON structure.

        Args:
            data: Response data to format
            response_type: Type identifier (e.g., 'fca.firm.search')
            pages_loaded: Number of pages loaded
            items_returned: Total items in response
            truncated: Whether response was truncated
            total_available: Total items available (if known)
            execution_time_ms: Execution time in milliseconds
            version: Schema version

        Returns:
            TOON formatted response
        """
        meta = ResponseMeta(
            pages_loaded=pages_loaded,
            items_returned=items_returned,
            truncated=truncated,
            total_available=total_available,
            execution_time_ms=execution_time_ms,
        )

        return ToonResponse(type=response_type, version=version, data=data, meta=meta)

    @staticmethod
    def format_search_results(
        results: list[Any],
        total: int | None = None,
        truncated: bool = False,
        execution_time_ms: float | None = None,
    ) -> ToonResponse:
        """Format search results."""
        return ToonFormatter.format_response(
            data=results,
            response_type="fca.firm.search",
            items_returned=len(results),
            truncated=truncated,
            total_available=total,
            execution_time_ms=execution_time_ms,
        )

    @staticmethod
    def format_firm_details(
        firm: Any,
        execution_time_ms: float | None = None,
    ) -> ToonResponse:
        """Format firm details."""
        return ToonFormatter.format_response(
            data=firm,
            response_type="fca.firm.details",
            items_returned=1,
            execution_time_ms=execution_time_ms,
        )

    @staticmethod
    def format_firm_related(
        data: list[Any],
        kind: str,
        pages_loaded: int,
        truncated: bool,
        total_available: int | None = None,
        execution_time_ms: float | None = None,
    ) -> ToonResponse:
        """Format firm related data (names, addresses, etc)."""
        return ToonFormatter.format_response(
            data=data,
            response_type=f"fca.firm.{kind}",
            pages_loaded=pages_loaded,
            items_returned=len(data),
            truncated=truncated,
            total_available=total_available,
            execution_time_ms=execution_time_ms,
        )
