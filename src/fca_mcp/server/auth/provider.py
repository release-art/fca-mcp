"""FastMCP authentication module."""

from __future__ import annotations

import logging

from fastmcp.server.auth import AuthProvider

import fca_mcp
import fca_mcp.settings

from . import scopes

logger = logging.getLogger(__name__)


def _get_remote_auth_provider() -> AuthProvider:
    """Create a RemoteAuthProvider with JWTVerifier for JWT-only validation."""
    from fastmcp.server.auth import RemoteAuthProvider
    from fastmcp.server.auth.providers.jwt import JWTVerifier
    from pydantic import AnyHttpUrl

    settings = fca_mcp.settings.get_settings()
    domain = settings.auth0.domain

    # NOTE: required_scopes is intentionally omitted here. Scope enforcement
    # is handled per-tool by AuthMiddleware + restrict_tag in server/__init__.py.
    # Setting required_scopes on JWTVerifier would reject tokens globally
    # (even for initialize/tools/list) before the middleware gets a chance to
    # apply per-tool checks.
    jwt_verifier = JWTVerifier(
        jwks_uri=f"https://{domain}/.well-known/jwks.json",
        issuer=f"https://{domain}/",
        audience=settings.auth0.audience,
    )

    return RemoteAuthProvider(
        token_verifier=jwt_verifier,
        authorization_servers=[AnyHttpUrl(f"https://{domain}/")],
        base_url=settings.get_base_url(),
        scopes_supported=[scopes.FCA_API_RO],
        resource_name="FCA Financial Services Register MCP",
    )


def _get_proxy_auth_provider() -> AuthProvider:
    """Create an Auth0Provider (OIDCProxy) for full OAuth proxy mode."""
    from cryptography.fernet import Fernet
    from fastmcp.server.auth.providers.auth0 import Auth0Provider
    from key_value.aio.wrappers.encryption import FernetEncryptionWrapper

    import fca_mcp.azure.api
    import fca_mcp.azure.blob_key_value
    import fca_mcp.azure.storage_container_names

    settings = fca_mcp.settings.get_settings()
    tmp_api = fca_mcp.azure.api.AzureAPI(settings.azure)

    assert settings.auth0.client_id is not None
    assert settings.auth0.client_secret is not None
    assert settings.auth0.jwt_signing_key is not None
    assert settings.auth0.storage_encryption_key is not None

    return Auth0Provider(
        audience=settings.auth0.audience,
        client_id=settings.auth0.client_id,
        client_secret=settings.auth0.client_secret,
        jwt_signing_key=settings.auth0.jwt_signing_key,
        base_url=settings.get_base_url(),
        config_url=f"https://{settings.auth0.domain}/.well-known/openid-configuration",
        required_scopes=[scopes.FCA_API_RO],
        client_storage=FernetEncryptionWrapper(
            key_value=fca_mcp.azure.blob_key_value.AzureBlobStore(
                client=tmp_api.blob_service_client,
                container_name=fca_mcp.azure.storage_container_names.AUTH_CLIENT_STORE,
                default_collection="auth0_clients",
            ),
            fernet=Fernet(settings.auth0.storage_encryption_key),
        ),
    )


def get_auth_provider() -> AuthProvider:
    """Get the authentication provider based on configured auth mode."""
    settings = fca_mcp.settings.get_settings()

    if settings.auth0.mode == fca_mcp.settings.AuthMode.REMOTE:
        logger.info("Using RemoteAuthProvider (JWT verification only)")
        return _get_remote_auth_provider()

    logger.info("Using Auth0Provider (OAuth proxy mode)")
    return _get_proxy_auth_provider()
