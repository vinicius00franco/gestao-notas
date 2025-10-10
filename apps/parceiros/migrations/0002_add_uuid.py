from django.db import migrations


sql = """
-- Ensure pgcrypto for gen_random_uuid
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Add UUID column if not exists and unique constraint
ALTER TABLE cadastro_parceiros
    ADD COLUMN IF NOT EXISTS pcr_uuid uuid DEFAULT gen_random_uuid();

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_pcr_uuid'
    ) THEN
        ALTER TABLE cadastro_parceiros
            ADD CONSTRAINT uq_pcr_uuid UNIQUE (pcr_uuid);
    END IF;
END$$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('parceiros', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql=(
            "ALTER TABLE IF EXISTS cadastro_parceiros DROP CONSTRAINT IF EXISTS uq_pcr_uuid;\n"
            "ALTER TABLE IF EXISTS cadastro_parceiros DROP COLUMN IF EXISTS pcr_uuid;"
        )),
    ]
