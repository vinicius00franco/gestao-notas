from rest_framework import generics, views, status
from rest_framework.response import Response
from django.db.models import Sum, Value, F, Q, DecimalField, IntegerField, Count
from django.db.models.functions import Coalesce
from .models import LancamentoFinanceiro
from .serializers import LancamentoFinanceiroSerializer
from apps.classificadores.models import get_classifier
import logging
from datetime import date

logger = logging.getLogger(__name__)

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


class CalendarResumoView(views.APIView):
    """
    Retorna um resumo por dia do mês informado com:
    - total_pagar
    - total_receber
    - saldo (receber - pagar) quando ambos existirem; caso contrário, retorna apenas o campo existente

    Query params:
      - ano (int) ex: 2025
      - mes (int 1-12)
    """

    def get(self, request, *args, **kwargs):
        try:
            ano = int(request.query_params.get('ano', date.today().year))
            mes = int(request.query_params.get('mes', date.today().month))
        except Exception:
            return Response({"detail": "Parâmetros inválidos"}, status=status.HTTP_400_BAD_REQUEST)

        tipo_pagar = get_classifier('TIPO_LANCAMENTO', 'PAGAR')
        tipo_receber = get_classifier('TIPO_LANCAMENTO', 'RECEBER')
        status_pendente = get_classifier('STATUS_LANCAMENTO', 'PENDENTE')

        qs_base = LancamentoFinanceiro.objects.filter(
            data_vencimento__year=ano,
            data_vencimento__month=mes,
            clf_status=status_pendente,
        )

        zero_dec = Value(0, output_field=DecimalField(max_digits=12, decimal_places=2))
        agg = qs_base.values('data_vencimento').annotate(
            total_pagar=Coalesce(Sum('valor', filter=Q(clf_tipo=tipo_pagar)), zero_dec),
            total_receber=Coalesce(Sum('valor', filter=Q(clf_tipo=tipo_receber)), zero_dec),
            qtde_pagar=Coalesce(Count('id', filter=Q(clf_tipo=tipo_pagar)), Value(0, output_field=IntegerField())),
            qtde_receber=Coalesce(Count('id', filter=Q(clf_tipo=tipo_receber)), Value(0, output_field=IntegerField())),
        ).order_by('data_vencimento')

        resultados = []
        for row in agg:
            pagar = float(row['total_pagar']) if row['total_pagar'] is not None else 0.0
            receber = float(row['total_receber']) if row['total_receber'] is not None else 0.0
            payload: dict = {
                'data': row['data_vencimento'].isoformat(),
            }
            if pagar and not receber:
                payload['valor_pagar'] = pagar
                payload['qtde_pagar'] = int(row.get('qtde_pagar') or 0)
            elif receber and not pagar:
                payload['valor_receber'] = receber
                payload['qtde_receber'] = int(row.get('qtde_receber') or 0)
            else:
                payload['saldo'] = round(receber - pagar, 2)
                payload['valor_pagar'] = pagar
                payload['valor_receber'] = receber
                payload['qtde_pagar'] = int(row.get('qtde_pagar') or 0)
                payload['qtde_receber'] = int(row.get('qtde_receber') or 0)
            resultados.append(payload)

        logger.info("Calendar resumo calculado", extra={
            'operation': 'calendar_resumo',
            'status': 'success',
            'ano': ano,
            'mes': mes,
            'dias_count': len(resultados)
        })

        return Response({'ano': ano, 'mes': mes, 'dias': resultados})


class CalendarDiaDetalhesView(views.APIView):
    """
    Retorna os lançamentos de um dia específico com:
      - nome_fantasia (parceiro.nome)
      - cnpj
      - valor
      - data (data_vencimento)
      - tipo (PAGAR/RECEBER)

    Query params:
      - data=YYYY-MM-DD
    """

    def get(self, request, *args, **kwargs):
        data_param = request.query_params.get('data')
        if not data_param:
            return Response({"detail": "Parâmetro 'data' é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ano, mes, dia = map(int, data_param.split('-'))
        except Exception:
            return Response({"detail": "Formato de data inválido. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        tipo_pagar = get_classifier('TIPO_LANCAMENTO', 'PAGAR')
        tipo_receber = get_classifier('TIPO_LANCAMENTO', 'RECEBER')
        status_pendente = get_classifier('STATUS_LANCAMENTO', 'PENDENTE')

        qs = (
            LancamentoFinanceiro.objects.filter(
                data_vencimento__year=ano,
                data_vencimento__month=mes,
                data_vencimento__day=dia,
                clf_status=status_pendente,
            )
            .select_related('nota_fiscal__parceiro', 'clf_tipo')
            .order_by('data_vencimento', 'nota_fiscal__parceiro__nome')
        )

        detalhes = []
        for lanc in qs:
            parceiro = lanc.nota_fiscal.parceiro
            tipo = 'PAGAR' if lanc.clf_tipo_id == tipo_pagar.id else ('RECEBER' if lanc.clf_tipo_id == tipo_receber.id else None)
            detalhes.append({
                'nome_fantasia': parceiro.nome,
                'cnpj': parceiro.cnpj,
                'valor': float(lanc.valor),
                'data': lanc.data_vencimento.isoformat(),
                'tipo': tipo,
                'numero_nota': lanc.nota_fiscal.numero,
            })

        logger.info("Calendar dia detalhes", extra={
            'operation': 'calendar_dia_detalhes',
            'status': 'success',
            'data': data_param,
            'itens': len(detalhes)
        })

        return Response({'data': data_param, 'detalhes': detalhes}, status=status.HTTP_200_OK)
