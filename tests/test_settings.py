"""Tests for settings validators and auth mode dispatch."""

from __future__ import annotations

import base64

import pytest
from cryptography.fernet import Fernet

import fca_mcp.settings as settings_mod


class TestAzureTableName:
    def test_valid(self):
        name = settings_mod.AzureTableName._validate("apicache00")
        assert name == "apicache00"

    def test_not_a_string(self):
        with pytest.raises(ValueError, match="Expected str"):
            settings_mod.AzureTableName._validate(123)

    def test_invalid_chars(self):
        with pytest.raises(ValueError, match="not a valid Azure Table"):
            settings_mod.AzureTableName._validate("bad-name")

    def test_starts_with_digit(self):
        with pytest.raises(ValueError, match="not a valid Azure Table"):
            settings_mod.AzureTableName._validate("1bad")

    def test_too_short(self):
        with pytest.raises(ValueError, match="not a valid Azure Table"):
            settings_mod.AzureTableName._validate("ab")


class TestStorageEncryptionKey:
    def _build(self, key: str) -> None:
        settings_mod.ProxyAuth0Settings(
            domain="test.auth0.com",
            audience="aud",
            mode=settings_mod.AuthMode.PROXY,
            client_id="cid",
            client_secret="csec",
            jwt_signing_key="jwt",
            storage_encryption_key=key,
        )

    def test_valid_fernet_key(self):
        self._build(Fernet.generate_key().decode())

    def test_wrong_length(self):
        short = base64.urlsafe_b64encode(b"x" * 10).decode()
        with pytest.raises(ValueError, match="32 bytes when decoded|32 url-safe"):
            self._build(short)

    def test_not_base64(self):
        with pytest.raises(ValueError, match="32 url-safe base64"):
            self._build("!!!not-base64!!!")


class TestAuth0ModeDispatch:
    def test_mode_none(self, monkeypatch):
        monkeypatch.setenv("AUTH0_MODE", "none")
        built = settings_mod.Settings._build_auth0({})
        assert isinstance(built["auth0"], settings_mod.NoneAuth0Settings)

    def test_mode_remote(self, monkeypatch):
        monkeypatch.setenv("AUTH0_MODE", "remote")
        monkeypatch.setenv("AUTH0_DOMAIN", "x.auth0.com")
        monkeypatch.setenv("AUTH0_AUDIENCE", "aud")
        built = settings_mod.Settings._build_auth0({})
        assert isinstance(built["auth0"], settings_mod.RemoteAuth0Settings)

    def test_mode_proxy(self, monkeypatch):
        monkeypatch.setenv("AUTH0_MODE", "proxy")
        monkeypatch.setenv("AUTH0_DOMAIN", "x.auth0.com")
        monkeypatch.setenv("AUTH0_AUDIENCE", "aud")
        monkeypatch.setenv("AUTH0_CLIENT_ID", "cid")
        monkeypatch.setenv("AUTH0_CLIENT_SECRET", "csec")
        monkeypatch.setenv("AUTH0_JWT_SIGNING_KEY", "jwt")
        monkeypatch.setenv("AUTH0_STORAGE_ENCRYPTION_KEY", Fernet.generate_key().decode())
        built = settings_mod.Settings._build_auth0({})
        assert isinstance(built["auth0"], settings_mod.ProxyAuth0Settings)

    def test_mode_invalid(self, monkeypatch):
        monkeypatch.setenv("AUTH0_MODE", "bogus")
        with pytest.raises(ValueError, match="Invalid AUTH0_MODE"):
            settings_mod.Settings._build_auth0({})

    def test_preserves_existing(self):
        sentinel = object()
        assert settings_mod.Settings._build_auth0({"auth0": sentinel})["auth0"] is sentinel

    def test_non_dict_passthrough(self):
        assert settings_mod.Settings._build_auth0("not-a-dict") == "not-a-dict"
