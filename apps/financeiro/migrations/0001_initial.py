from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('notas', '0001_initial'),
        ('classificadores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LancamentoFinanceiro',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, db_column='lcf_id')),
                ('descricao', models.CharField(max_length=255, db_column='lcf_descricao')),
                ('valor', models.DecimalField(max_digits=10, decimal_places=2, db_column='lcf_valor')),
                ('data_vencimento', models.DateField(db_column='lcf_data_vencimento')),
                ('data_pagamento', models.DateField(blank=True, null=True, db_column='lcf_data_pagamento')),
                ('dt_criacao', models.DateTimeField(auto_now_add=True, db_column='lcf_dt_criacao')),
                ('dt_alteracao', models.DateTimeField(auto_now=True, db_column='lcf_dt_alteracao')),
                ('usr_criacao', models.IntegerField(blank=True, null=True, db_column='lcf_usr_criacao')),
                ('usr_alteracao', models.IntegerField(blank=True, null=True, db_column='lcf_usr_alteracao')),
                ('nota_fiscal', models.OneToOneField(on_delete=models.CASCADE, related_name='lancamento', to='notas.NotaFiscal', db_column='ntf_id')),
                ('clf_tipo', models.ForeignKey(on_delete=models.PROTECT, related_name='lancamentos_tipo', to='classificadores.Classificador', db_column='clf_id_tipo')),
                ('clf_status', models.ForeignKey(on_delete=models.PROTECT, related_name='lancamentos_status', to='classificadores.Classificador', db_column='clf_id_status')),
            ],
            options={'db_table': 'movimento_lancamentos_financeiros'},
        ),
    ]
