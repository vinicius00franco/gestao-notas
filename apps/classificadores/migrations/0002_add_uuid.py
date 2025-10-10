from django.db import migrations


sql = """
-- Ensure pgcrypto for gen_random_uuid
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Add UUID column if not exists and unique constraint
ALTER TABLE geral_classificadores
    ADD COLUMN IF NOT EXISTS clf_uuid uuid DEFAULT gen_random_uuid();

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_clf_uuid'
    ) THEN
        ALTER TABLE geral_classificadores
            ADD CONSTRAINT uq_clf_uuid UNIQUE (clf_uuid);
    END IF;
END$$;
"""


class Migration(migrations.Migration):

        dependencies = [
                ('classificadores', '0001_initial'),
        ]

        operations = [
                migrations.RunSQL(sql, reverse_sql=(
                        "ALTER TABLE IF EXISTS geral_classificadores DROP CONSTRAINT IF EXISTS uq_clf_uuid;\n"
                        "ALTER TABLE IF EXISTS geral_classificadores DROP COLUMN IF EXISTS clf_uuid;"
                )),
        ]
