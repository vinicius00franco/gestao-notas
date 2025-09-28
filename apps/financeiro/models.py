from django.db import models

class LancamentoFinanceiro(models.Model):
    class Tipo(models.TextChoices):
        PAGAR = 'PAGAR', 'A Pagar'
        RECEBER = 'RECEBER', 'A Receber'
    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        PAGO = 'PAGO', 'Pago'
        ATRASADO = 'ATRASADO', 'Atrasado'
    nota_fiscal = models.OneToOneField('notas.NotaFiscal', on_delete=models.CASCADE, related_name='lancamento')
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDENTE)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao} - R$ {self.valor}"
