"""Caching middleware for the FCA MCP server."""

from __future__ import annotations

import contextlib
import logging
from collections.abc import AsyncGenerator

import azure.data.tables.aio as azure_tables_aio
import mcp.types
from fastmcp.server.middleware.caching import ResponseCachingMiddleware
from fastmcp.server.middleware.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult
from key_value.aio.protocols.key_value import AsyncKeyValue
from typing_extensions import override

import fca_mcp.__version__ as _fca_version
from fca_mcp.azure.api import AzureAPI
from fca_mcp.azure.table_key_value import AzureTableStore

logger = logging.getLogger(__name__)

# Appended to the configured table name prefix to form the active cache table name.
# Changing __version__.cache_version causes a new table to be created and stale
# tables from prior versions to be deleted on next startup.
_CACHE_VERSION_SLUG = _fca_version.cache_version.replace(".", "")


def _active_cache_table(settings: fca_mcp.settings.Settings) -> str:
    """Return the active cache table name: '{prefix}{cache_version_slug}'."""
    return f"{settings.table_store_names.api_cache}{_CACHE_VERSION_SLUG}"


async def _cleanup_stale_cache_tables(
    table_service_client: azure_tables_aio.TableServiceClient,
    prefix: str,
    active_table: str,
) -> None:
    """Delete cache tables belonging to previous cache_version values.

    Bump __version__.cache_version to invalidate all cached entries on significant
    API changes. Old tables are deleted here on startup; any entries that survive
    (e.g. from a concurrent instance) expire naturally via their configured TTL.
    """
    async for table_props in table_service_client.list_tables():
        name = table_props["TableName"]
        if name.startswith(prefix) and name != active_table:
            logger.info("Deleting stale cache table: %s", name)
            await table_service_client.delete_table(name)


@contextlib.asynccontextmanager
async def _open_azure_cache(settings: fca_mcp.settings.Settings) -> AsyncGenerator[AsyncKeyValue, None]:
    """Open the Azure Table Store used for API response caching.

    Manages the full Azure client lifecycle: opens all Azure Storage clients,
    deletes stale cache tables from previous cache_version values, creates the
    active table if needed, and closes everything on exit.
    """
    azure_api = AzureAPI(settings.azure)
    active_table = _active_cache_table(settings)

    async with azure_api.lifespan():
        await _cleanup_stale_cache_tables(
            azure_api.table_service_client,
            str(settings.table_store_names.api_cache),
            active_table,
        )
        store = AzureTableStore(client=azure_api.table_service_client, table_name=active_table)
        async with store:
            yield store


class FcaCachingMiddleware(Middleware):
    """Caching middleware that reads its backing store from lifespan_context.

    Registered at server construction time; the inner ResponseCachingMiddleware
    is created lazily on the first tool call, once the lifespan has stored the
    AzureTableStore under LIFESPAN_CONTEXT_KEY. Until then, calls pass through
    uncached.
    """

    _inner: ResponseCachingMiddleware | None

    def __init__(self, ttl_seconds: int) -> None:
        self._ttl = ttl_seconds
        self._inner = None

    def _get_inner(self, context: MiddlewareContext) -> ResponseCachingMiddleware | None:
        if self._inner is not None:
            return self._inner
        if context.fastmcp_context is None:
            return None
        store: AsyncKeyValue | None = context.fastmcp_context.lifespan_context.get("_cache_store")
        if store is None:
            return None
        self._inner = ResponseCachingMiddleware(
            cache_storage=store,
            call_tool_settings={"ttl": self._ttl},
        )
        return self._inner

    @override
    async def on_call_tool(
        self,
        context: MiddlewareContext[mcp.types.CallToolRequestParams],
        call_next: CallNext[mcp.types.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        inner = self._get_inner(context)
        if inner is None:
            return await call_next(context)
        return await inner.on_call_tool(context, call_next)
