-- Unified initial schema for the 'parceiros' app - Parceiro
-- This script is idempotent and can be run safely multiple times.

-- Enable the pgcrypto extension for UUID generation if it's not already enabled.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create the Parceiro table if it doesn't exist.
CREATE TABLE IF NOT EXISTS cadastro_parceiros (
    pcr_id BIGSERIAL PRIMARY KEY,
    pcr_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    pcr_nome VARCHAR(255) NOT NULL,
    pcr_cnpj VARCHAR(18) NOT NULL,
    clf_id_tipo BIGINT NOT NULL
);

-- Add unique constraints and foreign keys if they don't already exist.
DO $$
BEGIN
    -- Add a unique constraint on the CNPJ field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_pcr_cnpj' AND conrelid = 'cadastro_parceiros'::regclass
    ) THEN
        ALTER TABLE cadastro_parceiros ADD CONSTRAINT uq_pcr_cnpj UNIQUE (pcr_cnpj);
    END IF;

    -- Add a unique constraint on the UUID field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_pcr_uuid' AND conrelid = 'cadastro_parceiros'::regclass
    ) THEN
        ALTER TABLE cadastro_parceiros ADD CONSTRAINT uq_pcr_uuid UNIQUE (pcr_uuid);
    END IF;

    -- Add a foreign key to the geral_classificadores table.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_parceiro_tipo' AND conrelid = 'cadastro_parceiros'::regclass
    ) THEN
        ALTER TABLE cadastro_parceiros
            ADD CONSTRAINT fk_parceiro_tipo FOREIGN KEY (clf_id_tipo)
            REFERENCES geral_classificadores (clf_id) ON DELETE RESTRICT;
    END IF;
END$$;