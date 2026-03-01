import pathlib

import fca_api
import pytest
import pytest_asyncio
from fastmcp.client import Client

import fca_mcp


@pytest.fixture
def resources_dir() -> pathlib.Path:
    out = pathlib.Path(__file__).parent / "resources"
    assert out.is_dir(), f"Resources directory not found at {out}"
    return out.resolve()


@pytest.fixture(autouse=True)
def original_client_cls():
    """Original Client class."""
    return fca_api.async_api.Client


@pytest.fixture(autouse=True)
def mock_fca_api(mocker, original_client_cls, caching_mock_api):
    mock_client = caching_mock_api(
        api_implementation=original_client_cls(("developer@release.art", "1853090975e4fbb76d8811a8853971c2")),
    )
    mocker.patch("fca_api.async_api.Client", return_value=mock_client)
    return mock_client


@pytest.fixture
def mcp_app():
    return fca_mcp.server.get_server()


@pytest_asyncio.fixture
async def mcp_client(mcp_app):
    async with Client(transport=mcp_app) as mcp_client:
        yield mcp_client
