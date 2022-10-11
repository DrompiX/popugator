#!/bin/bash
set -e

echo "Waiting for infrastructure to initialize"
/app/common/scripts/wait-for.sh db:5432 -t 20
/app/common/scripts/wait-for.sh kafka1:9094 -t 1000
echo "Infrastructure was successfully initialized, starting service..."

# Run API worker
PYTHONPATH=gateway/app:$PYTHONPATH uvicorn gateway.app.asgi:app --host 0.0.0.0 --port 8080 --workers 1