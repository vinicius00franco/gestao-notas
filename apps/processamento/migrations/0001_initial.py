from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('empresa', '0001_initial'),
        ('classificadores', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                """
                -- Create table for processamento jobs
                CREATE TABLE IF NOT EXISTS movimento_jobs_processamento (
                    jbp_id BIGSERIAL PRIMARY KEY,
                    jbp_arquivo_original VARCHAR(255) NOT NULL,
                    emp_id BIGINT NOT NULL,
                    clf_id_status BIGINT NOT NULL,
                    jbp_dt_criacao TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    jbp_dt_alteracao TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    jbp_usr_criacao INTEGER NULL,
                    jbp_usr_alteracao INTEGER NULL,
                    jbp_dt_conclusao TIMESTAMP WITH TIME ZONE NULL,
                    jbp_mensagem_erro TEXT NULL,
                    CONSTRAINT fk_job_empresa FOREIGN KEY (emp_id)
                        REFERENCES cadastro_empresas (emp_id)
                        ON DELETE RESTRICT,
                    CONSTRAINT fk_job_status FOREIGN KEY (clf_id_status)
                        REFERENCES geral_classificadores (clf_id)
                        ON DELETE RESTRICT
                );
                """
            ),
            reverse_sql=(
                "DROP TABLE IF EXISTS movimento_jobs_processamento;"
            ),
        ),
    ]
