"""Tests for raw API validation and edge cases to achieve 100% coverage."""

import pytest
import httpx
from fca_api import raw_api, exc


class TestRawClientValidation:
    """Test RawClient initialization validation."""

    def test_invalid_credentials_type(self):
        """Test that invalid credentials type raises ValueError."""
        with pytest.raises(ValueError, match="credentials must be either"):
            raw_api.RawClient(credentials="invalid_string_type")

    def test_invalid_credentials_tuple_length(self):
        """Test that tuple with wrong length raises ValueError."""
        with pytest.raises(ValueError, match="credentials must be either"):
            raw_api.RawClient(credentials=("only_one_element",))


class TestCommonSearchValidation:
    """Test common_search method validation."""

    @pytest.mark.asyncio
    async def test_empty_resource_name(self, mocker):
        """Test that empty resource name raises ValueError."""
        mock_session = mocker.create_autospec(httpx.AsyncClient)
        client = raw_api.RawClient(credentials=mock_session)

        with pytest.raises(ValueError, match="Resource name must be a non-empty string"):
            await client.common_search("", "firm")

    @pytest.mark.asyncio
    async def test_empty_resource_type(self, mocker):
        """Test that empty resource type raises ValueError."""
        mock_session = mocker.create_autospec(httpx.AsyncClient)
        client = raw_api.RawClient(credentials=mock_session)

        with pytest.raises(ValueError, match="Resource type must be a non-empty string"):
            await client.common_search("test", "")


class TestGetResourceInfoValidation:
    """Test _get_resource_info method validation."""

    @pytest.mark.asyncio
    async def test_invalid_resource_type(self, mocker):
        """Test that invalid resource type raises ValueError."""
        mock_session = mocker.create_autospec(httpx.AsyncClient)
        client = raw_api.RawClient(credentials=mock_session)

        with pytest.raises(ValueError, match="Resource type must be one of"):
            await client._get_resource_info("invalid_type", "123456")
