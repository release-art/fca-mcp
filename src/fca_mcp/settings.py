"""Global settings for the fca-mcp project."""

from __future__ import annotations

import base64
import enum
import functools
import logging
import os
from typing import Annotated, Any, Literal, Union

from pydantic import Field, HttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


@enum.unique
class AuthMode(enum.StrEnum):
    """Authentication mode selection."""

    REMOTE = "remote"
    PROXY = "proxy"


@enum.unique
class AzureCredentialType(enum.StrEnum):
    """Types of Azure credentials supported for authentication."""

    NONE = "none"
    DEFAULT = "default"


class AzureSettings(BaseSettings):
    """Azure storage configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="AZURE_",
        extra="forbid",
    )

    credential: Annotated[
        AzureCredentialType,
        Field(
            default=AzureCredentialType.DEFAULT,
            description="Azure credential type to use for authentication",
        ),
    ]

    storage_connection_string: Annotated[
        str | None,
        Field(
            default=None,
            description="Azure Storage connection string (required for NONE credential type)",
        ),
    ]

    storage_account: Annotated[
        str | None,
        Field(
            default=None,
            description="Azure Storage account name (required for DEFAULT credential type)",
        ),
    ]

    storage_blob_endpoint: Annotated[
        str | None,
        Field(
            default=None,
            description="Azure Blob Storage endpoint URL (optional, defaults to https://{account}.blob.core.windows.net)",
        ),
    ]

    storage_queue_endpoint: Annotated[
        str | None,
        Field(
            default=None,
            description="Azure Queue Storage endpoint URL (optional, defaults to https://{account}.queue.core.windows.net)",
        ),
    ]

    storage_table_endpoint: Annotated[
        str | None,
        Field(
            default=None,
            description="Azure Table Storage endpoint URL (optional, defaults to https://{account}.table.core.windows.net)",
        ),
    ]


class _BaseAuth0Settings(BaseSettings):
    """Common Auth0 settings shared by all auth modes."""

    model_config = SettingsConfigDict(
        env_prefix="AUTH0_",
        extra="ignore",
    )

    domain: Annotated[
        str,
        Field(
            ...,
            description="Auth0 domain (e.g., 'your-tenant.auth0.com')",
        ),
    ]
    audience: Annotated[
        str,
        Field(
            ...,
            description="Auth0 API audience identifier",
        ),
    ]
    interactive_client_id: Annotated[
        str | None,
        Field(
            default=None,
            description="Auth0 SPA client ID for the interactive web UI",
        ),
    ]


class RemoteAuth0Settings(_BaseAuth0Settings):
    """Auth0 settings for remote/JWT-only verification mode."""

    mode: Literal[AuthMode.REMOTE] = AuthMode.REMOTE


class ProxyAuth0Settings(_BaseAuth0Settings):
    """Auth0 settings for full OAuth proxy mode."""

    mode: Literal[AuthMode.PROXY]
    client_id: Annotated[
        str,
        Field(
            ...,
            description="Auth0 client ID",
        ),
    ]
    client_secret: Annotated[
        str,
        Field(
            ...,
            description="Auth0 client secret",
        ),
    ]
    jwt_signing_key: Annotated[
        str,
        Field(
            ...,
            description="JWT signing key for proxy mode token issuance",
        ),
    ]
    storage_encryption_key: Annotated[
        str,
        Field(
            ...,
            description="Encryption key for client token storage",
        ),
    ]

    @field_validator("storage_encryption_key")
    @classmethod
    def validate_storage_encryption_key(cls, v: str) -> str:
        """Validate that storage_encryption_key is 32 url-safe base64-encoded bytes."""
        try:
            decoded = base64.urlsafe_b64decode(v)
            if len(decoded) != 32:
                raise ValueError(f"must be 32 bytes when decoded, got {len(decoded)} bytes")
        except Exception as e:
            raise ValueError(f"must be 32 url-safe base64-encoded bytes: {e}") from e
        return v


Auth0Settings = Annotated[
    Union[RemoteAuth0Settings, ProxyAuth0Settings],
    Field(discriminator="mode"),
]


class FcaApiSettings(BaseSettings):
    """FCA API credentials and configuration."""

    model_config = SettingsConfigDict(
        env_prefix="FCA_API_",
        extra="forbid",
    )

    username: Annotated[
        str,
        Field(
            ...,
            description="FCA API username/email",
        ),
    ]
    key: Annotated[
        str,
        Field(
            ...,
            description="FCA API key",
        ),
    ]
    base_url: Annotated[
        HttpUrl | None,
        Field(
            default=None,
            description="FCA API base URL (optional override)",
        ),
    ]
    timeout: Annotated[
        float,
        Field(
            default=30.0,
            gt=0,
            description="API request timeout in seconds",
        ),
    ]
    max_retries: Annotated[
        int,
        Field(
            default=3,
            ge=0,
            description="Maximum number of retries for failed requests",
        ),
    ]


class ServerSettings(BaseSettings):
    """Server configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="SERVER_",
        extra="forbid",
    )

    host: Annotated[
        str,
        Field(
            default="0.0.0.0",
            description="Server host address",
        ),
    ]
    port: Annotated[
        int,
        Field(
            default=8000,
            ge=1,
            le=65535,
            description="Server port number",
        ),
    ]
    base_url: Annotated[
        HttpUrl,
        Field(
            ...,
            description="Full base URL",
        ),
    ]
    workers: Annotated[
        int,
        Field(
            default=1,
            ge=1,
            description="Number of worker processes",
        ),
    ]


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        extra="forbid",
    )

    level: Annotated[
        Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        Field(
            default="INFO",
            description="Logging level",
        ),
    ]
    format: Annotated[
        Literal["json", "text"],
        Field(
            default="text",
            description="Log output format",
        ),
    ]
    file: Annotated[
        str | None,
        Field(
            default=None,
            description="Log file path (None = stdout only)",
        ),
    ]


