import pytest
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport


@pytest.mark.asyncio
async def test_get_fund(mcp_client: Client[FastMCPTransport]):
    tool_result = await mcp_client.call_tool(
        name="get_fund",
        arguments={
            "prn": "185045",
        },
    )
    assert tool_result is not None
    assert 'SI000001' in str(tool_result.data)