# Dremio MCP Service Dockerfile
FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/your-org/dremio-mcp-docker"
LABEL org.opencontainers.image.description="Dremio MCP Server"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Dremio MCP directly from GitHub
RUN pip install --no-cache-dir git+https://github.com/dremio/dremio-mcp.git

# Create directory for token files
RUN mkdir -p /app/tokens

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 mcp && \
    chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DREMIO_PAT_FILE=/app/tokens/current.token

# Copy entrypoint script
COPY --chown=mcp:mcp entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD test -f /app/tokens/current.token && echo "Token file exists" || exit 1

# Default command
ENTRYPOINT ["/app/entrypoint.sh"]
