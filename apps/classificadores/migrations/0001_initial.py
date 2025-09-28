from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Classificador',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, db_column='clf_id')),
                ('tipo', models.CharField(max_length=50, db_column='clf_tipo')),
                ('codigo', models.CharField(max_length=50, db_column='clf_codigo')),
                ('descricao', models.CharField(max_length=255, db_column='clf_descricao')),
            ],
            options={'db_table': 'geral_classificadores', 'unique_together': {('tipo', 'codigo')}},
        ),
    ]
