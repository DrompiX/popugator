#!/bin/bash
set -e

echo "Waiting for infrastructure to initialize"
/app/common/scripts/wait-for.sh db:5432 -t 20
echo "Infrastructure was successfully initialized, starting service..."

# Run everything passed via docker command
exec "$@"