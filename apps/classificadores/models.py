import uuid
from django.db import models


class Classificador(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='clf_id')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='clf_uuid')
    tipo = models.CharField(max_length=50, db_column='clf_tipo')  # ex: STATUS_JOB, TIPO_PARCEIRO, TIPO_LANCAMENTO, STATUS_LANCAMENTO
    codigo = models.CharField(max_length=50, db_column='clf_codigo')  # ex: CONCLUIDO, CLIENTE, RECEITA
    descricao = models.CharField(max_length=255, db_column='clf_descricao')

    class Meta:
        unique_together = ("tipo", "codigo")
        db_table = "geral_classificadores"

    def __str__(self):
        return f"{self.tipo}:{self.codigo}"


def get_classifier(tipo: str, codigo: str) -> "Classificador":
    return Classificador.objects.get(tipo=tipo, codigo=codigo)
