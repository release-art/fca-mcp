"""Search firms"""
from __future__ import annotations

import fastmcp

firms_mcp = fastmcp.FastMCP('search-firms')

@firms_mcp.tool
async def search_frn(firm_name: str) -> str:
    return "Hello {firm_name}!"

def get_server() -> fastmcp.FastMCP:
    return firms_mcp