-- Unified initial schema for the 'classificadores' app
-- This script is idempotent and can be run safely multiple times.

-- Enable the pgcrypto extension for UUID generation if it's not already enabled.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create the main table for classifiers.
CREATE TABLE IF NOT EXISTS geral_classificadores (
    clf_id BIGSERIAL PRIMARY KEY,
    clf_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    clf_tipo VARCHAR(50) NOT NULL,
    clf_codigo VARCHAR(50) NOT NULL,
    clf_descricao VARCHAR(255) NOT NULL
);

-- Add unique constraints if they don't already exist.
DO $$
BEGIN
    -- Add a unique constraint on the combination of tipo and codigo.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_clf_tipo_codigo' AND conrelid = 'geral_classificadores'::regclass
    ) THEN
        ALTER TABLE geral_classificadores ADD CONSTRAINT uq_clf_tipo_codigo UNIQUE (clf_tipo, clf_codigo);
    END IF;

    -- Add a unique constraint on the UUID field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_clf_uuid' AND conrelid = 'geral_classificadores'::regclass
    ) THEN
        ALTER TABLE geral_classificadores ADD CONSTRAINT uq_clf_uuid UNIQUE (clf_uuid);
    END IF;
END$$;