"""Fca-api dependencies"""

import logging
import typing
import weakref

import fastmcp
import fca_api
from fastmcp.dependencies import Depends

logger = logging.getLogger(__name__)
main_mcp_server: typing.Optional[weakref.ReferenceType[fastmcp.FastMCP]] = None


def get_fca_api() -> fca_api.async_api.Client:
    if not main_mcp_server:
        raise RuntimeError("FCA API client dependency accessed before server startup")
    server = main_mcp_server()
    logger.debug(f"Getting FCA API client from server {server}")
    return server.my_app_ctx.fca_api


FcaApiDep = Depends(get_fca_api)
