from rest_framework import serializers
from .models import LancamentoFinanceiro

class LancamentoFinanceiroSerializer(serializers.ModelSerializer):
    class Meta:
        model = LancamentoFinanceiro
        # Expor uuid em vez de id numérico
        fields = ['uuid', 'descricao', 'valor', 'data_vencimento', 'data_pagamento', 'clf_tipo', 'clf_status', 'dt_criacao', 'dt_alteracao']
        depth = 2
