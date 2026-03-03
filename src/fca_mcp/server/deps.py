"""Fca-api dependencies"""

from __future__ import annotations

import logging

import fastmcp
import fca_api
from fastmcp.dependencies import CurrentContext, Depends

from . import app

logger = logging.getLogger(__name__)


def get_fca_app(ctx: fastmcp.Context = CurrentContext()) -> app.FcaApp:
    return ctx.lifespan_context["fca_app"]


def get_fca_api(fca_app=Depends(get_fca_app)) -> fca_api.async_api.Client:
    return fca_app.fca_api


FcaApiDep = Depends(get_fca_api)
