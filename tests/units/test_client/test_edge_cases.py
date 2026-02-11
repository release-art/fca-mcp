"""Tests for edge cases and error handling to achieve 100% coverage."""

import pytest
import httpx
import fca_api
from fca_api import raw_api, types, exc


class TestClientProperties:
    """Test client properties."""

    @pytest.mark.asyncio
    async def test_raw_client_property(self, test_client: fca_api.async_api.Client):
        """Test accessing the raw_client property."""
        raw_client = test_client.raw_client
        assert isinstance(raw_client, raw_api.RawClient)
        assert raw_client is test_client._client

    @pytest.mark.asyncio
    async def test_api_version_property(self, test_client: fca_api.async_api.Client):
        """Test accessing the api_version property."""
        api_version = test_client.api_version
        assert isinstance(api_version, str)
        assert api_version  # Not empty


class TestContextManager:
    """Test async context manager behavior."""

    @pytest.mark.asyncio
    async def test_context_manager_entry_exit(
        self, test_api_username, test_api_key, caching_session_subclass, test_resources_path
    ):
        """Test __aenter__ and __aexit__."""
        async with caching_session_subclass(
            headers={"X-AUTH-EMAIL": test_api_username, "X-AUTH-KEY": test_api_key},
            cache_dir=test_resources_path / "test_context_manager",
            cache_mode="fetch_missing",
        ) as api_session:
            async with fca_api.async_api.Client(credentials=api_session) as client:
                # Should be able to use client inside context
                assert client is not None
                assert client.api_version
            # After exit, session should be closed (checked implicitly)

