"""In-memory cache layer."""

import time
from typing import Any


class CacheEntry:
    """Cache entry with TTL."""

    def __init__(self, value: Any, ttl_seconds: int = 300):
        """Initialize cache entry.

        Args:
            value: Cached value
            ttl_seconds: Time-to-live in seconds
        """
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        return time.time() - self.created_at > self.ttl_seconds


class InMemoryCache:
    """Simple in-memory cache with TTL."""

    def __init__(self, default_ttl: int = 300):
        """Initialize cache.

        Args:
            default_ttl: Default TTL in seconds
        """
        self.default_ttl = default_ttl
        self.cache: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        entry = self.cache.get(key)
        if not entry:
            return None

        if entry.is_expired():
            del self.cache[key]
            return None

        return entry.value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL override
        """
        effective_ttl = ttl if ttl is not None else self.default_ttl
        self.cache[key] = CacheEntry(value, effective_ttl)

    def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()

    def cleanup_expired(self) -> int:
        """Remove expired entries.

        Returns:
            Number of entries removed
        """
        expired = [key for key, entry in self.cache.items() if entry.is_expired()]
        for key in expired:
            del self.cache[key]
        return len(expired)

    def make_key(self, *args: Any) -> str:
        """Create cache key from arguments.

        Args:
            args: Key components

        Returns:
            Cache key string
        """
        return ":".join(str(arg) for arg in args)
