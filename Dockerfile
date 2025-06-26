# Dockerfile for Dremio MCP Server
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ src/
COPY README.md LICENSE ./

# Install dependencies using uv
RUN uv sync --frozen

# Create directory for token files
RUN mkdir -p /app/tokens

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash mcp && \
    chown -R mcp:mcp /app
USER mcp

# Expose port (if needed for health checks or metrics)
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/src
ENV DREMIO_PAT_FILE=/app/tokens/current.token

# Health check to verify MCP server is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Default command to run the MCP server
CMD ["uv", "run", "dremio-mcp-server", "run", "--dremio-pat", "@/app/tokens/current.token"]
