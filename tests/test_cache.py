"""Tests for cache layer."""

import time

import pytest

from fca_mcp.server.cache.memory import InMemoryCache


@pytest.fixture
def cache():
    """Create cache instance."""
    return InMemoryCache(default_ttl=1)


def test_cache_set_get(cache):
    """Test basic cache operations."""
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


def test_cache_get_nonexistent(cache):
    """Test getting nonexistent key."""
    assert cache.get("nonexistent") is None


def test_cache_expiration(cache):
    """Test cache expiration."""
    cache.set("key1", "value1", ttl=1)
    assert cache.get("key1") == "value1"

    time.sleep(1.1)
    assert cache.get("key1") is None


def test_cache_delete(cache):
    """Test cache deletion."""
    cache.set("key1", "value1")
    assert cache.delete("key1") is True
    assert cache.get("key1") is None
    assert cache.delete("key1") is False


def test_cache_clear(cache):
    """Test cache clearing."""
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.clear()

    assert cache.get("key1") is None
    assert cache.get("key2") is None


def test_cache_make_key(cache):
    """Test cache key generation."""
    key = cache.make_key("prefix", "arg1", 123)
    assert key == "prefix:arg1:123"


def test_cache_cleanup_expired(cache):
    """Test cleanup of expired entries."""
    cache.set("key1", "value1", ttl=1)
    cache.set("key2", "value2", ttl=10)

    time.sleep(1.1)

    removed = cache.cleanup_expired()
    assert removed == 1
    assert cache.get("key1") is None
    assert cache.get("key2") == "value2"
