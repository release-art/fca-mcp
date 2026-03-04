#!/bin/bash -xe

THIS_DIR=$(dirname "${BASH_SOURCE[0]}")
PROJECT_ROOT=$(realpath "${THIS_DIR}/..")
cd "${PROJECT_ROOT}"

LOCAL_BIN_PATH="${HOME}/.local/bin"
case ":${PATH}:" in
    *":${LOCAL_BIN_PATH}:"*) ;;
    *) export PATH="${LOCAL_BIN_PATH}:${PATH}" ;;
esac

export SERVER_BASE_URL="${SERVER_BASE_URL:-http://localhost:8000}"

export FCA_API_USERNAME="${FCA_API_USERNAME:-op://Employee/d5fon4y2ftqt6cb3bww4bizoza/username}"
export FCA_API_KEY="${FCA_API_KEY:-op://Employee/d5fon4y2ftqt6cb3bww4bizoza/api key}"

export AUTH0_DOMAIN="${AUTH0_DOMAIN:-op://Auth0 - dev/MCP Auth0 App/OAuth Domain}"
export AUTH0_AUDIENCE="${AUTH0_AUDIENCE:-op://Auth0 - dev/MCP Auth0 App/OAuth Audience}"
export AUTH0_CLIENT_ID="${AUTH0_CLIENT_ID:-op://Auth0 - dev/MCP Auth0 App/OAuth Client ID}"
export AUTH0_CLIENT_SECRET="${AUTH0_CLIENT_SECRET:-op://Auth0 - dev/MCP Auth0 App/OAuth Client Secret}"
export AUTH0_JWT_SIGNING_KEY="secret"
export AUTH0_STORAGE_ENCRYPTION_KEY="secret42"

if [ -n "$*" ]; then
    ARGS=("$@")
else
    ARGS=(python -m fca_mcp serve --reload)
fi

cd "${THIS_DIR}/.."
exec op run --no-masking -- pdm run "${ARGS[@]}"