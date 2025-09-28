import uuid
from django.db import models


class NotaFiscal(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='ntf_id')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='ntf_uuid')
    job_origem = models.ForeignKey('processamento.JobProcessamento', on_delete=models.PROTECT, db_column='jbp_id')
    parceiro = models.ForeignKey('parceiros.Parceiro', on_delete=models.PROTECT, related_name='notas_fiscais', db_column='pcr_id')
    numero = models.CharField(max_length=100, db_column='ntf_numero')
    data_emissao = models.DateField(db_column='ntf_data_emissao')
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, db_column='ntf_valor_total')

    class Meta:
        db_table = 'movimento_notas_fiscais'

    def __str__(self):
        return f"NF {self.numero} - {self.parceiro.nome}"


class NotaFiscalItem(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='nfi_id')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='nfi_uuid')
    nota_fiscal = models.ForeignKey('notas.NotaFiscal', on_delete=models.CASCADE, related_name='itens', db_column='ntf_id')
    descricao = models.CharField(max_length=255, db_column='nfi_descricao')
    quantidade = models.DecimalField(max_digits=10, decimal_places=3, db_column='nfi_quantidade')
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, db_column='nfi_valor_unitario')
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, db_column='nfi_valor_total')

    class Meta:
        db_table = 'movimento_nota_fiscal_itens'
