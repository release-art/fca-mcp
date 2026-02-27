import fca_api
import pytest
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport


@pytest.mark.asyncio
async def test_tools(mcp_client: Client[FastMCPTransport]):
    tools = await mcp_client.list_tools()
    assert len(tools) > 1


# @pytest.mark.asyncio
# async def test_get_firm(mock_fca_api, resources_dir, mcp_client: Client[FastMCPTransport]):
#     with (resources_dir / "get_firm.json").open() as f:
#         txt = f.read()
#         assert isinstance(txt, str)
#         print(repr(txt))
#         mock_fca_api.get_firm.return_value = fca_api.types.firm.FirmDetails.model_validate_json(txt)
#     search_results = await mcp_client.call_tool(
#         name="get_firm",
#         arguments={
#             "frn": "123456",
#         },
#     )
#     assert len(search_results.items) == 1
#     firm = search_results.items[0]
#     assert firm.frn is not None
#     details = await mcp_client.get_firm(firm.frn)
#     assert details.frn == firm.frn
