"""
FCA MCP Server with AI Analysis - Complete Production System.

This is the unified server combining MCP protocol, AI analysis, and LLM integration.
Run this single file to access all FCA regulatory data analysis features.
"""

from __future__ import annotations

import logging

import typer
import uvicorn

import fca_mcp

logger = logging.getLogger(__name__)

app = typer.Typer(pretty_exceptions_enable=False)


@app.callback(invoke_without_command=True)
def startup(ctx: typer.Context):
    """Startup callback that runs before any command."""
    fca_mcp.logging.configure()
    logger.info("Fca Mcp CLI started.")


@app.command()
def serve(host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
    """Run HTTP server mode (synchronous entry point)."""
    logger.info("[HTTP] Starting server on %s:%s", host, port)
    logger.info(
        "[HTTP] Web UI: http://%s:%s",
        host,
        port,
    )
    logger.info(
        "[HTTP] API Docs: http://%s:%s/docs",
        host,
        port,
    )

    # uvicorn.run manages its own event loop
    uvicorn.run(
        "fca_mcp.uvcorn_app:get_fastapi_app",
        host=host,
        port=port,
        log_config=fca_mcp.logging.get_config(),
        factory=True,
        reload=reload,
    )


@app.command()
def stdio() -> None:
    """Run stdio mode (asynchronous entry point)."""
    mcp = fca_mcp.server.get_server()
    mcp.run()


if __name__ == "__main__":
    app()
