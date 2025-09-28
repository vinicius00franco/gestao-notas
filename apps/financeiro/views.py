from rest_framework import generics
from .models import LancamentoFinanceiro
from .serializers import LancamentoFinanceiroSerializer

class ContasAPagarListView(generics.ListAPIView):
    queryset = LancamentoFinanceiro.objects.filter(
        tipo=LancamentoFinanceiro.Tipo.PAGAR, status=LancamentoFinanceiro.Status.PENDENTE
    ).select_related('nota_fiscal__parceiro').order_by('data_vencimento')
    serializer_class = LancamentoFinanceiroSerializer

class ContasAReceberListView(generics.ListAPIView):
    queryset = LancamentoFinanceiro.objects.filter(
        tipo=LancamentoFinanceiro.Tipo.RECEBER, status=LancamentoFinanceiro.Status.PENDENTE
    ).select_related('nota_fiscal__parceiro').order_by('data_vencimento')
    serializer_class = LancamentoFinanceiroSerializer
