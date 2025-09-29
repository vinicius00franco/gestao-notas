#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Starting container initialization..."

: "${DB_HOST:=db}"
: "${DB_PORT:=5432}"

wait_for_tcp() {
  local host="$1"; local port="$2"; local attempts=60; local sleep_s=1
  echo "[entrypoint] Waiting for ${host}:${port}..."
  for i in $(seq 1 "$attempts"); do
    if (echo > "/dev/tcp/${host}/${port}") >/dev/null 2>&1; then
      echo "[entrypoint] ${host}:${port} is up."
      return 0
    fi
    sleep "$sleep_s"
  done
  echo "[entrypoint] WARNING: ${host}:${port} not reachable after ${attempts}s; proceeding anyway." >&2
}

wait_for_tcp "$DB_HOST" "$DB_PORT" || true

PY=$(command -v python || command -v python3)
echo "[entrypoint] Applying migrations..."
"$PY" manage.py migrate --noinput

echo "[entrypoint] Collecting static files..."
"$PY" manage.py collectstatic --noinput || true

echo "[entrypoint] Starting application: $*"
exec "$@"
