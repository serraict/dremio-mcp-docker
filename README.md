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
   # Edit .env with your Dremio connection details
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
   docker-compose logs -f dremio-mcp
   ```

5. **Connect your MCP client**
   
   The server supports two connection methods:

   **HTTP Endpoint (Recommended for web and VS Code):**
   - URL: `http://localhost:7910/mcp`
   - Transport: streamableHttp (event-stream format)
   - Session timeout: 60 seconds

   **Stdio (for Claude Desktop and other stdio clients):**
   - Connect directly to the running container via stdio

## Available Tools

The Dremio MCP server provides the following tools for database interaction:

| Tool | Description |
|------|-------------|
| `RunSqlQuery` | Execute SELECT queries on the Dremio cluster |
| `GetSchemaOfTable` | Get table schema information including column names and types |
| `GetTableOrViewLineage` | Find lineage relationships for tables and views |
| `GetDescriptionOfTableOrSchema` | Get descriptions and tags for tables or schemas |
| `GetUsefulSystemTableNames` | List system tables available for analysis |

## VS Code Integration Guide

### Prerequisites for VS Code

1. **Ensure the Dremio MCP Docker stack is running:**

   ```bash
   docker-compose up -d
   # Verify HTTP endpoint is accessible
   curl -f http://localhost:7910/mcp
   ```

### Setup Steps

#### Option 1: Using VS Code MCP Extension

1. **Install MCP Extension** (if available in VS Code marketplace)

2. **Add server configuration** to your VS Code settings:

   **Global settings** (`settings.json`):

   ```json
   {
     "mcp.servers": {
       "dremio-docker": {
         "name": "Dremio MCP (Docker)",
         "transport": {
           "type": "streamableHttp",
           "url": "http://localhost:7910/mcp"
         },
         "description": "Dremio database access via Docker deployment"
       }
     }
   }
   ```

   **Workspace settings** (`.vscode/settings.json`):

   ```json
   {
     "mcp.servers": {
       "dremio": {
         "transport": {
           "type": "streamableHttp", 
           "url": "http://localhost:7910/mcp"
         }
       }
     }
   }
   ```

#### Option 2: Manual Integration via Extensions

If using a third-party MCP extension or custom integration:

1. **Configure HTTP endpoint:** `http://localhost:7910/mcp`
2. **Transport type:** streamableHttp or event-stream
3. **Session timeout:** 60 seconds (automatic)

### Verification Steps

1. **Check VS Code MCP status** (extension-dependent)
2. **Test tool availability:**
   - Look for Dremio tools in VS Code command palette
   - Available tools: RunSqlQuery, GetSchemaOfTable, GetTableOrViewLineage, etc.

3. **Test database query:**
   - Use the RunSqlQuery tool
   - Try: `SELECT * FROM INFORMATION_SCHEMA.TABLES LIMIT 5`

### Troubleshooting VS Code Integration

**Common Issues:**

1. **Connection timeout:**

   ```bash
   # Check if service is running and port is accessible
   docker-compose ps dremio-mcp
   curl -f http://localhost:7910/mcp
   ```

2. **No tools discovered:**

   ```bash
   # Verify tools are available via HTTP
   curl -X POST http://localhost:7910/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
   ```

3. **Session expired errors:**
   - Restart VS Code
   - Or restart the Docker service: `docker-compose restart dremio-mcp`

### Performance Notes

- **Session timeout**: 60 seconds of inactivity
- **Concurrent connections**: Supported via stateful mode
- **Token management**: Automatic refresh every 20 hours

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `DREMIO_URI` | Yes | Dremio server URL | - |
| `DREMIO_USERNAME` | Yes | Dremio username | - |
| `DREMIO_PASSWORD` | Yes | Dremio password | - |
| `REFRESH_INTERVAL` | No | Token refresh interval (seconds) | 72000 (20h) |
| `COMPOSE_PROJECT_NAME` | No | Docker Compose project name | dremio-mcp-docker |
| `MCP_EXTRA_ARGS` | No | Additional arguments for MCP server | - |

