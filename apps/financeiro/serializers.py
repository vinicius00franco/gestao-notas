from rest_framework import serializers
from .models import LancamentoFinanceiro
from apps.classificadores.serializers import ClassificadorSerializer

class LancamentoFinanceiroSerializer(serializers.ModelSerializer):
    clf_tipo = ClassificadorSerializer(read_only=True)
    clf_status = ClassificadorSerializer(read_only=True)

    class Meta:
        model = LancamentoFinanceiro
        # Expor uuid em vez de id numérico
        fields = ['uuid', 'descricao', 'valor', 'data_vencimento', 'data_pagamento', 'clf_tipo', 'clf_status', 'dt_criacao', 'dt_alteracao']
