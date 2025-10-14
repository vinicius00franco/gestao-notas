from rest_framework import serializers
from .models import JobProcessamento
from apps.notas.models import NotaFiscal

class UploadNotaFiscalSerializer(serializers.Serializer):
    arquivo = serializers.FileField()
    meu_cnpj = serializers.CharField(max_length=18, required=False, help_text="CNPJ da sua empresa (ex: 99.999.999/0001-99)")

class JobProcessamentoSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='status.codigo', read_only=True)
    numero_nota = serializers.SerializerMethodField()

    class Meta:
        model = JobProcessamento
        # Expor uuid para o cliente em vez do id numérico
        fields = ['uuid', 'status', 'dt_criacao', 'dt_conclusao', 'mensagem_erro', 'numero_nota']
        read_only_fields = fields

    def get_numero_nota(self, obj):
        # Usar o prefetch_related para evitar N+1 queries
        notas = getattr(obj, 'notafiscal_set', None)
        if notas:
            nota = notas.first()
            return nota.numero if nota else None
        return None
