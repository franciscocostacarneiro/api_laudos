#!/bin/bash
# Health check script for container orchestration
# Used by Docker, Kubernetes, etc.

set -e

HEALTH_CHECK_URL="${HEALTH_CHECK_URL:-http://localhost:8000/health}"
TIMEOUT="${TIMEOUT:-10}"

# Try to call the health endpoint
if timeout "$TIMEOUT" curl -f -s "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
    echo "✓ Health check passed"
    exit 0
else
    echo "✗ Health check failed"
    exit 1
fi
