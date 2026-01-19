#!/bin/sh
# entrypoint.sh
# Support zero down-time restart
mkdir /workspace
cd /workspace

mkdir -p logs

echo "Starting with Gunicorn (zero-downtime reload supported)..."
echo "  - Graceful reload: kill -HUP \$(cat /tmp/gunicorn.pid)"
echo ""
exec gunicorn anth2oai.server.app:app -c gunicorn.conf.py

# exec gunicorn server.app:app -c gunicorn.conf.py
