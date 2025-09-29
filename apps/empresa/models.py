import uuid
from django.db import models


class MinhaEmpresa(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='emp_id')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='emp_uuid')
    nome = models.CharField(max_length=255, default="Minha Empresa", db_column='emp_nome')
    cnpj = models.CharField(max_length=18, unique=True, db_column='emp_cnpj')
    senha_hash = models.CharField(max_length=128, db_column='emp_senha_hash', default='', blank=True)
    # Auditoria básica
    dt_criacao = models.DateTimeField(auto_now_add=True, db_column='emp_dt_criacao')
    dt_alteracao = models.DateTimeField(auto_now=True, db_column='emp_dt_alteracao')
    usr_criacao = models.IntegerField(null=True, blank=True, db_column='emp_usr_criacao')
    usr_alteracao = models.IntegerField(null=True, blank=True, db_column='emp_usr_alteracao')
    dt_exclusao = models.DateTimeField(null=True, blank=True, db_column='emp_dt_exclusao')

    class Meta:
        verbose_name_plural = "Minha Empresa"
        db_table = "cadastro_empresas"

    def __str__(self):
        return self.nome
