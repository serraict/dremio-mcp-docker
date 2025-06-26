#!/bin/bash
set -e

echo "Starting Dremio MCP Server..."

# Wait for token file to be available
echo "Waiting for token file at ${DREMIO_PAT_FILE}..."
while [ ! -f "${DREMIO_PAT_FILE}" ]; do
    echo "Token file not found, waiting 5 seconds..."
    sleep 5
done

echo "Token file found, starting MCP server..."

# Start the Dremio MCP server
exec dremio-mcp-server run \
    --dremio-uri "${DREMIO_URI}" \
    --dremio-pat "@${DREMIO_PAT_FILE}" \
    ${EXTRA_ARGS}
