import uuid
from django.db import models
from django.db.models import Q


class NotaFiscal(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='ntf_id')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='ntf_uuid')
    job_origem = models.ForeignKey('processamento.JobProcessamento', on_delete=models.PROTECT, db_column='jbp_id')
    parceiro = models.ForeignKey('parceiros.Parceiro', on_delete=models.PROTECT, related_name='notas_fiscais', db_column='pcr_id')
    # Para NF-e, quando disponível, ajuda na idempotência e consultas
    chave_acesso = models.CharField(max_length=44, unique=True, null=True, blank=True, db_column='ntf_chave_acesso')
    numero = models.CharField(max_length=100, db_column='ntf_numero')
    data_emissao = models.DateField(db_column='ntf_data_emissao')
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, db_column='ntf_valor_total')

    class Meta:
        db_table = 'movimento_notas_fiscais'
        indexes = [
            models.Index(fields=['parceiro', 'data_emissao'], name='idx_ntf_parc_data'),
            models.Index(fields=['parceiro', 'numero'], name='idx_ntf_parc_num'),
        ]
        constraints = [
            # Garante unicidade de (parceiro, numero) apenas quando não existe chave de acesso
            models.UniqueConstraint(
                fields=['parceiro', 'numero'],
                condition=Q(chave_acesso__isnull=True),
                name='uq_ntf_parceiro_numero_when_no_chave'
            )
        ]

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
        indexes = [
            models.Index(fields=['nota_fiscal'], name='idx_nfi_ntf'),
        ]
