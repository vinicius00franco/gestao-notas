from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classificadores', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                """
                -- Create parceiros table
                CREATE TABLE IF NOT EXISTS cadastro_parceiros (
                    pcr_id BIGSERIAL PRIMARY KEY,
                    pcr_nome VARCHAR(255) NOT NULL,
                    pcr_cnpj VARCHAR(18) NOT NULL UNIQUE,
                    clf_id_tipo BIGINT NOT NULL,
                    CONSTRAINT fk_parceiro_tipo FOREIGN KEY (clf_id_tipo)
                        REFERENCES geral_classificadores (clf_id)
                        ON DELETE RESTRICT
                );
                """
            ),
            reverse_sql=(
                """
                DROP TABLE IF EXISTS cadastro_parceiros;
                """
            ),
        ),
    ]
