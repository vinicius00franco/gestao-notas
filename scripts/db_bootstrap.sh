#!/usr/bin/env bash
set -euo pipefail

# Cria usuário e banco dedicados para a API quando usando Postgres local
# Requer um superuser (ex.: postgres) com acesso via psql

APP_DB_NAME=${APP_DB_NAME:-gestaonotas}
APP_DB_USER=${APP_DB_USER:-gestaonotas}
APP_DB_PASS=${APP_DB_PASS:-gestaonotas_pwd}
PGHOST=${PGHOST:-localhost}
PGPORT=${PGPORT:-5432}
PGUSER=${PGUSER:-postgres}

if ! command -v psql >/dev/null 2>&1; then
  echo "psql não encontrado. Instale o cliente do Postgres." >&2
  exit 1
fi

echo "Criando role '${APP_DB_USER}' e database '${APP_DB_NAME}' (se não existirem)..."
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -v ON_ERROR_STOP=1 <<SQL
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${APP_DB_USER}') THEN
    CREATE ROLE ${APP_DB_USER} LOGIN PASSWORD '${APP_DB_PASS}';
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${APP_DB_NAME}') THEN
    CREATE DATABASE ${APP_DB_NAME} OWNER ${APP_DB_USER};
  END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE ${APP_DB_NAME} TO ${APP_DB_USER};
SQL

echo "OK. Configure seu .env com:\nDB_NAME=${APP_DB_NAME}\nDB_USER=${APP_DB_USER}\nDB_PASSWORD=${APP_DB_PASS}\nDB_HOST=${PGHOST}\nDB_PORT=${PGPORT}"
