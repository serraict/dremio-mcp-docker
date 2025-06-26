# Token Refresher Dockerfile
FROM python:3.12-alpine

LABEL org.opencontainers.image.source="https://github.com/serraict/dremio-mcp-docker"
LABEL org.opencontainers.image.description="Dremio Token Refresher"

# Install required packages
RUN apk add --no-cache \
    docker-cli \
    && pip install --no-cache-dir requests docker

# Create non-root user
RUN adduser -D -u 1000 refresher

# Create working directory
WORKDIR /app

# Copy scripts
COPY --chown=refresher:refresher refresh-token.py /app/
COPY --chown=refresher:refresher entrypoint.sh /app/entrypoint.sh

# Make scripts executable
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER refresher

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV TOKEN_FILE=/app/tokens/current.token
ENV REFRESH_INTERVAL=72000
ENV COMPOSE_PROJECT_NAME=dremio-mcp-docker

# Default command
ENTRYPOINT ["/app/entrypoint.sh"]
