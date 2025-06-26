# Unified Design Document for Dremio MCP Docker Deployment

## Executive Summary

This document presents a comprehensive design for deploying the Dremio MCP (Model Context Protocol) server using Docker containers.
These containers allow you to run an MCP server for your Dremio Community edition.

## Problem Statement

The Dremio MCP server requires authentication tokens.
The Dremio community edition does not have the functionality of creating personal access tokens,
but we can use our username and password to get login token from the api,
which can be used as an access token for the Dremio MCP server.

## Solution Architecture

### Multi-Container Design

The solution employs a two-service architecture:

1. **Dremio MCP Server Container**

- Runs the official Dremio MCP server.
- Provides MCP interface to clients.

2. **Token Refresher Container**

- Retrieves token from Dremio community edition
- Monitors token expiration continuously.
- Restarts MCP server after token refresh.

### Shared Token Storage

Both containers share a Docker volume for secure token storage:

- Token files stored in JSON format with expiration metadata.

```json
{
  "token": "abc123",
  "expires_at": "2025-06-26T12:00:00Z"
}
```

- Read-only access for MCP server.
- Read-write access for token refresher.
- Proper file permissions and ownership.

## Implementation Details

### Repository Structure

```text
dremio-mcp-docker/
├── README.md                          # Quick start and overview
├── docker-compose.yml                 # Main deployment configuration
├── .env.example                       # Environment variable template
├── services/
│   ├── dremio-mcp/
│   │   ├── Dockerfile                 # MCP server container
│   │   ├── entrypoint.sh             # Startup script
│   │   └── health_check.py           # Health monitoring
│   └── token-refresher/
│       ├── Dockerfile                # Token management container
│       ├── refresh-token.py          # Token refresh logic
│       ├── entrypoint.sh            # Startup script
│       └── health_check.py          # Health monitoring
├── docs/
│   ├── DEPLOYMENT.md                 # Deployment guide
│   ├── TROUBLESHOOTING.md           # Common issues
│   └── SECURITY.md                  # Security guidelines
└── scripts/
    ├── setup.sh                     # Initial setup
    └── deploy.sh                    # Automated deployment
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  dremio-mcp:
    build: ./services/dremio-mcp
    ports:
      - "3000:3000"
    restart: unless-stopped
    depends_on:
      token-refresher:
        condition: service_healthy

  token-refresher:
    build: ./services/token-refresher
    environment:
      - DREMIO_URI=${DREMIO_URI}
      - DREMIO_USERNAME=${DREMIO_USERNAME}
      - DREMIO_PASSWORD=${DREMIO_PASSWORD}
    volumes:
      - tokens:/app/tokens:rw
      - /var/run/docker.sock:/var/run/docker.sock:ro
    restart: unless-stopped

volumes:
  tokens:
```

### Environment Configuration

```env
# Required Configuration
DREMIO_URI=https://your-dremio-instance.com
DREMIO_USERNAME=your-username
DREMIO_PASSWORD=your-password

# Optional Configuration
COMPOSE_PROJECT_NAME=dremio-mcp-docker
LOG_LEVEL=INFO
MCP_PORT=3000
REFRESH_INTERVAL=300
REFRESH_THRESHOLD=6
```

## Security Considerations

### Container Security

1. **Non-root Execution**: All containers run as dedicated non-root users.
2. **Minimal Images**: Based on slim Python images to reduce attack surface.
3. **Read-only Filesystems**: Where possible, containers use read-only root filesystems.
4. **Capability Dropping**: Unnecessary Linux capabilities are removed.

### Secret Management

1. **Environment Variables**: Credentials passed via environment (development).
2. **Docker Secrets**: Support for Docker Swarm secrets (production).
3. **Volume Security**: Token storage with restricted permissions.
4. **No Credential Logging**: Tokens and passwords never appear in logs.

### Network Security

1. **Internal Networks**: Services communicate over internal Docker networks.
2. **Minimal Exposure**: Only MCP server port exposed externally.
3. **Firewall Integration**: Designed to work with external firewalls.
4. **TLS Support**: Ready for TLS termination via reverse proxy.

## Operational Features

### Automated Token Management

- **Continuous Monitoring**: Token expiration checked every 5 minutes.
- **Proactive Refresh**: Tokens refreshed 6 hours before expiry.
- **Automatic Recovery**: Failed refresh attempts handled with exponential backoff.
- **Service Coordination**: MCP server automatically restarted after token refresh.

### Health Monitoring

- **Service Health Checks**: Both containers provide health endpoints.
- **Token Validation**: Health checks verify token validity and expiration.
- **Dependency Management**: Services start in correct order with health dependencies.
- **Restart Policies**: Automatic restart on failures with proper backoff.

### Logging and Debugging

- **Structured Logging**: JSON format for easy parsing and aggregation.
- **Configurable Levels**: Debug, info, warning, error logging levels.
- **Sensitive Data Protection**: No tokens or passwords in log output.
- **Audit Trail**: Complete record of token refresh activities.

## Deployment Scenarios

### Development Environment

```bash
# Quick start for development
git clone https://github.com/your-org/dremio-mcp-docker.git
cd dremio-mcp-docker
cp .env.example .env
# Edit .env with your settings
docker-compose up --build
```

### Production Environment

```bash
# Production deployment with Docker Swarm
docker stack deploy -c docker-compose.yml -c docker-compose.prod.yml dremio-mcp
```
