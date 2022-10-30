#!/bin/bash
set -e

echo "Waiting for infrastructure to initialize"
common/scripts/wait-for.sh db:5432 -t 20
common/scripts/wait-for.sh kafka:9092 -t 20
echo "Infrastructure was successfully initialized, starting service..."

# Run API worker
uvicorn accounting.asgi:app --host 0.0.0.0 --port 8080 --workers 1