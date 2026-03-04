#!/bin/bash -ex

THIS_DIR=$(dirname "${BASH_SOURCE[0]}")
PROJECT_ROOT=$(realpath "${THIS_DIR}/../..")
cd "${PROJECT_ROOT}"

export BUILDKIT_PROGRESS=plain

echo -ne "\033]0;Web UI\007"

docker compose run \
    -it --rm --service-ports \
    'app'