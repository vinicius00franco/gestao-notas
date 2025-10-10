# Generated migration to add partial unique index for (parceiro, numero) when chave_acesso IS NULL
from django.db import migrations


class Migration(migrations.Migration):

    # Depend on the last generated migration for the app
    dependencies = [
        ('notas', '0003_notafiscal_chave_acesso_notafiscal_idx_ntf_parc_data_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "-- Create a partial unique index for (parceiro, numero) when chave_acesso IS NULL\n"
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_ntf_parc_num_partial "
                "ON movimento_notas_fiscais (pcr_id, ntf_numero) WHERE ntf_chave_acesso IS NULL;"
            ),
            reverse_sql=(
                "-- Drop the partial unique index if it exists\n"
                "DROP INDEX IF EXISTS uq_ntf_parc_num_partial;"
            ),
        )
    ]
