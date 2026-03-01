import pytest
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport


@pytest.mark.asyncio
async def test_tools(mcp_client: Client[FastMCPTransport]):
    tools = await mcp_client.list_tools()
    assert len(tools) > 1


@pytest.mark.asyncio
async def test_get_firm(mcp_client: Client[FastMCPTransport]):
    tool_result = await mcp_client.call_tool(
        name="get_firm",
        arguments={
            "frn": "482551",
        },
    )
    assert tool_result is not None
    assert "Barclays Capital" in str(tool_result.data)
    assert "482551" in str(tool_result.data)


@pytest.mark.asyncio
async def test_get_firm_names(mcp_client: Client[FastMCPTransport]):
    tool_result = await mcp_client.call_tool(
        name="get_firm_names",
        arguments={
            "frn": "759676",
        },
    )
    assert tool_result is not None
