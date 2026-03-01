import fca_api
import pytest
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport


@pytest.mark.asyncio
async def test_tools(mcp_client: Client[FastMCPTransport]):
    tools = await mcp_client.list_tools()
    assert len(tools) > 1


@pytest.mark.asyncio
async def test_get_firm(mock_fca_api, resources_dir, mcp_client: Client[FastMCPTransport]):
    with (resources_dir / "get_firm.json").open() as f:
        txt = f.read()
        assert isinstance(txt, str)
        mock_fca_api.get_firm.return_value = fca_api.types.firm.FirmDetails.model_validate_json(txt)
    tool_result = await mcp_client.call_tool(
        name="get_firm",
        arguments={
            "frn": "482551",
        },
    )
    assert tool_result is not None
    assert "Barclays Capital" in str(tool_result.data)
    assert "482551" in str(tool_result.data)
