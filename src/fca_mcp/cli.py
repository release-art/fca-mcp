from __future__ import annotations

"""
FCA MCP Server with AI Analysis - Complete Production System.

This is the unified server combining MCP protocol, AI analysis, and LLM integration.
Run this single file to access all FCA regulatory data analysis features.
"""

import asyncio
import logging
import signal

import typer
import uvicorn

import fca_mcp

logger = logging.getLogger(__name__)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
app = typer.Typer(pretty_exceptions_enable=False)


@app.callback(invoke_without_command=True)
def startup(ctx: typer.Context):
    """Startup callback that runs before any command."""
    fca_mcp.logging.configure()
    logger.info("Fca Mcp CLI started.")


@app.command()
def main_http_mode(host: str = "0.0.0.0", port: int = 8000) -> None:
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
    uvicorn.run("fca_mcp.uvcorn_app:get_fastapi_app", host=host, port=port, log_level="info", factory=True)


@app.command()
def main(interactive: bool = True, enable_auth: bool = True) -> None:
    """Main entry point for the FCA MCP Server (CLI mode only)."""
    # parser = argparse.ArgumentParser(
    #     description="FCA MCP Server with AI Analysis",
    #     formatter_class=argparse.RawDescriptionHelpFormatter,
    #     epilog=textwrap.dedent("""
    #         Examples:
    #         python fca_mcp_server.py                    # Interactive mode
    #         python fca_mcp_server.py --no-interactive   # Non-interactive mode
    #         python fca_mcp_server.py --http-mode        # HTTP server mode
    #         python fca_mcp_server.py --enable-auth      # With OAuth authentication

    #         Interactive commands:
    #         search Barclays                             # Search for firms
    #         firm 122702                                 # Get firm details
    #         analyze Barclays Bank                       # AI risk analysis
    #         compare Barclays vs HSBC                    # Compare firms
    #         ask What is the risk of Barclays?          # Natural language query

    #         HTTP endpoints:
    #         GET  /                                       # Web UI
    #         GET  /health                                 # Health check
    #         POST /api/search                             # Search firms
    #         POST /api/analyze                            # Analyze firm
    #         POST /api/compare                            # Compare firms
    #         POST /api/ask                                # Natural language query
    #     """),
    # )
    # args = parser.parse_args()

    # CLI mode only
    runner = fca_mcp.server_runner.FcaMcpServerRunner()

    def signal_handler(sig, frame):
        runner.shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    asyncio.run(runner.run(interactive=interactive, enable_auth=enable_auth))


if __name__ == "__main__":
    app()
