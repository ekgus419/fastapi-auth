#!/bin/bash

set -e

host="$1"
shift
cmd="$@"

until PGPASSWORD=$DB_PASSWORD psql -h "$host" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  >&2 echo "⏳  PostgreSQL is unavailable - sleeping  ⏳"
  sleep 1
done

>&2 echo "✅  PostgreSQL is up - executing command  ✅"
exec $cmd
