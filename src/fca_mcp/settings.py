"""Global settings for the fca-mcp project."""

from __future__ import annotations

import functools
from typing import Annotated, Literal

from pydantic import Field, HttpUrl, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class AzureSettings(BaseSettings):
    """Azure storage configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="AZURE_",
        extra="forbid",
    )

    storage_connection_string: Annotated[
        str,
        Field(
            description="Azure Storage connection string",
        ),
    ]

class Auth0Settings(BaseSettings):
    """Auth0 OAuth configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="AUTH0_",
        extra="forbid",
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
    client_id: Annotated[
        str,
        Field(
            description="Auth0 client ID (optional, for client credentials flow)",
        ),
    ]
    client_secret: Annotated[
        str,
        Field(
            description="Auth0 client secret (optional, for client credentials flow)",
        ),
    ]
    jwt_signing_key: Annotated[
        str,
        Field(
            description="JWT signing key for validating tokens (optional)",
        ),
    ]
    storage_encryption_key: Annotated[
        str,
        Field(
            description="Encryption key for securely storing sensitive data (optional)",
        ),
    ]


class RedisSettings(BaseSettings):
    """Redis connection and caching configuration."""

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        extra="forbid",
    )

    url: Annotated[
        RedisDsn,
        Field(
            default="redis://localhost:6379/0",
            description="Redis connection URL",
        ),
    ]
    password: Annotated[
        str | None,
        Field(
            default=None,
            description="Redis password (if required)",
        ),
    ]
    db: Annotated[
        int,
        Field(
            default=0,
            ge=0,
            le=15,
            description="Redis database number (0-15)",
        ),
    ]
    max_connections: Annotated[
        int,
        Field(
            default=10,
            ge=1,
            description="Maximum number of connections in the pool",
        ),
    ]
    socket_timeout: Annotated[
        float,
        Field(
            default=5.0,
            gt=0,
            description="Socket timeout in seconds",
        ),
    ]
    socket_connect_timeout: Annotated[
        float,
        Field(
            default=5.0,
            gt=0,
            description="Socket connection timeout in seconds",
        ),
    ]
    cache_ttl: Annotated[
        int,
        Field(
            default=3600,
            ge=0,
            description="Default cache TTL in seconds (0 = no expiration)",
        ),
    ]
    enabled: Annotated[
        bool,
        Field(
            default=True,
            description="Enable Redis caching",
        ),
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
    auth0: Annotated[Auth0Settings, Field(default_factory=Auth0Settings)]
    redis: Annotated[RedisSettings, Field(default_factory=RedisSettings)]
    fca_api: Annotated[FcaApiSettings, Field(default_factory=FcaApiSettings)]
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
        return str(self.server.base_url)


@functools.lru_cache
def get_settings() -> Settings:
    """
    Get cached global settings instance.

    This function is cached to ensure a single Settings instance
    is used throughout the application lifecycle.

    Returns:
        Settings: The global settings instance
    """
    return Settings()
