-- Unified initial schema for the 'notas' app - NotaFiscal and NotaFiscalItem
-- This script is idempotent and can be run safely multiple times.

-- Enable the pgcrypto extension for UUID generation if it's not already enabled.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create the NotaFiscal table if it doesn't exist.
CREATE TABLE IF NOT EXISTS movimento_notas_fiscais (
    ntf_id BIGSERIAL PRIMARY KEY,
    ntf_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    ntf_chave_acesso VARCHAR(44),
    ntf_numero VARCHAR(100) NOT NULL,
    ntf_data_emissao DATE NOT NULL,
    ntf_valor_total DECIMAL(12, 2) NOT NULL,
    jbp_id BIGINT NOT NULL,
    pcr_id BIGINT NOT NULL
);

-- Add unique constraints and foreign keys for NotaFiscal if they don't already exist.
DO $$
BEGIN
    -- Add a unique constraint on the UUID field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_ntf_uuid' AND conrelid = 'movimento_notas_fiscais'::regclass
    ) THEN
        ALTER TABLE movimento_notas_fiscais ADD CONSTRAINT uq_ntf_uuid UNIQUE (ntf_uuid);
    END IF;

    -- Add a unique constraint on the chave_acesso field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_ntf_chave_acesso' AND conrelid = 'movimento_notas_fiscais'::regclass
    ) THEN
        ALTER TABLE movimento_notas_fiscais ADD CONSTRAINT uq_ntf_chave_acesso UNIQUE (ntf_chave_acesso);
    END IF;

    -- Add a foreign key to the movimento_jobs_processamento table.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_ntf_job_origem' AND conrelid = 'movimento_notas_fiscais'::regclass
    ) THEN
        ALTER TABLE movimento_notas_fiscais
            ADD CONSTRAINT fk_ntf_job_origem FOREIGN KEY (jbp_id)
            REFERENCES movimento_jobs_processamento (jbp_id) ON DELETE RESTRICT;
    END IF;

    -- Add a foreign key to the cadastro_parceiros table.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_ntf_parceiro' AND conrelid = 'movimento_notas_fiscais'::regclass
    ) THEN
        ALTER TABLE movimento_notas_fiscais
            ADD CONSTRAINT fk_ntf_parceiro FOREIGN KEY (pcr_id)
            REFERENCES cadastro_parceiros (pcr_id) ON DELETE RESTRICT;
    END IF;
END$$;

-- Create the NotaFiscalItem table if it doesn't exist.
CREATE TABLE IF NOT EXISTS movimento_nota_fiscal_itens (
    nfi_id BIGSERIAL PRIMARY KEY,
    nfi_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    nfi_descricao VARCHAR(255) NOT NULL,
    nfi_quantidade DECIMAL(10, 3) NOT NULL,
    nfi_valor_unitario DECIMAL(10, 2) NOT NULL,
    nfi_valor_total DECIMAL(12, 2) NOT NULL,
    ntf_id BIGINT NOT NULL
);

-- Add unique constraints and foreign keys for NotaFiscalItem if they don't already exist.
DO $$
BEGIN
    -- Add a unique constraint on the UUID field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_nfi_uuid' AND conrelid = 'movimento_nota_fiscal_itens'::regclass
    ) THEN
        ALTER TABLE movimento_nota_fiscal_itens ADD CONSTRAINT uq_nfi_uuid UNIQUE (nfi_uuid);
    END IF;

    -- Add a foreign key to the movimento_notas_fiscais table.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_nfi_nota_fiscal' AND conrelid = 'movimento_nota_fiscal_itens'::regclass
    ) THEN
        ALTER TABLE movimento_nota_fiscal_itens
            ADD CONSTRAINT fk_nfi_nota_fiscal FOREIGN KEY (ntf_id)
            REFERENCES movimento_notas_fiscais (ntf_id) ON DELETE CASCADE;
    END IF;
END$$;

-- Create indexes if they don't exist.
DO $$
BEGIN
    -- Index on nota_fiscal for NotaFiscalItem
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'movimento_nota_fiscal_itens' AND indexname = 'idx_nfi_ntf'
    ) THEN
        CREATE INDEX idx_nfi_ntf ON movimento_nota_fiscal_itens (ntf_id);
    END IF;

    -- Index on parceiro, data_emissao for NotaFiscal
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'movimento_notas_fiscais' AND indexname = 'idx_ntf_parc_data'
    ) THEN
        CREATE INDEX idx_ntf_parc_data ON movimento_notas_fiscais (pcr_id, ntf_data_emissao);
    END IF;

    -- Index on parceiro, numero for NotaFiscal
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'movimento_notas_fiscais' AND indexname = 'idx_ntf_parc_num'
    ) THEN
        CREATE INDEX idx_ntf_parc_num ON movimento_notas_fiscais (pcr_id, ntf_numero);
    END IF;
END$$;

-- Add unique constraint with condition (partial unique index)
DO $$
BEGIN
    -- Unique constraint for parceiro, numero when chave_acesso is null
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'movimento_notas_fiscais' AND indexname = 'uq_ntf_parceiro_numero_when_no_chave'
    ) THEN
        CREATE UNIQUE INDEX uq_ntf_parceiro_numero_when_no_chave
        ON movimento_notas_fiscais (pcr_id, ntf_numero)
        WHERE ntf_chave_acesso IS NULL;
    END IF;
END$$;