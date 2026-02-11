"""Main MCP server implementation."""

import logging
import os
import time
from typing import Any

from pydantic import ValidationError

from fca_mcp.adapters.fca_async_adapter import FcaApiAdapter
from fca_mcp.server.cache.memory import InMemoryCache
from fca_mcp.server.guards.limits import DataSizeGuard, RateLimitGuard, TimeoutGuard
from fca_mcp.server.oauth.middleware import OAuthMiddleware, OAuthRegistry
from fca_mcp.server.pagination.orchestrator import PaginationOrchestrator
from fca_mcp.server.tools.handlers import FirmGetParams, FirmRelatedParams, McpTools, SearchFirmsParams
from fca_mcp.server.tracking.tracker import UsageTracker

logger = logging.getLogger(__name__)


class McpServer:
    """MCP server for FCA Register API."""

    def __init__(
        self,
        fca_credentials: tuple[str, str],
        enable_auth: bool = True,
        enable_rate_limiting: bool = True,
    ):
        """Initialize MCP server.

        Args:
            fca_credentials: FCA API credentials (email, key)
            enable_auth: Enable OAuth authentication
            enable_rate_limiting: Enable rate limiting
        """
        self.fca_credentials = fca_credentials

        self.oauth_registry = OAuthRegistry()
        self.oauth_middleware = OAuthMiddleware(self.oauth_registry)
        self.usage_tracker = UsageTracker()

        self.rate_limiter = RateLimitGuard(max_requests=100, window_seconds=60)
        self.timeout_guard = TimeoutGuard(default_timeout=30.0)
        self.data_guard = DataSizeGuard(max_items=1000)

        self.cache = InMemoryCache(default_ttl=300)
        self.paginator = PaginationOrchestrator(max_items=200, preview_items=10)

        self.adapter: FcaApiAdapter | None = None
        self.tools: McpTools | None = None

        self.enable_auth = enable_auth
        self.enable_rate_limiting = enable_rate_limiting

    async def __aenter__(self):
        """Enter async context manager."""
        self.adapter = FcaApiAdapter(self.fca_credentials)
        await self.adapter.__aenter__()

        self.tools = McpTools(
            adapter=self.adapter,
            cache=self.cache,
            paginator=self.paginator,
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        if self.adapter:
            await self.adapter.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self):
        """Close the server and cleanup resources."""
        await self.__aexit__(None, None, None)

    def register_client(
        self,
        client_id: str,
        client_secret: str,
        scopes: list[str] | None = None,
    ) -> dict[str, Any]:
        """Register OAuth client.

        Args:
            client_id: Client identifier
            client_secret: Client secret
            scopes: Allowed scopes

        Returns:
            Client details
        """
        client = self.oauth_registry.register_client(client_id, client_secret, scopes)
        return {"client_id": client.client_id, "scopes": client.scopes}

    def create_token(self, client_id: str, client_secret: str) -> dict[str, Any] | None:
        """Create access token.

        Args:
            client_id: Client identifier
            client_secret: Client secret

        Returns:
            Token details or None
        """
        token = self.oauth_registry.create_token(client_id, client_secret)
        if not token:
            return None

        return {
            "access_token": token.token,
            "token_type": "Bearer",
            "expires_at": token.expires_at.isoformat(),
            "scopes": token.scopes,
        }

    async def handle_request(
        self,
        tool: str,
        params: dict[str, Any],
        authorization: str | None = None,
    ) -> dict[str, Any]:
        """Handle MCP tool request.

        Args:
            tool: Tool name
            params: Tool parameters
            authorization: Authorization header

        Returns:
            Tool response
        """
        start_time = time.time()

        if self.enable_auth:
            success, message, token = await self.oauth_middleware.authenticate(authorization)
            if not success:
                return {"error": message, "code": "AUTH_FAILED"}
            client_id = token.client_id if token else "unknown"
        else:
            client_id = "anonymous"

        if self.enable_rate_limiting:
            allowed, message = self.rate_limiter.check_limit(client_id)
            if not allowed:
                self.usage_tracker.record_event(
                    client_id=client_id,
                    tool=tool,
                    items_returned=0,
                    latency_ms=(time.time() - start_time) * 1000,
                    error=message,
                )
                return {"error": message, "code": "RATE_LIMIT_EXCEEDED"}

        try:
            if tool == "search_firms":
                validated_params = SearchFirmsParams(**params)
                result, timed_out = await self.timeout_guard.execute_with_timeout(
                    self.tools.search_firms(validated_params)
                )

                if timed_out:
                    raise TimeoutError("Request timed out")

            elif tool == "firm_get":
                validated_params = FirmGetParams(**params)
                result, timed_out = await self.timeout_guard.execute_with_timeout(self.tools.firm_get(validated_params))

                if timed_out:
                    raise TimeoutError("Request timed out")

            elif tool == "firm_related":
                validated_params = FirmRelatedParams(**params)
                result, timed_out = await self.timeout_guard.execute_with_timeout(
                    self.tools.firm_related(validated_params)
                )

                if timed_out:
                    raise TimeoutError("Request timed out")

            else:
                return {"error": f"Unknown tool: {tool}", "code": "UNKNOWN_TOOL"}

            latency_ms = (time.time() - start_time) * 1000

            items_returned = result.get("meta", {}).get("items_returned", 0) if isinstance(result, dict) else 0
            truncated = result.get("meta", {}).get("truncated", False) if isinstance(result, dict) else False

            self.usage_tracker.record_event(
                client_id=client_id,
                tool=tool,
                items_returned=items_returned,
                latency_ms=latency_ms,
                truncated=truncated,
            )

            return result

        except ValidationError as e:
            error_msg = f"Invalid parameters: {str(e)}"
            self.usage_tracker.record_event(
                client_id=client_id,
                tool=tool,
                items_returned=0,
                latency_ms=(time.time() - start_time) * 1000,
                error=error_msg,
            )
            return {"error": error_msg, "code": "INVALID_PARAMS"}

        except TimeoutError as e:
            error_msg = str(e)
            self.usage_tracker.record_event(
                client_id=client_id,
                tool=tool,
                items_returned=0,
                latency_ms=(time.time() - start_time) * 1000,
                error=error_msg,
            )
            return {"error": error_msg, "code": "TIMEOUT"}

        except Exception as e:
            error_msg = f"Internal error: {str(e)}"
            self.usage_tracker.record_event(
                client_id=client_id,
                tool=tool,
                items_returned=0,
                latency_ms=(time.time() - start_time) * 1000,
                error=error_msg,
            )
            return {"error": error_msg, "code": "INTERNAL_ERROR"}

    def get_usage_stats(self, client_id: str | None = None) -> dict[str, Any]:
        """Get usage statistics.

        Args:
            client_id: Filter by client

        Returns:
            Usage statistics
        """
        return self.usage_tracker.get_stats(client_id)


async def create_server(
    fca_email: str | None = None,
    fca_key: str | None = None,
    enable_auth: bool = True,
) -> McpServer:
    """Create and initialize MCP server.

    Args:
        fca_email: FCA API email
        fca_key: FCA API key
        enable_auth: Enable OAuth

    Returns:
        Initialized server
    """
    email = fca_email or os.getenv("FCA_API_USERNAME")
    key = fca_key or os.getenv("FCA_API_KEY")

    if not email or not key:
        raise ValueError("FCA API credentials required")

    server = McpServer(
        fca_credentials=(email, key),
        enable_auth=enable_auth,
    )

    await server.__aenter__()
    return server
