#!/bin/bash
set -e

echo "Starting Dremio Token Refresher..."

# Validate required environment variables
required_vars=("DREMIO_URI" "DREMIO_USERNAME" "DREMIO_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Required environment variable $var is not set"
        exit 1
    fi
done

echo "Environment validated, starting token refresh daemon..."

# Start the token refresher
exec python /app/refresh-token.py "$@"
