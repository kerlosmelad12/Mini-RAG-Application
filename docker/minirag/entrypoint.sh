#!/bin/bash
set -e

echo "Running database migrations..."
cd /app/models/DB_Schemas/minirag/
alembic upgrade head
cd /app

# Hand off execution to the CMD from Dockerfile/docker-compose
exec "$@"