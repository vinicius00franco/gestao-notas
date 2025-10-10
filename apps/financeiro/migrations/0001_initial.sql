-- Unified initial schema for the 'financeiro' app
-- This script is idempotent and can be run safely multiple times.

-- Enable the pgcrypto extension for UUID generation if it's not already enabled.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create the main table for lancamentos financeiros.
CREATE TABLE IF NOT EXISTS movimento_lancamentos_financeiros (
    lcf_id BIGSERIAL PRIMARY KEY,
    lcf_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    ntf_id BIGINT UNIQUE,
    lcf_descricao VARCHAR(255) NOT NULL,
    lcf_valor DECIMAL(10, 2) NOT NULL,
    clf_id_tipo BIGINT NOT NULL,
    clf_id_status BIGINT NOT NULL,
    lcf_data_vencimento DATE NOT NULL,
    lcf_data_pagamento DATE,
    lcf_dt_criacao TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    lcf_dt_alteracao TIMESTAMptZ NOT NULL DEFAULT NOW(),
    lcf_usr_criacao INTEGER,
    lcf_usr_alteracao INTEGER
);

-- Add unique constraints and foreign keys if they don't already exist.
DO $$
BEGIN
    -- Add a unique constraint on the UUID field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_lcf_uuid' AND conrelid = 'movimento_lancamentos_financeiros'::regclass
    ) THEN
        ALTER TABLE movimento_lancamentos_financeiros ADD CONSTRAINT uq_lcf_uuid UNIQUE (lcf_uuid);
    END IF;

    -- Add a foreign key to the notas_fiscais table.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_lcf_nota_fiscal' AND conrelid = 'movimento_lancamentos_financeiros'::regclass
    ) THEN
        ALTER TABLE movimento_lancamentos_financeiros
            ADD CONSTRAINT fk_lcf_nota_fiscal FOREIGN KEY (ntf_id)
            REFERENCES movimento_notas_fiscais (ntf_id) ON DELETE CASCADE;
    END IF;

    -- Add a foreign key to the geral_classificadores table for tipo.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_lcf_tipo' AND conrelid = 'movimento_lancamentos_financeiros'::regclass
    ) THEN
        ALTER TABLE movimento_lancamentos_financeiros
            ADD CONSTRAINT fk_lcf_tipo FOREIGN KEY (clf_id_tipo)
            REFERENCES geral_classificadores (clf_id) ON DELETE RESTRICT;
    END IF;

    -- Add a foreign key to the geral_classificadores table for status.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_lcf_status' AND conrelid = 'movimento_lancamentos_financeiros'::regclass
    ) THEN
        ALTER TABLE movimento_lancamentos_financeiros
            ADD CONSTRAINT fk_lcf_status FOREIGN KEY (clf_id_status)
            REFERENCES geral_classificadores (clf_id) ON DELETE RESTRICT;
    END IF;
END$$;