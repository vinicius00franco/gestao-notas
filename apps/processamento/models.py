import uuid
from django.db import models
from apps.empresa.models import MinhaEmpresa
from apps.classificadores.models import Classificador


class JobProcessamento(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='jbp_id')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='jbp_uuid')
    arquivo_original = models.FileField(upload_to='notas_fiscais_uploads/', db_column='jbp_arquivo_original')
    hash_arquivo = models.CharField(max_length=64, db_index=True, null=True, blank=True, db_column='jbp_hash_arquivo')
    empresa = models.ForeignKey(MinhaEmpresa, on_delete=models.PROTECT, related_name='jobs', db_column='emp_cnpj_numero', null=True, blank=True)
    status = models.ForeignKey(Classificador, on_delete=models.PROTECT, related_name='jobs_status', db_column='clf_id_status')
    dt_criacao = models.DateTimeField(auto_now_add=True, db_column='jbp_dt_criacao')
    dt_alteracao = models.DateTimeField(auto_now=True, db_column='jbp_dt_alteracao')
    usr_criacao = models.IntegerField(null=True, blank=True, db_column='jbp_usr_criacao')
    usr_alteracao = models.IntegerField(null=True, blank=True, db_column='jbp_usr_alteracao')
    dt_conclusao = models.DateTimeField(null=True, blank=True, db_column='jbp_dt_conclusao')
    mensagem_erro = models.TextField(null=True, blank=True, db_column='jbp_mensagem_erro')

    class Meta:
        db_table = 'movimento_jobs_processamento'

    def __str__(self):
        return f"Job {self.id}"
