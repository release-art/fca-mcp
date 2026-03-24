import fastmcp

from . import interactive


def mount_interactive_router(mcp: fastmcp.FastMCP) -> None:
    mcp.custom_route("/interactive/config", methods=["GET"], include_in_schema=False)(interactive.interactive_config)
    mcp.custom_route("/interactive", methods=["GET"], include_in_schema=False)(interactive.interactive_ui)
    # return interactive.interactive_router
