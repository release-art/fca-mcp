FROM python:3.13-slim

WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl && \
    rm -rf /var/lib/apt/lists/*

# Install PDM
RUN pip install --no-cache-dir pdm

# Copy project files
COPY pyproject.toml pdm.lock* ./
COPY README.md ./
COPY src/ ./src/
COPY mcp_fca/ ./mcp_fca/
COPY fca_mcp_server.py ./
COPY .env.example ./

# Install dependencies including FastAPI and uvicorn
RUN pdm install --prod --no-editable

# Set Python path
ENV PYTHONPATH=/app/src:/app

# Expose HTTP port
EXPOSE 8000

# Health check for HTTP server
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD curl -f http://localhost:8000/health || exit 1

# Run HTTP server by default
CMD ["pdm", "run", "python", "fca_mcp_server.py", "--http-mode", "--host", "0.0.0.0", "--port", "8000"]
