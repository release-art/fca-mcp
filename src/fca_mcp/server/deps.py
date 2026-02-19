"""Fca-api dependencies"""

from __future__ import annotations

import logging

import fastmcp
from fastmcp.dependencies import CurrentContext, Depends

import fca_mcp

from . import types

logger = logging.getLogger(__name__)


def get_fca_app(ctx: fastmcp.Context = CurrentContext()) -> fca_mcp.types.FcaApp:
    return ctx.lifespan_context["fca_app"]


def get_fca_api(fca_app=Depends(get_fca_app)) -> types.CleanFirmDetails:
    return fca_app.fca_api


FcaApiDep = Depends(get_fca_api)
