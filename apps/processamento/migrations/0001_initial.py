from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('empresa', '0001_initial'),
        ('classificadores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobProcessamento',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, db_column='jbp_id')),
                ('arquivo_original', models.FileField(upload_to='notas_fiscais_uploads/', db_column='jbp_arquivo_original')),
                ('empresa', models.ForeignKey(on_delete=models.PROTECT, related_name='jobs', to='empresa.MinhaEmpresa', db_column='emp_id')),
                ('status', models.ForeignKey(on_delete=models.PROTECT, related_name='jobs_status', to='classificadores.Classificador', db_column='clf_id_status')),
                ('dt_criacao', models.DateTimeField(auto_now_add=True, db_column='jbp_dt_criacao')),
                ('dt_alteracao', models.DateTimeField(auto_now=True, db_column='jbp_dt_alteracao')),
                ('usr_criacao', models.IntegerField(blank=True, null=True, db_column='jbp_usr_criacao')),
                ('usr_alteracao', models.IntegerField(blank=True, null=True, db_column='jbp_usr_alteracao')),
                ('dt_conclusao', models.DateTimeField(blank=True, null=True, db_column='jbp_dt_conclusao')),
                ('mensagem_erro', models.TextField(blank=True, null=True, db_column='jbp_mensagem_erro')),
            ],
            options={'db_table': 'movimento_jobs_processamento'},
        ),
    ]
