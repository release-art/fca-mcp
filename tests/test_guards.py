from __future__ import annotations

"""Tests for guards."""

import asyncio
import time

import pytest

from fca_mcp.server.guards.limits import DataSizeGuard, RateLimitGuard, TimeoutGuard


@pytest.fixture
def rate_limiter():
    """Create rate limiter."""
    return RateLimitGuard(max_requests=5, window_seconds=1)


@pytest.fixture
def timeout_guard():
    """Create timeout guard."""
    return TimeoutGuard(default_timeout=1.0)


@pytest.fixture
def data_guard():
    """Create data size guard."""
    return DataSizeGuard(max_items=10)


def test_rate_limit_within_limit(rate_limiter):
    """Test rate limiting within limit."""
    for _ in range(5):
        allowed, message = rate_limiter.check_limit("client1")
        assert allowed is True


def test_rate_limit_exceeded(rate_limiter):
    """Test rate limit exceeded."""
    for _ in range(5):
        rate_limiter.check_limit("client1")

    allowed, message = rate_limiter.check_limit("client1")
    assert allowed is False
    assert "Rate limit exceeded" in message


def test_rate_limit_window_reset(rate_limiter):
    """Test rate limit window reset."""
    for _ in range(5):
        rate_limiter.check_limit("client1")

    time.sleep(1.1)

    allowed, message = rate_limiter.check_limit("client1")
    assert allowed is True


@pytest.mark.asyncio
async def test_timeout_guard_success(timeout_guard):
    """Test timeout guard with successful execution."""

    async def quick_task():
        await asyncio.sleep(0.1)
        return "success"

    result, timed_out = await timeout_guard.execute_with_timeout(quick_task())

    assert result == "success"
    assert timed_out is False


@pytest.mark.asyncio
async def test_timeout_guard_timeout(timeout_guard):
    """Test timeout guard with timeout."""

    async def slow_task():
        await asyncio.sleep(2.0)
        return "success"

    result, timed_out = await timeout_guard.execute_with_timeout(slow_task(), timeout=0.1)

    assert result is None
    assert timed_out is True


def test_data_size_guard_within_limit(data_guard):
    """Test data size guard within limit."""
    items = list(range(5))
    result, truncated = data_guard.check_size(items)

    assert len(result) == 5
    assert truncated is False


def test_data_size_guard_exceeds_limit(data_guard):
    """Test data size guard exceeding limit."""
    items = list(range(20))
    result, truncated = data_guard.check_size(items)

    assert len(result) == 10
    assert truncated is True
