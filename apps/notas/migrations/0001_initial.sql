-- Unified initial schema for the 'notas' app
-- This script is idempotent and can be run safely multiple times.

-- Enable the pgcrypto extension for UUID generation if it's not already enabled.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create the main table for notas fiscais.
CREATE TABLE IF NOT EXISTS movimento_notas_fiscais (
    ntf_id BIGSERIAL PRIMARY KEY,
    ntf_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    ntf_chave_acesso VARCHAR(44) UNIQUE,
    ntf_numero VARCHAR(100) NOT NULL,
    ntf_data_emissao DATE NOT NULL,
    ntf_valor_total DECIMAL(12, 2) NOT NULL,
    jbp_id BIGINT NOT NULL,
    pcr_id BIGINT NOT NULL
);

-- Create the table for nota fiscal items.
CREATE TABLE IF NOT EXISTS movimento_nota_fiscal_itens (
    nfi_id BIGSERIAL PRIMARY KEY,
    nfi_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    ntf_id BIGINT NOT NULL,
    nfi_descricao VARCHAR(255) NOT NULL,
    nfi_quantidade DECIMAL(10, 3) NOT NULL,
    nfi_valor_unitario DECIMAL(10, 2) NOT NULL,
    nfi_valor_total DECIMAL(12, 2) NOT NULL
);

-- Add indexes and foreign keys if they don't already exist.
DO $$
BEGIN
    -- Add foreign key to jobs table.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_ntf_job' AND conrelid = 'movimento_notas_fiscais'::regclass
    ) THEN
        ALTER TABLE movimento_notas_fiscais
            ADD CONSTRAINT fk_ntf_job FOREIGN KEY (jbp_id)
            REFERENCES movimento_jobs_processamento (jbp_id) ON DELETE RESTRICT;
    END IF;

    -- Add foreign key to parceiros table.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_ntf_parceiro' AND conrelid = 'movimento_notas_fiscais'::regclass
    ) THEN
        ALTER TABLE movimento_notas_fiscais
            ADD CONSTRAINT fk_ntf_parceiro FOREIGN KEY (pcr_id)
            REFERENCES cadastro_parceiros (pcr_id) ON DELETE RESTRICT;
    END IF;

    -- Add foreign key to notas fiscais table.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_nfi_nota_fiscal' AND conrelid = 'movimento_nota_fiscal_itens'::regclass
    ) THEN
        ALTER TABLE movimento_nota_fiscal_itens
            ADD CONSTRAINT fk_nfi_nota_fiscal FOREIGN KEY (ntf_id)
            REFERENCES movimento_notas_fiscais (ntf_id) ON DELETE CASCADE;
    END IF;

    -- Add indexes.
    CREATE INDEX IF NOT EXISTS idx_nfi_ntf ON movimento_nota_fiscal_itens(ntf_id);
    CREATE INDEX IF NOT EXISTS idx_ntf_parc_data ON movimento_notas_fiscais(pcr_id, ntf_data_emissao);
    CREATE INDEX IF NOT EXISTS idx_ntf_parc_num ON movimento_notas_fiscais(pcr_id, ntf_numero);
    CREATE UNIQUE INDEX IF NOT EXISTS uq_ntf_parceiro_numero_when_no_chave ON movimento_notas_fiscais(pcr_id, ntf_numero) WHERE ntf_chave_acesso IS NULL;
END$$;