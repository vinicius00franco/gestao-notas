from datetime import date, timedelta
import logging

from apps.core.observers import Observer

logger = logging.getLogger(__name__)


class AlertaVencimentoObserver(Observer):
    """Observer that logs a warning when a financial entry has a near due date."""

    def update(self, subject, event_type: str, **kwargs):
        if event_type == "lancamento_created":
            lancamento = kwargs.get("lancamento")
            if lancamento is not None:
                self._verificar_vencimento_proximo(lancamento)

    def _verificar_vencimento_proximo(self, lancamento):
        # número de dias antes do vencimento para emitir alerta
        dias_alerta = 7
        data_limite = date.today() + timedelta(days=dias_alerta)

        try:
            data_venc = lancamento.data_vencimento
        except Exception:
            return

        if data_venc and data_venc <= data_limite:
            logger.warning(
                "ALERTA: Vencimento próximo - %s vence em %s",
                getattr(lancamento, "descricao", "<sem descricao>"),
                data_venc,
            )
