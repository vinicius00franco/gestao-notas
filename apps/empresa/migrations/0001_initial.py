from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='MinhaEmpresa',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, db_column='emp_id')),
                ('nome', models.CharField(max_length=255, default='Minha Empresa', db_column='emp_nome')),
                ('cnpj', models.CharField(max_length=18, db_column='emp_cnpj', unique=True)),
                ('dt_criacao', models.DateTimeField(auto_now_add=True, db_column='emp_dt_criacao')),
                ('dt_alteracao', models.DateTimeField(auto_now=True, db_column='emp_dt_alteracao')),
                ('usr_criacao', models.IntegerField(blank=True, null=True, db_column='emp_usr_criacao')),
                ('usr_alteracao', models.IntegerField(blank=True, null=True, db_column='emp_usr_alteracao')),
                ('dt_exclusao', models.DateTimeField(blank=True, null=True, db_column='emp_dt_exclusao')),
            ],
            options={'db_table': 'cadastro_empresas'},
        ),
    ]
