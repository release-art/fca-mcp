from __future__ import annotations

import dataclasses
import typing

import fastapi
import fca_api


@dataclasses.dataclass(slots=True)
class FcaApp:
    fca_api: fca_api.async_api.Client


async def get_fca_app(request: fastapi.Request) -> FcaApp:
    return request.app.my_app_ctx


FcaAppT = typing.Annotated[FcaApp, fastapi.Depends(get_fca_app)]
