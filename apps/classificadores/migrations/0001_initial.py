from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            sql=(
                """
                -- Create table for classificadores (initial schema, without UUID)
                CREATE TABLE IF NOT EXISTS geral_classificadores (
                    clf_id BIGSERIAL PRIMARY KEY,
                    clf_tipo VARCHAR(50) NOT NULL,
                    clf_codigo VARCHAR(50) NOT NULL,
                    clf_descricao VARCHAR(255) NOT NULL,
                    CONSTRAINT uq_tipo_codigo UNIQUE (clf_tipo, clf_codigo)
                );
                """
            ),
            reverse_sql=(
                """
                DROP TABLE IF EXISTS geral_classificadores;
                """
            ),
        ),
    ]
