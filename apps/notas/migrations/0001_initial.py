from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('processamento', '0001_initial'),
        ('parceiros', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotaFiscal',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, db_column='ntf_id')),
                ('numero', models.CharField(max_length=100, db_column='ntf_numero')),
                ('data_emissao', models.DateField(db_column='ntf_data_emissao')),
                ('valor_total', models.DecimalField(max_digits=12, decimal_places=2, db_column='ntf_valor_total')),
                ('job_origem', models.ForeignKey(on_delete=models.PROTECT, to='processamento.JobProcessamento', db_column='jbp_id')),
                ('parceiro', models.ForeignKey(on_delete=models.PROTECT, related_name='notas_fiscais', to='parceiros.Parceiro', db_column='pcr_id')),
            ],
            options={'db_table': 'movimento_notas_fiscais'},
        ),
        migrations.CreateModel(
            name='NotaFiscalItem',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, db_column='nfi_id')),
                ('descricao', models.CharField(max_length=255, db_column='nfi_descricao')),
                ('quantidade', models.DecimalField(max_digits=10, decimal_places=3, db_column='nfi_quantidade')),
                ('valor_unitario', models.DecimalField(max_digits=10, decimal_places=2, db_column='nfi_valor_unitario')),
                ('valor_total', models.DecimalField(max_digits=12, decimal_places=2, db_column='nfi_valor_total')),
                ('nota_fiscal', models.ForeignKey(on_delete=models.CASCADE, related_name='itens', to='notas.NotaFiscal', db_column='ntf_id')),
            ],
            options={'db_table': 'movimento_nota_fiscal_itens'},
        ),
    ]
