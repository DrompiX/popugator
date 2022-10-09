#!/bin/bash
set -e

echo "Waiting for infrastructure to initialize"
/app/common/scripts/wait-for.sh db:5432 -t 20
echo "Infrastructure was successfully initialized, starting service..."

cd gateway/app

# Run API worker
uvicorn asgi:app --host 0.0.0.0 --port 8080 --workers 1