-- 0002_initial.sql: idempotent DDL to ensure 'geral_classificadores' exists and matches model expectations

-- Enable pgcrypto for gen_random_uuid (if not already)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Ensure table exists
CREATE TABLE IF NOT EXISTS geral_classificadores (
    clf_id BIGSERIAL PRIMARY KEY,
    clf_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    clf_tipo VARCHAR(50) NOT NULL,
    clf_codigo VARCHAR(50) NOT NULL,
    clf_descricao VARCHAR(255) NOT NULL
);

-- Ensure unique constraints exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_clf_tipo_codigo' AND conrelid = 'geral_classificadores'::regclass
    ) THEN
        ALTER TABLE geral_classificadores ADD CONSTRAINT uq_clf_tipo_codigo UNIQUE (clf_tipo, clf_codigo);
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_clf_uuid' AND conrelid = 'geral_classificadores'::regclass
    ) THEN
        ALTER TABLE geral_classificadores ADD CONSTRAINT uq_clf_uuid UNIQUE (clf_uuid);
    END IF;
END$$;
