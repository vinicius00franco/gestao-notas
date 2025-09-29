import logging

from apps.core.observers import Observer
from apps.financeiro.models import LancamentoFinanceiro

logger = logging.getLogger(__name__)


class MetricasFinanceirasObserver(Observer):
    """Observer that recalculates simple financial metrics for the dashboard."""

    def update(self, subject, event_type: str, **kwargs):
        if event_type == "lancamento_created":
            try:
                self._atualizar_metricas()
            except Exception:
                logger.exception("Erro ao atualizar métricas financeiras")

    def _atualizar_metricas(self):
        # import Sum locally to avoid static analysis complaining about Django imports at top level
        from django.db.models import Sum

        total_pagar = (
            LancamentoFinanceiro.objects.filter(
                clf_tipo__codigo="PAGAR", clf_status__codigo="PENDENTE"
            )
            .aggregate(Sum("valor"))["valor__sum"]
            or 0
        )

        total_receber = (
            LancamentoFinanceiro.objects.filter(
                clf_tipo__codigo="RECEBER", clf_status__codigo="PENDENTE"
            )
            .aggregate(Sum("valor"))["valor__sum"]
            or 0
        )

        logger.info("MÉTRICAS: A Pagar: R$%s, A Receber: R$%s", total_pagar, total_receber)
