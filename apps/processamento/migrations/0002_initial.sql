-- Unified initial schema for the 'processamento' app - JobProcessamento
-- This script is idempotent and can be run safely multiple times.

-- Enable the pgcrypto extension for UUID generation if it's not already enabled.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create the JobProcessamento table if it doesn't exist.
CREATE TABLE IF NOT EXISTS movimento_jobs_processamento (
    jbp_id BIGSERIAL PRIMARY KEY,
    jbp_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    jbp_arquivo_original VARCHAR(255) NOT NULL,
    jbp_dt_criacao TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    jbp_dt_alteracao TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    jbp_usr_criacao INTEGER,
    jbp_usr_alteracao INTEGER,
    jbp_dt_conclusao TIMESTAMPTZ,
    jbp_mensagem_erro TEXT,
    emp_id BIGINT,
    clf_id_status BIGINT NOT NULL
);

-- Add unique constraints and foreign keys if they don't already exist.
DO $$
BEGIN
    -- Add a unique constraint on the UUID field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_jbp_uuid' AND conrelid = 'movimento_jobs_processamento'::regclass
    ) THEN
        ALTER TABLE movimento_jobs_processamento ADD CONSTRAINT uq_jbp_uuid UNIQUE (jbp_uuid);
    END IF;

    -- Add a foreign key to the cadastro_empresas table.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_job_empresa' AND conrelid = 'movimento_jobs_processamento'::regclass
    ) THEN
        ALTER TABLE movimento_jobs_processamento
            ADD CONSTRAINT fk_job_empresa FOREIGN KEY (emp_id)
            REFERENCES cadastro_empresas (emp_id) ON DELETE RESTRICT;
    END IF;

    -- Add a foreign key to the geral_classificadores table.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_job_status' AND conrelid = 'movimento_jobs_processamento'::regclass
    ) THEN
        ALTER TABLE movimento_jobs_processamento
            ADD CONSTRAINT fk_job_status FOREIGN KEY (clf_id_status)
            REFERENCES geral_classificadores (clf_id) ON DELETE RESTRICT;
    END IF;
END$$;