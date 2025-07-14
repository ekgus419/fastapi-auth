#!/bin/sh

HOST="${1:-backend}"
PORT="${2:-8000}"

echo "⏳ Waiting for backend at $HOST:$PORT... ⏳"

while ! nc -z $HOST $PORT; do
  sleep 1
done

echo "✅ Backend is available at $HOST:$PORT ✅"

shift 2
exec "$@"
