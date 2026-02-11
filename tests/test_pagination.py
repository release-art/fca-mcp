"""Tests for pagination orchestrator."""

import asyncio

import pytest

from fca_mcp.server.pagination.orchestrator import PaginationMode, PaginationOrchestrator


@pytest.fixture
def paginator():
    """Create paginator instance."""
    return PaginationOrchestrator(max_items=100, preview_items=5)


async def async_generator(items):
    """Create async generator."""
    for item in items:
        yield item


@pytest.mark.asyncio
async def test_paginate_preview_mode(paginator):
    """Test preview mode pagination."""
    items = list(range(20))

    async def fetch():
        return async_generator(items)

    result, pages, truncated = await paginator.paginate(fetch, mode=PaginationMode.PREVIEW)

    assert len(result) == 5
    assert pages == 1
    assert truncated is True


@pytest.mark.asyncio
async def test_paginate_full_mode(paginator):
    """Test full mode pagination."""
    items = list(range(20))

    async def fetch():
        return async_generator(items)

    result, pages, truncated = await paginator.paginate(fetch, mode=PaginationMode.FULL)

    assert len(result) == 20
    assert pages == 1
    assert truncated is False


@pytest.mark.asyncio
async def test_paginate_with_max_items(paginator):
    """Test pagination with max items limit."""
    items = list(range(200))

    async def fetch():
        return async_generator(items)

    result, pages, truncated = await paginator.paginate(fetch, mode=PaginationMode.FULL, max_items=50)

    assert len(result) == 50
    assert truncated is True


@pytest.mark.asyncio
async def test_paginate_timeout(paginator):
    """Test pagination timeout."""

    async def fetch():
        await asyncio.sleep(100)
        return []

    paginator.timeout_seconds = 0.1

    result, pages, truncated = await paginator.paginate(fetch)

    assert len(result) == 0
    assert truncated is True
