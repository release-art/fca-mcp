"""FastMCP authentication module."""

from __future__ import annotations

from cryptography.fernet import Fernet
from fastmcp.server.auth import AuthProvider
from fastmcp.server.auth.providers.auth0 import Auth0Provider
from key_value.aio.wrappers.encryption import FernetEncryptionWrapper

import fca_mcp
import fca_mcp.settings


from . import scopes


def get_auth_provider() -> AuthProvider:
    """Get the Auth0 authentication provider."""
    settings = fca_mcp.settings.get_settings()
    tmp_api = fca_mcp.azure.api.AzureAPI(settings.azure)

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
