from __future__ import annotations

"""Usage tracking and metrics."""

import logging
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class UsageEvent(BaseModel):
    """Usage event record."""

    client_id: str = Field(..., description="Client that made the request")
    tool: str = Field(..., description="Tool that was invoked")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    items_returned: int = Field(..., description="Number of items returned")
    latency_ms: float = Field(..., description="Request latency in milliseconds")
    truncated: bool = Field(default=False, description="Whether response was truncated")
    error: str | None = Field(None, description="Error message if failed")


class UsageTracker:
    """Tracks usage events and metrics."""

    def __init__(self):
        """Initialize tracker."""
        self.events: list[UsageEvent] = []

    def record_event(
        self,
        client_id: str,
        tool: str,
        items_returned: int,
        latency_ms: float,
        truncated: bool = False,
        error: str | None = None,
    ) -> UsageEvent:
        """Record usage event.

        Args:
            client_id: Client identifier
            tool: Tool name
            items_returned: Items returned
            latency_ms: Latency in milliseconds
            truncated: Whether truncated
            error: Error message

        Returns:
            Recorded event
        """
        event = UsageEvent(
            client_id=client_id,
            tool=tool,
            items_returned=items_returned,
            latency_ms=latency_ms,
            truncated=truncated,
            error=error,
        )
        self.events.append(event)
        return event

    def get_events(
        self,
        client_id: str | None = None,
        tool: str | None = None,
        limit: int = 100,
    ) -> list[UsageEvent]:
        """Get usage events.

        Args:
            client_id: Filter by client
            tool: Filter by tool
            limit: Maximum events to return

        Returns:
            List of events
        """
        filtered = self.events

        if client_id:
            filtered = [e for e in filtered if e.client_id == client_id]

        if tool:
            filtered = [e for e in filtered if e.tool == tool]

        return filtered[-limit:]

    def get_stats(self, client_id: str | None = None) -> dict[str, Any]:
        """Get usage statistics.

        Args:
            client_id: Filter by client

        Returns:
            Statistics dictionary
        """
        events = self.events if not client_id else [e for e in self.events if e.client_id == client_id]

        if not events:
            return {"total_requests": 0}

        total_requests = len(events)
        total_items = sum(e.items_returned for e in events)
        avg_latency = sum(e.latency_ms for e in events) / total_requests
        error_rate = sum(1 for e in events if e.error) / total_requests

        tool_counts = {}
        for event in events:
            tool_counts[event.tool] = tool_counts.get(event.tool, 0) + 1

        return {
            "total_requests": total_requests,
            "total_items": total_items,
            "avg_latency_ms": avg_latency,
            "error_rate": error_rate,
            "tool_usage": tool_counts,
        }
