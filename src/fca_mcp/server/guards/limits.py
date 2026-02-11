"""Guards for rate limiting, timeouts, and data limits."""

import asyncio
import time
from collections import defaultdict
from typing import Any


class RateLimitGuard:
    """Rate limiting guard."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    def check_limit(self, client_id: str) -> tuple[bool, str]:
        """Check if client is within rate limit.

        Args:
            client_id: Client identifier

        Returns:
            Tuple of (allowed, message)
        """
        now = time.time()
        cutoff = now - self.window_seconds

        self.requests[client_id] = [ts for ts in self.requests[client_id] if ts > cutoff]

        if len(self.requests[client_id]) >= self.max_requests:
            return False, f"Rate limit exceeded: {self.max_requests} requests per {self.window_seconds}s"

        self.requests[client_id].append(now)
        return True, "OK"


class TimeoutGuard:
    """Timeout guard for long-running operations."""

    def __init__(self, default_timeout: float = 30.0):
        """Initialize timeout guard.

        Args:
            default_timeout: Default timeout in seconds
        """
        self.default_timeout = default_timeout

    async def execute_with_timeout(
        self,
        coro: Any,
        timeout: float | None = None,
    ) -> tuple[Any, bool]:
        """Execute coroutine with timeout.

        Args:
            coro: Coroutine to execute
            timeout: Timeout override

        Returns:
            Tuple of (result, timed_out)
        """
        effective_timeout = timeout if timeout is not None else self.default_timeout

        try:
            result = await asyncio.wait_for(coro, timeout=effective_timeout)
            return result, False
        except asyncio.TimeoutError:
            return None, True


class DataSizeGuard:
    """Guard for limiting response data size."""

    def __init__(self, max_items: int = 2000):
        """Initialize data size guard.

        Args:
            max_items: Maximum items to allow
        """
        self.max_items = max_items

    def check_size(self, items: list[Any]) -> tuple[list[Any], bool]:
        """Check and enforce size limit.

        Args:
            items: List of items

        Returns:
            Tuple of (limited_items, was_truncated)
        """
        if len(items) > self.max_items:
            return items[: self.max_items], True
        return items, False
