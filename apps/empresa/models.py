from django.db import models

class MinhaEmpresa(models.Model):
    nome = models.CharField(max_length=255, default="Minha Empresa")
    cnpj = models.CharField(max_length=18, unique=True)

    class Meta:
        verbose_name_plural = "Minha Empresa"

    def __str__(self):
        return self.nome
