#!/usr/bin/env bash
set -euo pipefail

# This script runs in the Postgres container on first init (via /docker-entrypoint-initdb.d)
# It uses env vars provided to the container: DB_NAME, DB_USER, DB_PASSWORD

DB_NAME=${DB_NAME:-gestaonotas}
DB_USER=${DB_USER:-gestaonotas}
DB_PASSWORD=${DB_PASSWORD:-gestaonotas_pwd}

export PGPASSWORD="$POSTGRES_PASSWORD"

# Create role if not exists
if ! psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
  echo "Creating role $DB_USER"
  psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres -c "CREATE ROLE \"$DB_USER\" LOGIN PASSWORD '$DB_PASSWORD';"
else
  echo "Role $DB_USER already exists"
fi

# Create database if not exists (cannot run CREATE DATABASE inside DO $$, so run plain)
if ! psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
  echo "Creating database $DB_NAME owned by $DB_USER"
  psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_USER\";"
else
  echo "Database $DB_NAME already exists"
fi

# Grant privileges
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE \"$DB_NAME\" TO \"$DB_USER\";"

exit 0