## Network Configuration

The deployment exposes the following ports:

| Port | Service | Protocol | Description |
|------|---------|----------|-------------|
| 7910 | HTTP MCP Server | HTTP | Supergateway HTTP endpoint for MCP access |

Internal communication:

- Token storage via shared Docker volume
- Stdio communication between Supergateway and Dremio MCP server

## Usage Examples

### HTTP Endpoint Usage

```bash
# Test server availability
curl -f http://localhost:7910/mcp \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'

# Query Dremio system tables
curl -X POST http://localhost:7910/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "mcp_local_dremio__GetUsefulSystemTableNames",
      "arguments": {}
    }
  }'
```

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

### Stdio Access for Claude Desktop

For applications that require stdio access (like Claude Desktop):

```bash
# Direct container execution
docker-compose exec dremio-mcp dremio-mcp-server run

# Or connect via stdio in your MCP client configuration
```

## Troubleshooting

### HTTP Endpoint Issues

```bash
# Check if HTTP endpoint is responding
curl -f http://localhost:7910/mcp -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'

# Check Supergateway logs
docker-compose logs dremio-mcp | grep -i supergateway

# Test MCP server directly via stdio
docker-compose exec dremio-mcp dremio-mcp-server run --log-level DEBUG
```

### Session State Issues

If you're experiencing issues with VS Code or HTTP clients losing session state:

```bash
# Check if stateful mode is enabled (should see --stateful in logs)
docker-compose logs dremio-mcp | grep -i stateful

# Restart with fresh session
docker-compose restart dremio-mcp
```

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

# Test internal MCP server connectivity
docker-compose exec dremio-mcp ps aux | grep -E "(supergateway|dremio-mcp)"
```

### Port Conflicts

If port 7910 is already in use:

```bash
# Check what's using the port
lsof -i :7910

# Change the port in docker-compose.yml
# Update the ports mapping: "NEW_PORT:7910"
```

## Architecture

### Single Container Architecture

The `dremio-mcp` service runs both:

- **Supergateway** (Node.js): HTTP proxy providing streamableHttp transport
- **Dremio MCP Server** (Python): Core MCP server with Dremio integration

Communication flow:

```text
HTTP Client → Supergateway (port 7910) → stdio → Dremio MCP Server
```

### Service Overview

- **dremio-mcp**: Combined MCP server with HTTP proxy (Node.js + Python)
- **token-refresher**: Automatic Dremio token management (Python)
- **token-volume**: Shared volume for secure token storage

### Transport Methods

| Transport | Use Case | Configuration |
|-----------|----------|---------------|
| streamableHttp | VS Code, web clients, MCP Inspector | `http://localhost:7910/mcp` |
| stdio | Claude Desktop, direct integration | Container stdio access |

## Security Notes

- Tokens are stored in Docker volumes, not environment variables
- Both services run as non-root users
- Docker socket access is read-only and limited to token-refresher
- Consider using Docker secrets for production deployments

## Example Usage Scenarios

### Scenario 1: Data Analysis in VS Code

1. **Start the stack:**

   ```bash
   docker-compose up -d
   ```

2. **Connect VS Code** to the MCP server (see VS Code Integration Guide above)

3. **Explore your Dremio data:**

   - Use `GetUsefulSystemTableNames` to see available system tables
   - Use `GetSchemaOfTable` to understand table structures  
   - Use `RunSqlQuery` to execute analytical queries
   - Use `GetTableOrViewLineage` to understand data dependencies

### Scenario 2: API Development with MCP Inspector

1. **Install MCP Inspector:**

   ```bash
   npm install -g @modelcontextprotocol/inspector
   ```

2. **Connect and explore:**

   ```bash
   mcp-inspector http://localhost:7910/mcp
   ```

3. **Test queries interactively** in the web interface

### Scenario 3: Claude Desktop Integration (Stdio)

1. **Configure Claude Desktop** to use stdio transport
2. **Connect to container:**

   ```bash
   docker-compose exec dremio-mcp dremio-mcp-server run
   ```
