from django.db import models

class NotaFiscal(models.Model):
    from apps.parceiros.models import Parceiro  # type: ignore
    from apps.processamento.models import JobProcessamento  # type: ignore

    job_origem = models.OneToOneField('processamento.JobProcessamento', on_delete=models.PROTECT)
    parceiro = models.ForeignKey('parceiros.Parceiro', on_delete=models.CASCADE, related_name='notas_fiscais')
    numero = models.CharField(max_length=100)
    data_emissao = models.DateField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"NF {self.numero} - {self.parceiro.nome}"
