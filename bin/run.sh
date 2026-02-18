#!/bin/bash -xe

THIS_DIR=$(dirname "${BASH_SOURCE[0]}")
PROJECT_ROOT=$(realpath "${THIS_DIR}/..")
cd "${PROJECT_ROOT}"

LOCAL_BIN_PATH="${HOME}/.local/bin"
case ":${PATH}:" in
    *":${LOCAL_BIN_PATH}:"*) ;;
    *) export PATH="${LOCAL_BIN_PATH}:${PATH}" ;;
esac

export FCA_API_USERNAME="${FCA_API_USERNAME:-op://Employee/d5fon4y2ftqt6cb3bww4bizoza/username}"
export FCA_API_KEY="${FCA_API_KEY:-op://Employee/d5fon4y2ftqt6cb3bww4bizoza/api key}"

if [ -n "$*" ]; then
    ARGS=("$@")
else
    ARGS=(python -m fca_mcp serve)
fi

cd "${THIS_DIR}/.."
exec op run --no-masking -- pdm run "${ARGS[@]}"