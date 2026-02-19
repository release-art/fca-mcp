from __future__ import annotations

import dataclasses
import typing

import fastapi

import fca_mcp


@dataclasses.dataclass(slots=True)
class FcaApp:
    fca_api_adapter: fca_mcp.adapters.fca_async_adapter.FcaApiAdapter
    tools: fca_mcp.server.tools.handlers.McpTools


async def get_fca_app(request: fastapi.Request) -> FcaApp:
    return request.app.my_app_ctx


FcaAppT = typing.Annotated[FcaApp, fastapi.Depends(get_fca_app)]
