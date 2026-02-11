"""Tests for usage tracker."""

import pytest

from fca_mcp.server.tracking.tracker import UsageTracker


@pytest.fixture
def tracker():
    """Create usage tracker."""
    return UsageTracker()


def test_record_event(tracker):
    """Test recording usage event."""
    event = tracker.record_event(
        client_id="client1",
        tool="search_firms",
        items_returned=10,
        latency_ms=150.5,
        truncated=False,
    )

    assert event.client_id == "client1"
    assert event.tool == "search_firms"
    assert event.items_returned == 10
    assert event.latency_ms == 150.5
    assert event.truncated is False
    assert event.error is None


def test_get_events_all(tracker):
    """Test getting all events."""
    tracker.record_event("client1", "search_firms", 10, 100.0)
    tracker.record_event("client2", "firm_get", 1, 50.0)

    events = tracker.get_events()
    assert len(events) == 2


def test_get_events_by_client(tracker):
    """Test filtering events by client."""
    tracker.record_event("client1", "search_firms", 10, 100.0)
    tracker.record_event("client2", "firm_get", 1, 50.0)
    tracker.record_event("client1", "firm_related", 5, 75.0)

    events = tracker.get_events(client_id="client1")
    assert len(events) == 2
    assert all(e.client_id == "client1" for e in events)


def test_get_events_by_tool(tracker):
    """Test filtering events by tool."""
    tracker.record_event("client1", "search_firms", 10, 100.0)
    tracker.record_event("client2", "search_firms", 5, 80.0)
    tracker.record_event("client1", "firm_get", 1, 50.0)

    events = tracker.get_events(tool="search_firms")
    assert len(events) == 2
    assert all(e.tool == "search_firms" for e in events)


def test_get_stats(tracker):
    """Test getting statistics."""
    tracker.record_event("client1", "search_firms", 10, 100.0)
    tracker.record_event("client1", "firm_get", 1, 50.0)
    tracker.record_event("client1", "search_firms", 5, 150.0, error="Test error")

    stats = tracker.get_stats(client_id="client1")

    assert stats["total_requests"] == 3
    assert stats["total_items"] == 16
    assert stats["avg_latency_ms"] == 100.0
    assert stats["error_rate"] == pytest.approx(1 / 3)
    assert stats["tool_usage"]["search_firms"] == 2
    assert stats["tool_usage"]["firm_get"] == 1


def test_get_stats_empty(tracker):
    """Test statistics with no events."""
    stats = tracker.get_stats()
    assert stats["total_requests"] == 0
