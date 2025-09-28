from rest_framework import generics
from .models import LancamentoFinanceiro
from .serializers import LancamentoFinanceiroSerializer
from apps.classificadores.models import get_classifier

class ContasAPagarListView(generics.ListAPIView):
    serializer_class = LancamentoFinanceiroSerializer

    def get_queryset(self):
        tipo = get_classifier('TIPO_LANCAMENTO', 'PAGAR')
        status = get_classifier('STATUS_LANCAMENTO', 'PENDENTE')
        return (
            LancamentoFinanceiro.objects.filter(
                clf_tipo=tipo, clf_status=status
            )
            .select_related('nota_fiscal__parceiro')
            .order_by('data_vencimento')
        )

class ContasAReceberListView(generics.ListAPIView):
    serializer_class = LancamentoFinanceiroSerializer

    def get_queryset(self):
        tipo = get_classifier('TIPO_LANCAMENTO', 'RECEBER')
        status = get_classifier('STATUS_LANCAMENTO', 'PENDENTE')
        return (
            LancamentoFinanceiro.objects.filter(
                clf_tipo=tipo, clf_status=status
            )
            .select_related('nota_fiscal__parceiro')
            .order_by('data_vencimento')
        )
