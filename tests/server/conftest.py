import pytest
import pytest_asyncio
from fastmcp.client import Client

import fca_mcp


@pytest.fixture
def mcp_app():
    return fca_mcp.server.get_server()


@pytest_asyncio.fixture
async def mcp_client(mcp_app):
    async with Client(transport=mcp_app) as mcp_client:
        yield mcp_client
