#!/bin/bash
set -e

echo "Waiting for infrastructure to initialize"
common/scripts/wait-for.sh db:5432 -t 20
common/scripts/wait-for.sh kafka1:9094 -t 20
echo "Infrastructure was successfully initialized, starting service..."

# Run API worker
uvicorn analytics.asgi:app --host 0.0.0.0 --port 8080 --workers 1