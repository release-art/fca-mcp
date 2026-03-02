# Settings System Documentation

## Overview

The FCA MCP project uses a well-designed, type-safe settings system built on **Pydantic v2** and **pydantic-settings**. All configuration is loaded from environment variables, with sensible defaults and comprehensive validation.

## Quick Start

### 1. Configure Environment Variables

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```bash
# Required settings
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=https://your-api-audience
FCA_API_USERNAME=your-email@example.com
FCA_API_KEY=your-fca-api-key

# Optional: Redis is enabled by default at localhost:6379
REDIS_URL=redis://localhost:6379/0
REDIS_ENABLED=true

# Optional: Server configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_HOSTNAME=localhost
```

### 2. Use Settings in Code

```python
from fca_mcp.settings import get_settings

# Get the global settings instance (cached)
settings = get_settings()

# Access nested settings
print(settings.auth0.domain)
print(settings.fca_api.username)
print(settings.redis.url)
print(settings.server.port)

# Get the full base URL
base_url = settings.get_base_url()
```

## Settings Structure

### Top-Level Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `environment` | `Literal["development", "staging", "production"]` | `"development"` | Application environment |
| `debug` | `bool` | `False` | Enable debug mode |
| `cors_origins` | `list[str]` | `["*"]` | Allowed CORS origins |
| `api_version` | `str` | `"v1"` | API version prefix |

### Auth0Settings (`settings.auth0`)

OAuth authentication configuration for Auth0.

| Setting | Type | Required | Description |
|---------|------|----------|-------------|
| `domain` | `str` | Yes | Auth0 domain (e.g., 'tenant.auth0.com') |
| `audience` | `str` | Yes | Auth0 API audience identifier |
| `client_id` | `str` | No | Client ID for client credentials flow |
| `client_secret` | `str` | No | Client secret for client credentials flow |

**Environment Variables:**
- `AUTH0_DOMAIN`
- `AUTH0_AUDIENCE`
- `AUTH0_CLIENT_ID` (optional)
- `AUTH0_CLIENT_SECRET` (optional)

### RedisSettings (`settings.redis`)

Redis connection and caching configuration.

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `url` | `RedisDsn` | `redis://localhost:6379/0` | Redis connection URL |
| `password` | `str` | `None` | Redis password |
| `db` | `int` | `0` | Redis database number (0-15) |
| `max_connections` | `int` | `10` | Maximum pool connections |
| `socket_timeout` | `float` | `5.0` | Socket timeout (seconds) |
| `socket_connect_timeout` | `float` | `5.0` | Connection timeout (seconds) |
| `cache_ttl` | `int` | `3600` | Default cache TTL (seconds, 0=no expiration) |
| `enabled` | `bool` | `True` | Enable Redis caching |

**Environment Variables:**
- `REDIS_URL`
- `REDIS_PASSWORD`
- `REDIS_DB`
- `REDIS_MAX_CONNECTIONS`
- `REDIS_SOCKET_TIMEOUT`
- `REDIS_SOCKET_CONNECT_TIMEOUT`
- `REDIS_CACHE_TTL`
- `REDIS_ENABLED`

### FcaApiSettings (`settings.fca_api`)

FCA API credentials and configuration.

| Setting | Type | Required | Description |
|---------|------|----------|-------------|
| `username` | `str` | Yes | FCA API username/email |
| `key` | `str` | Yes | FCA API key |
| `base_url` | `HttpUrl` | `None` | FCA API base URL (optional override) |
| `timeout` | `float` | `30.0` | API request timeout (seconds) |
| `max_retries` | `int` | `3` | Maximum retries for failed requests |

**Environment Variables:**
- `FCA_API_USERNAME`
- `FCA_API_KEY`
- `FCA_API_BASE_URL` (optional)
- `FCA_API_TIMEOUT`
- `FCA_API_MAX_RETRIES`

### ServerSettings (`settings.server`)

Server and host configuration.

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `host` | `str` | `"0.0.0.0"` | Server host address |
| `port` | `int` | `8000` | Server port number |
| `hostname` | `str` | `"localhost"` | Public hostname for URL generation |
| `base_url` | `HttpUrl` | `None` | Full base URL (auto-generated if not set) |
| `reload` | `bool` | `False` | Enable auto-reload (development) |
| `workers` | `int` | `1` | Number of worker processes |

