-- Unified initial schema for the 'empresa' app
-- This script is idempotent and can be run safely multiple times.

-- Enable the pgcrypto extension for UUID generation if it's not already enabled.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create the main table for the company.
CREATE TABLE IF NOT EXISTS cadastro_empresas (
    emp_id BIGSERIAL PRIMARY KEY,
    emp_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    emp_nome VARCHAR(255) NOT NULL,
    emp_cnpj VARCHAR(18) NOT NULL,
    emp_senha_hash VARCHAR(128),
    emp_dt_criacao TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    emp_dt_alteracao TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    emp_usr_criacao INTEGER,
    emp_usr_alteracao INTEGER,
    emp_dt_exclusao TIMESTAMPTZ
);

-- Add unique constraints if they don't already exist.
DO $$
BEGIN
    -- Add a unique constraint on the CNPJ field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_emp_cnpj' AND conrelid = 'cadastro_empresas'::regclass
    ) THEN
        ALTER TABLE cadastro_empresas ADD CONSTRAINT uq_emp_cnpj UNIQUE (emp_cnpj);
    END IF;

    -- Add a unique constraint on the UUID field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_emp_uuid' AND conrelid = 'cadastro_empresas'::regclass
    ) THEN
        ALTER TABLE cadastro_empresas ADD CONSTRAINT uq_emp_uuid UNIQUE (emp_uuid);
    END IF;
END$$;

-- Initialize the password hash column to an empty string where it is null.
UPDATE cadastro_empresas SET emp_senha_hash = '' WHERE emp_senha_hash IS NULL;