"""Tests for AzureAPI client factory."""

from __future__ import annotations

import pytest

import fca_mcp.settings as settings_mod
from fca_mcp.azure.api import AzureAPI


def test_none_credential_builds_from_connection_string():
    s = settings_mod.AzureSettings(
        credential="none",
        storage_connection_string=(
            "DefaultEndpointsProtocol=https;AccountName=a;AccountKey=dGVzdA==;EndpointSuffix=core.windows.net"
        ),
    )
    api = AzureAPI(s)
    assert api.blob_service_client is not None
    assert api.queue_service_client is not None
    assert api.table_service_client is not None


def test_none_credential_without_connection_string_raises():
    s = settings_mod.AzureSettings(credential="none", storage_connection_string=None)
    with pytest.raises(ValueError, match="storage_connection_string is required"):
        AzureAPI(s)


def test_default_credential_builds_from_account(mocker):
    mocker.patch("fca_mcp.azure.api.DefaultAzureCredential")
    s = settings_mod.AzureSettings(credential="default", storage_account="myacct")
    api = AzureAPI(s)
    assert api.blob_service_client is not None


def test_default_credential_without_account_raises():
    s = settings_mod.AzureSettings(credential="default", storage_account=None)
    with pytest.raises(ValueError, match="storage_account is required"):
        AzureAPI(s)


def test_default_credential_uses_explicit_endpoints(mocker):
    mocker.patch("fca_mcp.azure.api.DefaultAzureCredential")
    s = settings_mod.AzureSettings(
        credential="default",
        storage_account="myacct",
        storage_blob_endpoint="https://blob.example.com",
        storage_queue_endpoint="https://queue.example.com",
        storage_table_endpoint="https://table.example.com",
    )
    api = AzureAPI(s)
    assert api.blob_service_client is not None


@pytest.mark.anyio
async def test_get_helpers(mocker):
    s = settings_mod.AzureSettings(
        credential="none",
        storage_connection_string=(
            "DefaultEndpointsProtocol=https;AccountName=a;AccountKey=dGVzdA==;EndpointSuffix=core.windows.net"
        ),
    )
    api = AzureAPI(s)
    assert await api.get_queue("q") is not None
    assert await api.get_blob_container("c") is not None
    assert api.get_table("t") is not None


@pytest.fixture
def anyio_backend():
    return "asyncio"
