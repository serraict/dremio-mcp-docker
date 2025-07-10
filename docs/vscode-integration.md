# VS Code Integration Guide

This guide covers how to integrate the Dremio MCP Docker setup with VS Code and other MCP-compatible clients.

## Prerequisites

1. **Ensure the Dremio MCP Docker stack is running:**

   ```bash
   docker compose up -d
   # Verify HTTP endpoint is accessible
   curl -f http://localhost:7910/mcp
   ```

## VS Code Setup

### Option 1: Using VS Code with GitHub Copilot

Add server configuration to your VS Code settings:

**Global settings** (`settings.json`):

```json
{
   "mcp": {
      "servers": {
         "dremio-local": {
            "url": "http://localhost:7910/mcp/"
         }
      }
   }
}
```

### Option 2: Manual Integration via Extensions

If using a third-party MCP extension or custom integration:

1. **Configure HTTP endpoint:** `http://localhost:7910/mcp`
2. **Transport type:** streamableHttp or event-stream  
3. **Session timeout:** 60 seconds (automatic)

## Testing the Connection

Once configured, you should be able to use MCP tools in your AI conversations:

- `RunSqlQuery` - Execute SELECT queries on Dremio
- `GetSchemaOfTable` - Get table schema information
- `GetTableOrViewLineage` - Find data lineage relationships
- `GetDescriptionOfTableOrSchema` - Get descriptions and tags
- `GetUsefulSystemTableNames` - List system tables

## Example Usage

Ask your AI agent to:
- "Show me what sample data is available"
- "What's the structure of the NYC weather data?"
- "Run a query to analyze temperature trends"

## Troubleshooting

### MCP Server Not Responding
- Check if Docker services are running: `docker compose ps`
- Verify endpoint is accessible: `curl -f http://localhost:7910/mcp`
- Check MCP server logs: `docker compose logs dremio-mcp`

### Connection Refused
- Ensure ports 7910 is not blocked by firewall
- Verify VS Code settings are correct
- Restart VS Code after configuration changes
