#!/bin/bash
set -e

# Port binding logic for Railway
PORT="${PORT:-8000}"

echo "Starting backend on port $PORT..."

# Optional: Run migrations if needed
# alembic upgrade head

# Start Gunicorn with Uvicorn workers
exec gunicorn app.main:app \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --access-logformat '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"' \
    --access-logfile -
