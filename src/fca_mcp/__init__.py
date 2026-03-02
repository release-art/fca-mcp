from __future__ import annotations

"""MCP server for FCA Financial Services Register API.

This package provides a Model Context Protocol (MCP) server that exposes
the FCA Register API to LLM clients through structured tools.
"""

import logging as std_logging

from . import (
    __version__,
    app,
    cli,
    logging as fca_logging,
    server,
    uvcorn_app,
    settings,
)

logger = std_logging.getLogger(__name__)
logging = fca_logging
version = __version__.__version__
