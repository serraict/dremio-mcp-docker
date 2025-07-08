# Dremio MCP Service Dockerfile with Supergateway Support
FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/serraict/dremio-mcp-docker"
LABEL org.opencontainers.image.description="Dremio MCP Server with HTTP Support via Supergateway"

# Set working directory
WORKDIR /app

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Dremio MCP directly from GitHub
RUN pip install --no-cache-dir git+https://github.com/dremio/dremio-mcp.git

# Install Supergateway globally
RUN npm install -g supergateway

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

# Health check - verify both token file exists and HTTP endpoint responds
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD test -f /app/tokens/current.token && curl -f http://localhost:7910/mcp || exit 1

# Default command
ENTRYPOINT ["/app/entrypoint.sh"]
