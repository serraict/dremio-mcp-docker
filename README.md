# Dremio MCP Docker Deployment

Quick start guide for deploying Dremio MCP Server with Docker.

## Prerequisites

- Docker and Docker Compose
- Access to a Dremio server with username/password authentication
- Network connectivity between containers and Dremio server

## Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/serraict/dremio-mcp-docker.git
   cd dremio-mcp-docker
   ```

2. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your Dremio connection details
   ```

3. **Deploy**

   ```bash
   docker compose up -d
   ```

4. **Connect your MCP client**

   - URL: `http://localhost:7910/mcp`
   - Transport: `streamableHttp` (event-stream format)
   - Session timeout: 60 seconds

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
   docker compose up -d
   # Verify HTTP endpoint is accessible
   curl -f http://localhost:7910/mcp
   ```

### Setup Steps

#### Option 1: Using VS Code with Github CoPilot

**Add server configuration** to your VS Code settings:

   **Global settings** (`settings.json`):

   ```json
   {
      ...
      "mcp": {
         "servers": {
            "local dremio with supergateway": {
               "url": "http://localhost:7910/mcp/"
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

## Architecture

### MCP container

The `dremio-mcp` service runs both:

- **Supergateway** (Node.js): HTTP proxy providing `streamableHttp` transport
- **Dremio MCP Server** (Python): Core MCP server with Dremio integration

Communication flow:

```text
HTTP Client → Supergateway (port 7910) → stdio → Dremio MCP Server
```

### Service Overview

- **dremio-mcp**: Combined MCP server with HTTP proxy (Node.js + Python)
- **token-refresher**: Automatic Dremio token management (Python)
- **token-volume**: Shared volume for secure token storage

## Example Usage Scenarios

### Data Analysis in VS Code

1. **Start the stack:**

   ```bash
   docker compose up -d
   ```

2. **Connect VS Code** to the MCP server (see VS Code Integration Guide above)

3. **Explore your Dremio data:**

   - Use `GetUsefulSystemTableNames` to see available system tables
   - Use `GetSchemaOfTable` to understand table structures  
   - Use `RunSqlQuery` to execute analytical queries
   - Use `GetTableOrViewLineage` to understand data dependencies

### Add your scenario here

Share how you use `dremio-mcp-docker`!
