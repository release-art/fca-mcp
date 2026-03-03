"""FastMCP authentication module."""

from __future__ import annotations

from fastmcp.server.auth import AuthProvider
from fastmcp.server.auth.providers.auth0 import Auth0Provider

import fca_mcp.settings


def get_auth_provider() -> AuthProvider:
    """Get the Auth0 authentication provider."""
    settings = fca_mcp.settings.get_settings()
    return Auth0Provider(
        audience=settings.auth0.audience,
        client_id=settings.auth0.client_id,
        client_secret=settings.auth0.client_secret,
        base_url=settings.get_base_url(),
        config_url=f"{settings.get_base_url()}/.well-known/openid-configuration",
    )
