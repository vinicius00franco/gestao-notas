-- This script runs automatically on first container init
-- It creates a dedicated role and database for the Django API.
-- Uses default POSTGRES_* envs for superuser provided by .env.db

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT FROM pg_roles WHERE rolname = 'gestaonotas'
  ) THEN
    CREATE ROLE gestaonotas LOGIN PASSWORD 'gestaonotas_pwd';
  END IF;
END
$$;

-- Create database if not exists, owned by the app role
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'gestaonotas'
  ) THEN
    CREATE DATABASE gestaonotas OWNER gestaonotas;
  END IF;
END
$$;

-- Grant privileges (idempotent)
GRANT ALL PRIVILEGES ON DATABASE gestaonotas TO gestaonotas;
