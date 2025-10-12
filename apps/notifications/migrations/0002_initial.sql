-- Unified initial schema for the 'notifications' app - Notification and Device
-- This script is idempotent and can be run safely multiple times.

-- Enable the pgcrypto extension for UUID generation if it's not already enabled.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create the Notification table if it doesn't exist.
CREATE TABLE IF NOT EXISTS notifications_notification (
    ntf_id BIGSERIAL PRIMARY KEY,
    ntf_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    data JSONB,
    delivered BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    delivered_at TIMESTAMPTZ,
    user_id INTEGER NOT NULL
);

-- Add unique constraints and foreign keys for Notification if they don't already exist.
DO $$
BEGIN
    -- Add a unique constraint on the UUID field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_ntf_uuid' AND conrelid = 'notifications_notification'::regclass
    ) THEN
        ALTER TABLE notifications_notification ADD CONSTRAINT uq_ntf_uuid UNIQUE (ntf_uuid);
    END IF;

    -- Add a foreign key to the auth_user table.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_notification_user' AND conrelid = 'notifications_notification'::regclass
    ) THEN
        ALTER TABLE notifications_notification
            ADD CONSTRAINT fk_notification_user FOREIGN KEY (user_id)
            REFERENCES auth_user (id) ON DELETE CASCADE;
    END IF;
END$$;

-- Create the Device table if it doesn't exist.
CREATE TABLE IF NOT EXISTS notifications_device (
    dvc_id BIGSERIAL PRIMARY KEY,
    dvc_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    token VARCHAR(512) NOT NULL,
    platform VARCHAR(16),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    empresa_id BIGINT,
    user_id INTEGER
);

-- Add unique constraints and foreign keys for Device if they don't already exist.
DO $$
BEGIN
    -- Add a unique constraint on the token field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_dvc_token' AND conrelid = 'notifications_device'::regclass
    ) THEN
        ALTER TABLE notifications_device ADD CONSTRAINT uq_dvc_token UNIQUE (token);
    END IF;

    -- Add a unique constraint on the UUID field.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_dvc_uuid' AND conrelid = 'notifications_device'::regclass
    ) THEN
        ALTER TABLE notifications_device ADD CONSTRAINT uq_dvc_uuid UNIQUE (dvc_uuid);
    END IF;

    -- Add a foreign key to the cadastro_empresas table.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_device_empresa' AND conrelid = 'notifications_device'::regclass
    ) THEN
        ALTER TABLE notifications_device
            ADD CONSTRAINT fk_device_empresa FOREIGN KEY (empresa_id)
            REFERENCES cadastro_empresas (emp_id) ON DELETE CASCADE;
    END IF;

    -- Add a foreign key to the auth_user table.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_device_user' AND conrelid = 'notifications_device'::regclass
    ) THEN
        ALTER TABLE notifications_device
            ADD CONSTRAINT fk_device_user FOREIGN KEY (user_id)
            REFERENCES auth_user (id) ON DELETE CASCADE;
    END IF;
END$$;