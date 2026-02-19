from __future__ import annotations

"""Pagination orchestrator for multi-page endpoints."""

import asyncio
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class PaginationMode:
    """Pagination mode constants."""

    PREVIEW = "preview"
    FULL = "full"


class PaginationOrchestrator:
    """Orchestrates pagination for slow multi-page endpoints."""

    def __init__(
        self,
        max_items: int = 1000,
        preview_items: int = 50,
        timeout_seconds: float = 60.0,
    ):
        """Initialize pagination orchestrator.

        Args:
            max_items: Hard limit on total items
            preview_items: Items to return in preview mode
            timeout_seconds: Maximum time for pagination
        """
        self.max_items = max_items
        self.preview_items = preview_items
        self.timeout_seconds = timeout_seconds

    async def paginate(
        self,
        fetch_func: Callable[[], Any],
        mode: str = PaginationMode.PREVIEW,
        max_items: int | None = None,
    ) -> tuple[list[Any], int, bool]:
        """Execute pagination with mode and limits.

        Args:
            fetch_func: Async function that returns iterable/async iterable
            mode: PaginationMode.PREVIEW or PaginationMode.FULL
            max_items: Override default max_items

        Returns:
            Tuple of (items, pages_loaded, truncated)
        """
        effective_max = max_items if max_items is not None else self.max_items
        limit = self.preview_items if mode == PaginationMode.PREVIEW else effective_max

        items = []
        pages_loaded = 0
        truncated = False

        try:
            result = await asyncio.wait_for(fetch_func(), timeout=self.timeout_seconds)

            if hasattr(result, "__aiter__"):
                async for item in result:
                    items.append(item)
                    if len(items) >= limit:
                        truncated = True
                        break
                pages_loaded = 1
            elif hasattr(result, "__iter__"):
                for item in result:
                    items.append(item)
                    if len(items) >= limit:
                        truncated = True
                        break
                pages_loaded = 1
            else:
                items = [result] if result else []
                pages_loaded = 1

        except asyncio.TimeoutError:
            truncated = True

        return items, pages_loaded, truncated

    async def paginate_manual(
        self,
        fetch_page_func: Callable[[int], Any],
        start_page: int = 1,
        mode: str = PaginationMode.PREVIEW,
        max_items: int | None = None,
    ) -> tuple[list[Any], int, bool]:
        """Manual pagination with page-by-page control.

        Args:
            fetch_page_func: Function that takes page number and returns items
            start_page: Starting page number
            mode: PaginationMode.PREVIEW or PaginationMode.FULL
            max_items: Override default max_items

        Returns:
            Tuple of (items, pages_loaded, truncated)
        """
        effective_max = max_items if max_items is not None else self.max_items
        limit = self.preview_items if mode == PaginationMode.PREVIEW else effective_max

        items = []
        page = start_page
        pages_loaded = 0
        truncated = False

        try:
            while len(items) < limit:
                page_items = await asyncio.wait_for(
                    fetch_page_func(page),
                    timeout=self.timeout_seconds,
                )

                if not page_items:
                    break

                items.extend(page_items)
                pages_loaded += 1
                page += 1

                if len(items) >= limit:
                    items = items[:limit]
                    truncated = True
                    break

        except asyncio.TimeoutError:
            truncated = True

        return items, pages_loaded, truncated
