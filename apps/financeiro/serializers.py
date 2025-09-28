from rest_framework import serializers
from .models import LancamentoFinanceiro

class LancamentoFinanceiroSerializer(serializers.ModelSerializer):
    class Meta:
        model = LancamentoFinanceiro
        fields = '__all__'
        depth = 2
