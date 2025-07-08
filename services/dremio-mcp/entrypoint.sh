#!/bin/bash
set -e

echo "Starting Dremio MCP Server with Supergateway HTTP proxy..."

# Wait for token file to be available
echo "Waiting for token file at ${DREMIO_PAT_FILE}..."
while [ ! -f "${DREMIO_PAT_FILE}" ]; do
    echo "Token file not found, waiting 5 seconds..."
    sleep 5
done

echo "Token file found, starting MCP server with HTTP proxy..."

# Read the token
DREMIO_TOKEN=$(cat "${DREMIO_PAT_FILE}")
echo "Token read successfully (length: ${#DREMIO_TOKEN} characters)"

# Ensure the config directory exists and create a proper config file
mkdir -p /home/mcp/.config/dremioai

# Create a proper config file with the actual token
cat > /home/mcp/.config/dremioai/config.yaml << EOF
dremio:
  uri: "${DREMIO_URI}"
  pat: "${DREMIO_TOKEN}"
tools:
  server_mode: FOR_DATA_PATTERNS
EOF

echo "Config file created successfully"

# Start Supergateway with Dremio MCP as stdio backend
echo "Starting Supergateway on port 7910 with Dremio MCP backend..."
exec npx -y supergateway \
    --stdio "dremio-mcp-server run -c /home/mcp/.config/dremioai/config.yaml ${EXTRA_ARGS}" \
    --outputTransport streamableHttp \
    --stateful \
    --sessionTimeout 60000 \
    --port 7910 \
    --streamableHttpPath /mcp \
    --logLevel info