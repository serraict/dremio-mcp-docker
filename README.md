# Dremio MCP Docker Deployment

Quick start guide for deploying Dremio MCP Server with Docker.

## Prerequisites

- Docker and Docker Compose
- Access to a Dremio server with username/password authentication
- Network connectivity between containers and Dremio server

## Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/dremio-mcp-docker.git
   cd dremio-mcp-docker
   ```

2. **Configure environment**

   ```bash
   cp .env.example .env
   ```

3. **Deploy**

   ```bash
   docker-compose up -d
   ```

4. **Verify deployment**

   ```bash
   # Check service status
   docker-compose ps
   
   # Check logs
   docker-compose logs -f
   ```

5. **Connect your MCP client**
   - The MCP server will be available via stdio
   - Connect Claude Desktop or other MCP clients to the running container

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `DREMIO_URI` | Yes | Dremio server URL | - |
| `DREMIO_USERNAME` | Yes | Dremio username | - |
| `DREMIO_PASSWORD` | Yes | Dremio password | - |
| `REFRESH_INTERVAL` | No | Token refresh interval (seconds) | 72000 (20h) |
| `COMPOSE_PROJECT_NAME` | No | Docker Compose project name | dremio-mcp-docker |

## Usage Examples

### Development with Debug Logging

```bash
# .env file
MCP_EXTRA_ARGS=--log-level DEBUG

docker-compose up
```

### Production Deployment

```bash
# Use Docker secrets or external secret management
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Custom Token Refresh Interval

```bash
# Refresh every 12 hours instead of 20
REFRESH_INTERVAL=43200 docker-compose up -d
```

## Troubleshooting

### Token Issues

```bash
# Check token refresher logs
docker-compose logs token-refresher

# Manually trigger token refresh
docker-compose exec token-refresher python /app/refresh-token.py --once
```

### MCP Service Issues

```bash
# Check MCP server logs
docker-compose logs dremio-mcp

# Restart MCP service
docker-compose restart dremio-mcp
```

### Network Connectivity

```bash
# Test Dremio connectivity from token-refresher
docker-compose exec token-refresher curl -v $DREMIO_URI/apiv2/login
```

## Architecture

- **dremio-mcp**: Main MCP server container
- **token-refresher**: Automatic token management
- **token-volume**: Shared volume for secure token storage

## Security Notes

- Tokens are stored in Docker volumes, not environment variables
- Both services run as non-root users
- Docker socket access is read-only and limited to token-refresher
- Consider using Docker secrets for production deployments
