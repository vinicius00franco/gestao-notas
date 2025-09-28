from rest_framework import serializers
from .models import JobProcessamento

class UploadNotaFiscalSerializer(serializers.Serializer):
    arquivo = serializers.FileField()
    meu_cnpj = serializers.CharField(max_length=18, help_text="CNPJ da sua empresa (ex: 99.999.999/0001-99)")

class JobProcessamentoSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='status.codigo', read_only=True)

    class Meta:
        model = JobProcessamento
        # Expor uuid para o cliente em vez do id numérico
        fields = ['uuid', 'status', 'dt_criacao', 'dt_conclusao', 'mensagem_erro']
        read_only_fields = fields
