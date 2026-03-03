from __future__ import annotations

import dataclasses
import typing

import fastapi
import fastmcp.server
import fastmcp.server.http


@dataclasses.dataclass(slots=True)
class FcaMcpApp:
    fastmcp_server: fastmcp.server.FastMCP
    fastmcp_http_app: fastmcp.server.http.StarletteWithLifespan


async def get_fca_mcp_app(request: fastapi.Request) -> FcaMcpApp:
    return request.app.my_app_ctx


FcaMcpAppT = typing.Annotated[FcaMcpApp, fastapi.Depends(get_fca_mcp_app)]
