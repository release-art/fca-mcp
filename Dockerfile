FROM python:3.13-slim AS base

WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install PDM
RUN pip install --upgrade --no-cache-dir pdm pip

# Copy project files
COPY pyproject.toml pdm.lock* ./
COPY README.md ./
COPY src/ ./src/

# Install dependencies including FastAPI and uvicorn
RUN pdm install --frozen-lockfile --prod --no-editable --no-self
# Build the project
RUN pdm build --no-sdist


# Expose HTTP port
EXPOSE 8000

# Health check for HTTP server
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD curl -f http://localhost:8000//.container/health || exit 1


FROM python:3.13-slim AS release

WORKDIR /app

COPY --from=base /app/.venv /app/.venv
COPY --from=base /app/dist /app/dist

RUN python -m pip install --no-cache-dir --prefix=/app/.venv --no-deps --no-warn-script-location dist/*.whl

# Run HTTP server by default
CMD ["/app/.venv/bin/python", "-m", "fca_mcp", "serve", "--port", "8000"]