class Settings(BaseSettings):
    """Global application settings."""

    model_config = SettingsConfigDict(
        extra="forbid",
        case_sensitive=False,
    )

    # Environment and deployment
    environment: Annotated[
        Literal["development", "staging", "production"],
        Field(
            default="development",
            description="Application environment",
        ),
    ]
    debug: Annotated[
        bool,
        Field(
            default=False,
            description="Enable debug mode",
        ),
    ]

    # Nested settings
    azure: Annotated[AzureSettings, Field(default_factory=AzureSettings)]
    auth0: Auth0Settings
    fca_api: Annotated[FcaApiSettings, Field(default_factory=FcaApiSettings)]

    @model_validator(mode="before")
    @classmethod
    def _build_auth0(cls, data: Any) -> Any:
        if isinstance(data, dict) and "auth0" not in data:
            mode = os.environ.get("AUTH0_MODE", AuthMode.REMOTE)
            data["auth0"] = ProxyAuth0Settings() if mode == AuthMode.PROXY else RemoteAuth0Settings()
        return data
    server: Annotated[ServerSettings, Field(default_factory=ServerSettings)]
    logging: Annotated[LoggingSettings, Field(default_factory=LoggingSettings)]

    # Additional top-level settings
    cors_origins: Annotated[
        list[str],
        Field(
            default_factory=lambda: ["*"],
            description="Allowed CORS origins",
        ),
    ]
    api_version: Annotated[
        str,
        Field(
            default="v1",
            description="API version prefix",
        ),
    ]

    def get_base_url(self) -> str:
        """Get the full base URL for the application."""
        return str(self.server.base_url).rstrip("/")


@functools.lru_cache
def get_settings() -> Settings:
    """
    Get cached global settings instance.

    This function is cached to ensure a single Settings instance
    is used throughout the application lifecycle.

    Returns:
        Settings: The global settings instance
    """
    try:
        return Settings()
    except Exception as e:
        logger.error(
            "Failed to construct Settings. Environment variables:",
            extra={"environ": dict(os.environ)},
        )
        raise
