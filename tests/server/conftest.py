import pytest
import pytest_asyncio
from fastmcp.client import Client

import fca_mcp
import fca_api
import pathlib


@pytest.fixture
def resources_dir() -> pathlib.Path:
    out = pathlib.Path(__file__).parent / "resources"
    assert out.is_dir(), f"Resources directory not found at {out}"
    return out.resolve()


@pytest.fixture(autouse=True)
def mock_fca_api(mocker):
    mock_client = mocker.AsyncMock(spec=fca_api.async_api.Client)
    # Set up mock methods as needed, e.g.:
    # mock_client.search_frn.return_value = ...
    mocker.patch("fca_api.async_api.Client", return_value=mock_client)
    return mock_client


@pytest.fixture
def mcp_app():
    return fca_mcp.server.get_server()


@pytest_asyncio.fixture
async def mcp_client(mcp_app):
    async with Client(transport=mcp_app) as mcp_client:
        yield mcp_client
