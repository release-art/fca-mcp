from __future__ import annotations

"""MCP server for FCA Financial Services Register API.

This package provides a Model Context Protocol (MCP) server that exposes
the FCA Register API to LLM clients through structured tools.
"""

import logging as std_logging

from . import (
    __version__,
    adapters,
    cli,
    fca_ai_assistant,
    logging as fca_logging,
    models,
    nli,
    server,
    server_runner,
    uvcorn_app,
)

logger = std_logging.getLogger(__name__)
logging = fca_logging
version = __version__.__version__
