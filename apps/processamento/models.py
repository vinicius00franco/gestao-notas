from django.db import models

class JobProcessamento(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        PROCESSANDO = 'PROCESSANDO', 'Processando'
        CONCLUIDO = 'CONCLUIDO', 'Concluído'
        FALHA = 'FALHA', 'Falha'
    arquivo_original = models.FileField(upload_to='notas_fiscais_uploads/')
    meu_cnpj = models.CharField(max_length=18)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDENTE)
    dt_criacao = models.DateTimeField(auto_now_add=True)
    dt_conclusao = models.DateTimeField(null=True, blank=True)
    mensagem_erro = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Job {self.id} - {self.get_status_display()}"
