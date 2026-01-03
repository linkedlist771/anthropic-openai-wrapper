#!/bin/bash
# restart_zero_downtime.sh
# Performs a zero-downtime graceful reload of the Gunicorn server
# This spawns new workers, waits for them to be ready, then gracefully shuts down old workers

set -e

CONTAINER_NAME="anth2oai_server"
PID_FILE="/tmp/gunicorn.pid"

echo "🔄 Initiating zero-downtime restart..."

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Error: Container '${CONTAINER_NAME}' is not running"
    echo "   Start it with: docker-compose up -d"
    exit 1
fi

# Send HUP signal to Gunicorn master process for graceful reload
echo "📤 Sending HUP signal to Gunicorn master process..."
docker exec "${CONTAINER_NAME}" sh -c "kill -HUP \$(cat ${PID_FILE})"

if [ $? -eq 0 ]; then
    echo "✅ Graceful reload triggered successfully!"
    echo ""
    echo "   Gunicorn will:"
    echo "   1. Spawn new workers with updated code"
    echo "   2. Wait for new workers to be ready"
    echo "   3. Gracefully shutdown old workers (finishing existing requests)"
    echo ""
    echo "📋 Monitor logs with: docker logs -f ${CONTAINER_NAME}"
else
    echo "❌ Failed to send reload signal"
    exit 1
fi

