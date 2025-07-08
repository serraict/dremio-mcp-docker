# Unified Design Document for Dremio MCP Docker Deployment

## Executive Summary

This document presents a comprehensive design for deploying the Dremio MCP (Model Context Protocol) server using Docker containers.
These containers allow you to run an MCP server for your Dremio Community edition.

## Problem Statement

The Dremio MCP server requires authentication tokens.
The Dremio community edition does not have the functionality of creating personal access tokens.

The Dremio MCP server interfaces over stdio, requiring to run an instance of it on the same node.

## Solution Architecture

We can use our username and password to get login token from the api,
which can be used as an access token for the Dremio MCP server.

Provide an http streamable proxy in front of dremio mcp.

### Multi-Container Design

The solution employs a two-service architecture:

1. **Dremio MCP Server Container**

- ✅ Runs the official Dremio MCP server.
- ⏳ Provides MCP interface to clients.

2. **Token Refresher Container**

- ✅ Retrieves token from Dremio community edition
- ✅ Monitors token expiration continuously.
- ❌ Restarts MCP server after token refresh - we do not do this because we don't want to give this container access to sudo and docker privileges.

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

(todo: review)

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

Todo: reference the files

### Environment Configuration

Todo: create .env.example files

## Security Considerations

### Container Security

1. **Non-root Execution**: All containers run as dedicated non-root users.
2. **Read-only Filesystems**: Where possible, containers use read-only root filesystems.

### Secret Management

1. **Environment Variables**: Credentials passed via environment (development).
2. **Docker Secrets**: Support for Docker Swarm secrets (production).
3. **Volume Security**: Token storage with restricted permissions.
4. **No Credential Logging**: Tokens and passwords never appear in logs.

### Network Security

1. **Internal Networks**: Services communicate over internal Docker networks.
2. **Minimal Exposure**: Only MCP server port exposed externally.
3. **TLS Support**: Ready for TLS termination via reverse proxy.

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
