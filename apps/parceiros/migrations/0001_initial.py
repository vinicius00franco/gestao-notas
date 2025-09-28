from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classificadores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parceiro',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, db_column='pcr_id')),
                ('nome', models.CharField(max_length=255, db_column='pcr_nome')),
                ('cnpj', models.CharField(max_length=18, unique=True, db_column='pcr_cnpj')),
                ('clf_tipo', models.ForeignKey(on_delete=models.PROTECT, related_name='parceiros_tipo', to='classificadores.Classificador', db_column='clf_id_tipo')),
            ],
            options={'db_table': 'cadastro_parceiros'},
        ),
    ]
