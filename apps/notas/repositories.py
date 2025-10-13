"""
Repository layer for NotaFiscal persistence.

Implements data access patterns with idempotency checks,
transaction management, and separation of concerns from business logic.
"""

from typing import Optional
from django.db import transaction
from django.db.models import Q
import logging

from apps.notas.models import NotaFiscal, NotaFiscalItem
from apps.notas.extractors import InvoiceData
from apps.processamento.models import JobProcessamento
from apps.parceiros.models import Parceiro
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)


class NotaFiscalRepository:
    """
    Repository for NotaFiscal and NotaFiscalItem operations.

    Handles:
    - Idempotent creation/update of NotaFiscal
    - Item persistence with safe decimal conversion
    - Transaction management
    """

    @staticmethod
    def create_from_invoice_data(invoice, job, parceiro) -> NotaFiscal:
        """
        Create NotaFiscal from invoice data using ORM.
        """
        return NotaFiscal.objects.create(
            job_origem=job,
            parceiro=parceiro,
            chave_acesso=getattr(invoice, 'chave_acesso', None),
            numero=invoice.numero,
            data_emissao=invoice.data_emissao,
            valor_total=invoice.valor_total,
        )

    @staticmethod
    def create_items_from_invoice_data(nota_fiscal: NotaFiscal, invoice) -> int:
        """
        Create NotaFiscalItem records from invoice data using ORM.
        """
        itens = None
        if hasattr(invoice, 'produtos'):
            itens = getattr(invoice, 'produtos') or []
        elif hasattr(invoice, 'itens'):
            itens = getattr(invoice, 'itens') or []
        elif isinstance(invoice, dict):
            itens = invoice.get('produtos') or invoice.get('itens') or []
        else:
            itens = []

        if not itens:
            logger.info("No items found for NotaFiscal %s", nota_fiscal.numero)
            return 0

        created_count = 0
        for item in itens:
            try:
                # Flexible field extraction
                descricao = NotaFiscalRepository._get_attr(item, 'descricao') or \
                           NotaFiscalRepository._get_attr(item, 'nome') or 'Item'

                quantidade = NotaFiscalRepository._get_attr(item, 'quantidade') or 0
                valor_unitario = NotaFiscalRepository._get_attr(item, 'valor_unitario') or \
                                NotaFiscalRepository._get_attr(item, 'preco_unitario') or 0
                valor_total = NotaFiscalRepository._get_attr(item, 'valor_total') or \
                             NotaFiscalRepository._get_attr(item, 'preco_total') or 0

                # Safe decimal conversion
                qtd = NotaFiscalRepository._safe_decimal(quantidade)
                v_unit = NotaFiscalRepository._safe_decimal(valor_unitario)
                v_total = NotaFiscalRepository._safe_decimal(valor_total)

                # Calculate total if missing
                if not v_total and qtd and v_unit:
                    v_total = (qtd * v_unit).quantize(Decimal('0.01'))

                NotaFiscalItem.objects.create(
                    nota_fiscal=nota_fiscal,
                    descricao=str(descricao)[:255],  # Truncate if needed
                    quantidade=qtd,
                    valor_unitario=v_unit,
                    valor_total=v_total,
                )
                created_count += 1

            except Exception as e:
                logger.exception("Failed to create item for NotaFiscal %s: %s", nota_fiscal.numero, item)

        logger.info("Created %d items for NotaFiscal %s", created_count, nota_fiscal.numero)
        return created_count

    @staticmethod
    def _get_attr(obj, name: str, default=None):
        """Safely get attribute from object or dict."""
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

    @staticmethod
    def _safe_decimal(value, default=Decimal('0')) -> Decimal:
        """Convert value to Decimal safely."""
        if value is None:
            return default
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            logger.warning("Could not convert %r to Decimal, using default %s", value, default)
            return default