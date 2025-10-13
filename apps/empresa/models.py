import uuid
from django.db import models
from django.core.exceptions import ValidationError
from apps.classificadores.models import Classificador


def cnpj_para_numero(cnpj_str):
    """Converte CNPJ string para número inteiro."""
    if not cnpj_str:
        return None
    # Remove pontos, barras e traços
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj_str))
    return int(cnpj_limpo) if cnpj_limpo else None


class MinhaEmpresa(models.Model):
    cnpj_numero = models.BigIntegerField(primary_key=True, db_column='emp_cnpj_numero')
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

    @classmethod
    def get_by_cnpj(cls, cnpj_str):
        """Busca empresa por CNPJ (string ou número)."""
        cnpj_numero = cnpj_para_numero(cnpj_str) if isinstance(cnpj_str, str) else cnpj_str
        try:
            return cls.objects.get(pk=cnpj_numero)
        except cls.DoesNotExist:
            raise cls.DoesNotExist()

    def __str__(self):
        return self.nome


class EmpresaNaoClassificada(models.Model):
    cnpj_numero = models.BigIntegerField(primary_key=True, db_column='enc_cnpj_numero')
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