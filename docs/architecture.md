# Architecture Overview

This document explains how the Dremio MCP Docker setup works internally.

## Service Overview

The setup consists of three main services:

- **dremio**: Dremio Community Edition database
- **dremio-mcp**: Combined MCP server with HTTP proxy
- **token-refresher**: Automatic Dremio token management

## Communication Flow

```text
VS Code/AI Client → HTTP (port 7910) → Supergateway → stdio → Dremio MCP Server → Dremio (port 9047)
```

## MCP Container Details

The `dremio-mcp` service runs both:

- **Supergateway** (Node.js): HTTP proxy providing `streamableHttp` transport
- **Dremio MCP Server** (Python): Core MCP server with Dremio integration

### Why This Architecture?

1. **HTTP Compatibility**: Many AI clients work better with HTTP than stdio
2. **Token Management**: Automatic token refresh without interrupting sessions
3. **Security**: Tokens stored in shared volume, not exposed in environment variables
4. **Isolation**: Each service has a single responsibility

## Token Management

1. **token-refresher** authenticates with Dremio using username/password
2. Stores the JWT token in `/app/tokens/current.token` (shared volume)
3. **dremio-mcp** reads the token and uses it for Dremio API calls
4. Token automatically refreshes before expiration (default: every 20 hours)

## Volumes

- **token-volume**: Shared between token-refresher (rw) and dremio-mcp (ro)
- **dremio-data**: Persistent storage for Dremio database files

## Networking

All services communicate over the `dremio-mcp-network` bridge network:
- **dremio**: Internal hostname `dremio:9047`
- **dremio-mcp**: Exposed on `localhost:7910`
- **token-refresher**: Internal only, no exposed ports

## Security Considerations

- Credentials only in `.env` file and Docker environment variables
- JWT tokens stored in Docker volume, not in logs
- MCP server has read-only access to token volume
- Dremio data persisted in named volume for data safety
