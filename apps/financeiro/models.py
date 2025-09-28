import uuid
from django.db import models
from apps.classificadores.models import Classificador


class LancamentoFinanceiro(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='lcf_id')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='lcf_uuid')
    nota_fiscal = models.OneToOneField('notas.NotaFiscal', on_delete=models.CASCADE, related_name='lancamento', db_column='ntf_id')
    descricao = models.CharField(max_length=255, db_column='lcf_descricao')
    valor = models.DecimalField(max_digits=10, decimal_places=2, db_column='lcf_valor')
    clf_tipo = models.ForeignKey(Classificador, on_delete=models.PROTECT, related_name='lancamentos_tipo', db_column='clf_id_tipo')
    clf_status = models.ForeignKey(Classificador, on_delete=models.PROTECT, related_name='lancamentos_status', db_column='clf_id_status')
    data_vencimento = models.DateField(db_column='lcf_data_vencimento')
    data_pagamento = models.DateField(null=True, blank=True, db_column='lcf_data_pagamento')
    dt_criacao = models.DateTimeField(auto_now_add=True, db_column='lcf_dt_criacao')
    dt_alteracao = models.DateTimeField(auto_now=True, db_column='lcf_dt_alteracao')
    usr_criacao = models.IntegerField(null=True, blank=True, db_column='lcf_usr_criacao')
    usr_alteracao = models.IntegerField(null=True, blank=True, db_column='lcf_usr_alteracao')

    class Meta:
        db_table = 'movimento_lancamentos_financeiros'

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"