**Environment Variables:**
- `SERVER_HOST`
- `SERVER_PORT`
- `SERVER_HOSTNAME`
- `SERVER_BASE_URL` (optional)
- `SERVER_RELOAD`
- `SERVER_WORKERS`

### LoggingSettings (`settings.logging`)

Logging configuration.

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `level` | `Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]` | `"INFO"` | Logging level |
| `format` | `Literal["json", "text"]` | `"text"` | Log output format |
| `file` | `str` | `None` | Log file path (None = stdout only) |

**Environment Variables:**
- `LOG_LEVEL`
- `LOG_FORMAT`
- `LOG_FILE` (optional)

## Usage Examples

### Getting Settings Instance

```python
from fca_mcp.settings import get_settings

# The settings instance is cached via @lru_cache
settings = get_settings()
```

### FastAPI Dependency Injection

```python
from typing import Annotated
from fastapi import Depends
from fca_mcp.settings import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]

@app.get("/config")
async def get_config(settings: SettingsDep):
    return {
        "environment": settings.environment,
        "api_version": settings.api_version,
    }
```

### Redis Client Configuration

```python
import redis
from fca_mcp.settings import get_settings

settings = get_settings()

if settings.redis.enabled:
    client = redis.from_url(
        str(settings.redis.url),
        password=settings.redis.password,
        db=settings.redis.db,
        max_connections=settings.redis.max_connections,
        socket_timeout=settings.redis.socket_timeout,
    )
```

### Environment-Specific Behavior

```python
from fca_mcp.settings import get_settings

settings = get_settings()

if settings.environment == "production":
    # Production configuration
    enable_metrics()
    setup_monitoring()
elif settings.environment == "development":
    # Development configuration
    if settings.debug:
        enable_debug_toolbar()
```

### Generating URLs

```python
from fca_mcp.settings import get_settings

settings = get_settings()

# Get full base URL
base_url = settings.get_base_url()
# Returns: "http://localhost:8000" (development)
#      or: "https://api.example.com" (production with SERVER_BASE_URL set)

# Generate API endpoints
api_endpoint = f"{base_url}/api/{settings.api_version}/firms"
```

## Type Safety

All settings are fully typed using Pydantic v2, providing:

- **Automatic validation** at startup
- **Type checking** with mypy/pyright
- **IDE autocomplete** for all settings
- **Runtime validation** for all values

## Environment Variable Loading

Settings are loaded in the following order (later overrides earlier):

1. Default values defined in the settings classes
2. Environment variables from the system
3. Values from `.env` file (if present)

## Best Practices

1. **Always use `get_settings()`** - Don't instantiate `Settings()` directly
2. **Use type hints** - Leverage `Settings` type for better IDE support
3. **Validate early** - Call `get_settings()` at application startup to catch configuration errors
4. **Never commit `.env`** - Keep credentials in `.env` (gitignored), use `.env.example` for documentation
5. **Use environment-specific settings** - Check `settings.environment` for env-specific behavior

## Troubleshooting

### Missing Required Settings

If you see a ValidationError at startup:

```
pydantic.ValidationError: 2 validation errors for Auth0Settings
domain
  Field required [type=missing, input_value={}, input_type=dict]
```

This means a required environment variable is not set. Check `.env.example` for required variables.

### Type Validation Errors

If you see a ValidationError for type mismatch:

```
pydantic.ValidationError: 1 validation error for ServerSettings
port
  Input should be a valid integer [type=int_type, input_value='abc', input_type=str]
```

Check that your environment variables have the correct format (e.g., `SERVER_PORT` should be a number).

## Migration from Direct `os.environ`

**Before:**
```python
import os

domain = os.environ["AUTH0_DOMAIN"]
username = os.environ["FCA_API_USERNAME"]
```

**After:**
```python
from fca_mcp.settings import get_settings

settings = get_settings()
domain = settings.auth0.domain
username = settings.fca_api.username
```

Benefits:
- Type safety and validation
- Better organization (namespaced)
- Centralized configuration
- Default values and documentation
- No KeyError exceptions
