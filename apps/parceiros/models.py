from django.db import models

class Parceiro(models.Model):
    class Tipo(models.TextChoices):
        CLIENTE = 'CLIENTE', 'Cliente'
        FORNECEDOR = 'FORNECEDOR', 'Fornecedor'
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    def __str__(self):
        return f"{self.nome} ({self.cnpj})"
