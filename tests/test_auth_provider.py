"""Tests for auth provider dispatch."""

from __future__ import annotations

from cryptography.fernet import Fernet

import fca_mcp.settings as settings_mod
from fca_mcp.server.auth.provider import get_auth_provider


def _make_settings(auth0) -> settings_mod.Settings:
    return settings_mod.Settings(
        auth0=auth0,
        azure=settings_mod.AzureSettings(
            credential="none",
            storage_connection_string="DefaultEndpointsProtocol=https;AccountName=a;AccountKey=dGVzdA==;EndpointSuffix=core.windows.net",
        ),
        fca_api=settings_mod.FcaApiSettings(username="u", key="k"),
        server=settings_mod.ServerSettings(base_url="http://localhost:8000", jwt_secret_key="s"),
    )


def test_none_returns_none(mocker):
    mocker.patch(
        "fca_mcp.settings.get_settings",
        return_value=_make_settings(settings_mod.NoneAuth0Settings()),
    )
    assert get_auth_provider() is None


def test_remote_builds_remote_provider(mocker):
    from fastmcp.server.auth import RemoteAuthProvider

    mocker.patch(
        "fca_mcp.settings.get_settings",
        return_value=_make_settings(
            settings_mod.RemoteAuth0Settings(domain="test.auth0.com", audience="aud"),
        ),
    )
    provider = get_auth_provider()
    assert isinstance(provider, RemoteAuthProvider)


def test_proxy_builds_auth0_provider(mocker):
    sentinel = object()
    provider_ctor = mocker.patch(
        "fastmcp.server.auth.providers.auth0.Auth0Provider",
        return_value=sentinel,
    )
    mocker.patch(
        "fca_mcp.settings.get_settings",
        return_value=_make_settings(
            settings_mod.ProxyAuth0Settings(
                domain="test.auth0.com",
                audience="aud",
                mode=settings_mod.AuthMode.PROXY,
                client_id="cid",
                client_secret="csec",
                jwt_signing_key="jwt",
                storage_encryption_key=Fernet.generate_key().decode(),
            )
        ),
    )
    assert get_auth_provider() is sentinel
    provider_ctor.assert_called_once()


