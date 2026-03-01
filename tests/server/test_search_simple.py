import pytest
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport


@pytest.mark.asyncio
async def test_get_individual(mcp_client: Client[FastMCPTransport]):
    tool_result = await mcp_client.call_tool(
        name="search_frn",
        arguments={
            "firm_name": "Liverpool Victoria",
        },
    )
    assert tool_result is not None
    assert "Bob Keijzers" in str(tool_result.data)
