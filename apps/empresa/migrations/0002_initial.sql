-- Unified initial schema for the 'empresa' app - EmpresaNaoClassificada and MinhaEmpresa
-- This script is idempotent and can be run safely multiple times.

-- Enable the pgcrypto extension for UUID generation if it's not already enabled.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create the EmpresaNaoClassificada table if it doesn't exist.
CREATE TABLE IF NOT EXISTS empresas_nao_classificadas (
    enc_id BIGSERIAL PRIMARY KEY,
    enc_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    enc_cnpj VARCHAR(18) NOT NULL,
    enc_nome_fantasia VARCHAR(255) NOT NULL,
    enc_razao_social VARCHAR(255) NOT NULL,
    enc_uf VARCHAR(2) NOT NULL,
    enc_cidade VARCHAR(255) NOT NULL,
    enc_logradouro VARCHAR(255) NOT NULL,
    enc_numero VARCHAR(255) NOT NULL,
    enc_bairro VARCHAR(255) NOT NULL,
    enc_cep VARCHAR(9) NOT NULL,
    enc_telefone VARCHAR(20) NOT NULL,
    enc_email VARCHAR(255) NOT NULL,
    enc_dt_criacao TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add unique constraints for EmpresaNaoClassificada if they don't already exist.
DO $$
BEGIN
    -- Add a unique constraint on the CNPJ field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_enc_cnpj' AND conrelid = 'empresas_nao_classificadas'::regclass
    ) THEN
        ALTER TABLE empresas_nao_classificadas ADD CONSTRAINT uq_enc_cnpj UNIQUE (enc_cnpj);
    END IF;

    -- Add a unique constraint on the UUID field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_enc_uuid' AND conrelid = 'empresas_nao_classificadas'::regclass
    ) THEN
        ALTER TABLE empresas_nao_classificadas ADD CONSTRAINT uq_enc_uuid UNIQUE (enc_uuid);
    END IF;
END$$;

-- Create the MinhaEmpresa table if it doesn't exist.
CREATE TABLE IF NOT EXISTS cadastro_empresas (
    emp_id BIGSERIAL PRIMARY KEY,
    emp_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    emp_nome VARCHAR(255) NOT NULL DEFAULT 'Minha Empresa',
    emp_cnpj VARCHAR(18) NOT NULL,
    emp_senha_hash VARCHAR(128) DEFAULT '',
    emp_dt_criacao TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    emp_dt_alteracao TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    emp_usr_criacao INTEGER,
    emp_usr_alteracao INTEGER,
    emp_dt_exclusao TIMESTAMPTZ
);

-- Add unique constraints for MinhaEmpresa if they don't already exist.
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