"""Tests for TOON formatter."""

import pytest

from fca_mcp.server.toon.formatter import ToonFormatter


@pytest.fixture
def formatter():
    """Create formatter instance."""
    return ToonFormatter()


def test_format_response(formatter):
    """Test basic response formatting."""
    data = {"key": "value"}
    response = formatter.format_response(
        data=data,
        response_type="test.type",
        pages_loaded=1,
        items_returned=1,
        truncated=False,
    )

    assert response.type == "test.type"
    assert response.version == "1.0"
    assert response.data == data
    assert response.meta.pages_loaded == 1
    assert response.meta.items_returned == 1
    assert response.meta.truncated is False


def test_format_search_results(formatter):
    """Test search results formatting."""
    results = [{"firm_id": "123", "name": "Test Firm"}]
    response = formatter.format_search_results(
        results=results,
        total=10,
        truncated=False,
        execution_time_ms=100.5,
    )

    assert response.type == "fca.firm.search"
    assert len(response.data) == 1
    assert response.meta.items_returned == 1
    assert response.meta.total_available == 10
    assert response.meta.execution_time_ms == 100.5


def test_format_firm_details(formatter):
    """Test firm details formatting."""
    firm = {"firm_id": "123", "name": "Test Firm"}
    response = formatter.format_firm_details(firm=firm)

    assert response.type == "fca.firm.details"
    assert response.data == firm
    assert response.meta.items_returned == 1


def test_format_firm_related(formatter):
    """Test firm related data formatting."""
    data = [{"name": "Address 1"}, {"name": "Address 2"}]
    response = formatter.format_firm_related(
        data=data,
        kind="addresses",
        pages_loaded=1,
        truncated=False,
        total_available=2,
    )

    assert response.type == "fca.firm.addresses"
    assert len(response.data) == 2
    assert response.meta.pages_loaded == 1
    assert response.meta.truncated is False
