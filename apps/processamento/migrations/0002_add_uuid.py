from django.db import migrations


sql = """
CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE movimento_jobs_processamento
    ADD COLUMN IF NOT EXISTS jbp_uuid uuid DEFAULT gen_random_uuid();

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_jbp_uuid'
    ) THEN
        ALTER TABLE movimento_jobs_processamento
            ADD CONSTRAINT uq_jbp_uuid UNIQUE (jbp_uuid);
    END IF;
END$$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('processamento', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(sql, reverse_sql=(
            "ALTER TABLE IF EXISTS movimento_jobs_processamento DROP CONSTRAINT IF EXISTS uq_jbp_uuid;\n"
            "ALTER TABLE IF EXISTS movimento_jobs_processamento DROP COLUMN IF EXISTS jbp_uuid;"
        )),
    ]
