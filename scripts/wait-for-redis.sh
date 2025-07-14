#!/bin/sh

# Redis 호스트와 포트 설정 (기본값: redis:6379)
HOST="${1:-redis}"
PORT="${2:-6379}"

echo "⏳ Waiting for Redis at $HOST:$PORT... ⏳"

while ! nc -z $HOST $PORT; do
  sleep 1
done

echo "✅ Redis is available at $HOST:$PORT ✅"
