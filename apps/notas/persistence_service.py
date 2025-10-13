"""
Persistence service using repositories instead of direct queries.
"""

import logging
from decimal import Decimal, InvalidOperation
from apps.notas.models import NotaFiscal
from apps.financeiro.models import LancamentoFinanceiro
from apps.classificadores.models import get_classifier
from .repositories import NotaFiscalRepository

logger = logging.getLogger(__name__)

class NotaFiscalPersistenceService:
    """
    Service for persisting NotaFiscal and LancamentoFinanceiro.
    Now uses repositories for all database operations.
    """

    def __init__(self):
        self.nota_fiscal_repository = NotaFiscalRepository()

    def persist_nota_e_lancamento(self, job, dados_extraidos, parceiro, tipo_lancamento) -> LancamentoFinanceiro:
        """
        Persist NotaFiscal and LancamentoFinanceiro using repositories.
        """
        # Create NotaFiscal using repository
        nota_fiscal = self.nota_fiscal_repository.create_from_invoice_data(
            invoice=dados_extraidos,
            job=job,
            parceiro=parceiro
        )

        # Persist items using repository
        self.nota_fiscal_repository.create_items_from_invoice_data(nota_fiscal, dados_extraidos)

        # Create LancamentoFinanceiro
        status_pendente = get_classifier('STATUS_LANCAMENTO', 'PENDENTE')

        lancamento = LancamentoFinanceiro.objects.create(
            nota_fiscal=nota_fiscal,
            descricao=f"NF {dados_extraidos.numero} - {parceiro.nome}",
            valor=dados_extraidos.valor_total,
            clf_tipo=tipo_lancamento,
            clf_status=status_pendente,
            data_vencimento=dados_extraidos.data_vencimento,
        )

        return lancamento