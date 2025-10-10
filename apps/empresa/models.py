import uuid
from django.db import models
from apps.classificadores.models import Classificador


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


class EmpresaNaoClassificada(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='enc_id')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='enc_uuid')
    cnpj = models.CharField(max_length=18, unique=True, db_column='enc_cnpj')
    nome_fantasia = models.CharField(max_length=255, db_column='enc_nome_fantasia')
    razao_social = models.CharField(max_length=255, db_column='enc_razao_social')
    uf = models.CharField(max_length=2, db_column='enc_uf')
    cidade = models.CharField(max_length=255, db_column='enc_cidade')
    logradouro = models.CharField(max_length=255, db_column='enc_logradouro')
    numero = models.CharField(max_length=255, db_column='enc_numero')
    bairro = models.CharField(max_length=255, db_column='enc_bairro')
    cep = models.CharField(max_length=9, db_column='enc_cep')
    telefone = models.CharField(max_length=20, db_column='enc_telefone')
    email = models.CharField(max_length=255, db_column='enc_email')
    dt_criacao = models.DateTimeField(auto_now_add=True, db_column='enc_dt_criacao')

    class Meta:
        verbose_name_plural = "Empresas Não Classificadas"
        db_table = "empresas_nao_classificadas"

    def __str__(self):
        return self.nome_fantasia