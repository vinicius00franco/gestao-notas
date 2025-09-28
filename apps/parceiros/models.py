import uuid
from django.db import models
from apps.classificadores.models import Classificador


class Parceiro(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='pcr_id')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='pcr_uuid')
    nome = models.CharField(max_length=255, db_column='pcr_nome')
    cnpj = models.CharField(max_length=18, unique=True, db_column='pcr_cnpj')
    # Substitui choices por FK para classificadores (TIPO_PARCEIRO)
    clf_tipo = models.ForeignKey(Classificador, on_delete=models.PROTECT, related_name='parceiros_tipo', db_column='clf_id_tipo')

    class Meta:
        db_table = 'cadastro_parceiros'

    def __str__(self):
        return f"{self.nome} ({self.cnpj})"
