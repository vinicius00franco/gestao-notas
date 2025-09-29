#!/usr/bin/env bash
#set -euo pipefail

# Script to create DB user and database using env vars or provided values.
# It supports running inside Docker (exec into postgres_db) or locally via psql.

DB_NAME=${DB_NAME:-gestao_notas_db}
DB_USER=${DB_USER:-vinicius}
DB_PASSWORD=${DB_PASSWORD:-BENEF}

# Defaults for local psql (can be overridden)
PG_SUPERUSER=${PG_SUPERUSER:-postgres}
PG_SUPERPASS=${PG_SUPERPASS:-postgres}
PG_HOST=${PG_HOST:-localhost}
PG_PORT=${PG_PORT:-5432}

set -euo pipefail

echo "Create DB user script: DB_NAME=${DB_NAME}, DB_USER=${DB_USER}, DB_HOST=${PG_HOST}:${PG_PORT}"

# If docker container exists, try to read its POSTGRES_USER/POSTGRES_PASSWORD to use as superuser creds
if docker ps --format '{{.Names}}' | grep -q '^postgres_db$'; then
  echo "Detected running container 'postgres_db'"
  # try to read env vars from container
  CONTAINER_PG_USER=$(docker exec postgres_db printenv POSTGRES_USER 2>/dev/null || true)
  CONTAINER_PG_PASS=$(docker exec postgres_db printenv POSTGRES_PASSWORD 2>/dev/null || true)
  if [ -n "$CONTAINER_PG_USER" ]; then
    PG_SUPERUSER="$CONTAINER_PG_USER"
    echo "Using container POSTGRES_USER=$PG_SUPERUSER"
  fi
  if [ -n "$CONTAINER_PG_PASS" ]; then
    PG_SUPERPASS="$CONTAINER_PG_PASS"
    echo "Using container POSTGRES_PASSWORD (hidden)"
  fi
fi

# Helper to run a psql command and return output
psql_exec() {
  local sql="$1"
  if docker ps --format '{{.Names}}' | grep -q '^postgres_db$'; then
    docker exec -e PGPASSWORD="$PG_SUPERPASS" postgres_db psql -U "$PG_SUPERUSER" -d postgres -tAc "$sql"
  else
    PGPASSWORD="$PG_SUPERPASS" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_SUPERUSER" -d postgres -tAc "$sql"
  fi
}

# Check if role exists
exists=$(psql_exec "SELECT 1 FROM pg_roles WHERE rolname = '$DB_USER';" || true)
if [ -z "$(echo "$exists" | tr -d '[:space:]')" ]; then
  echo "Role $DB_USER does not exist -> creating"
  if docker ps --format '{{.Names}}' | grep -q '^postgres_db$'; then
    docker exec -e PGPASSWORD="$PG_SUPERPASS" postgres_db psql -U "$PG_SUPERUSER" -d postgres -c "CREATE ROLE \"$DB_USER\" LOGIN PASSWORD '$DB_PASSWORD';"
  else
    PGPASSWORD="$PG_SUPERPASS" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_SUPERUSER" -d postgres -c "CREATE ROLE \"$DB_USER\" LOGIN PASSWORD '$DB_PASSWORD';"
  fi
else
  echo "Role $DB_USER already exists"
fi

# Check if database exists
db_exists=$(psql_exec "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME';" || true)
if [ -z "$(echo "$db_exists" | tr -d '[:space:]')" ]; then
  echo "Database $DB_NAME does not exist -> creating owned by $DB_USER"
  if docker ps --format '{{.Names}}' | grep -q '^postgres_db$'; then
    docker exec -e PGPASSWORD="$PG_SUPERPASS" postgres_db psql -U "$PG_SUPERUSER" -d postgres -c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_USER\";"
  else
    PGPASSWORD="$PG_SUPERPASS" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_SUPERUSER" -d postgres -c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_USER\";"
  fi
else
  echo "Database $DB_NAME already exists"
fi

echo "Granting privileges on $DB_NAME to $DB_USER"
if docker ps --format '{{.Names}}' | grep -q '^postgres_db$'; then
  docker exec -e PGPASSWORD="$PG_SUPERPASS" postgres_db psql -U "$PG_SUPERUSER" -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE \"$DB_NAME\" TO \"$DB_USER\";"
else
  PGPASSWORD="$PG_SUPERPASS" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_SUPERUSER" -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE \"$DB_NAME\" TO \"$DB_USER\";"
fi

echo "Done. Make sure your .env points to: DB_NAME=$DB_NAME DB_USER=$DB_USER DB_PASSWORD=$DB_PASSWORD DB_HOST=${PG_HOST} DB_PORT=$PG_PORT"
