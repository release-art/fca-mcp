"""Tests for the Starlette HTTP app: landing page, health, MCP aliases."""

from __future__ import annotations

import httpx
import pytest

import fca_mcp.uvcorn_app


@pytest.fixture
def http_app(mock_auth_components, mock_azure_cache):
    return fca_mcp.uvcorn_app.get_http_app()


@pytest.mark.anyio
async def test_landing_html(http_app):
    transport = httpx.ASGITransport(app=http_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        async with http_app.router.lifespan_context(http_app):
            resp = await client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "fca-mcp" in resp.text
    assert fca_mcp.__version__.__version__ in resp.text


@pytest.mark.anyio
async def test_health(http_app):
    transport = httpx.ASGITransport(app=http_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        async with http_app.router.lifespan_context(http_app):
            resp = await client.get("/.container/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["service"] == "FCA MCP Server"
    assert body["version"] == fca_mcp.__version__.__version__


def test_mcp_alias_installed(http_app):
    from starlette.routing import Route

    paths = {r.path for r in http_app.routes if isinstance(r, Route)}
    assert "/" in paths
    assert "/mcp" in paths


def test_mcp_alias_shares_endpoint(http_app):
    from starlette.routing import Route

    canonical = next(
        r for r in http_app.routes if isinstance(r, Route) and r.path == "/" and "POST" in (r.methods or set())
    )
    alias = next(r for r in http_app.routes if isinstance(r, Route) and r.path == "/mcp")
    assert alias.endpoint is canonical.endpoint
    assert alias.methods == canonical.methods


@pytest.fixture
def anyio_backend():
    return "asyncio"
