from rest_framework import serializers
from .models import NotaFiscal
from apps.parceiros.models import Parceiro


class ParceiroResumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parceiro
        fields = ('uuid', 'nome', 'cnpj')


class NotaFiscalSerializer(serializers.ModelSerializer):
    # Expor apenas uuid (do not expose internal integer id) e dados do parceiro resumidos
    parceiro = ParceiroResumoSerializer(read_only=True)

    class Meta:
        model = NotaFiscal
        # explicit fields: do not send internal DB id
        fields = ('uuid', 'numero', 'data_emissao', 'valor_total', 'parceiro', 'chave_acesso')