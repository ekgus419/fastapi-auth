#!/bin/bash

host="$1"
port="${2:-5672}"

until nc -z "$host" "$port"; do
  echo "🕐  Waiting for RabbitMQ at $host:$port...  🕐"
  sleep 2
done

echo "✅  RabbitMQ is up - executing command  ✅"
exec "${@:3}"
