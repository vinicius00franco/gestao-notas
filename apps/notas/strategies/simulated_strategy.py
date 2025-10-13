"""
Estratégia de extração com dados simulados para desenvolvimento e testes.
"""

import logging
from decimal import Decimal
from datetime import date

from apps.notas.extractors import InvoiceData
from apps.notas.extraction_service import ExtractionMethod
from .base import ExtractionStrategy

logger = logging.getLogger(__name__)


class SimulatedExtractionStrategy(ExtractionStrategy):
    """Estratégia de extração com dados simulados."""

    @property
    def method(self) -> ExtractionMethod:
        return ExtractionMethod.SIMULATED

    @property
    def name(self) -> str:
        return "Simulated"

    @property
    def description(self) -> str:
        return "Extração com dados simulados para desenvolvimento e testes"

    def extract(self, file_content: bytes, filename: str) -> InvoiceData:
        """Retorna dados simulados baseados no nome do arquivo."""
        logger.info(f"SIMULATED: Gerando dados simulados para {filename}")

        # Lógica baseada no nome do arquivo
        is_compra = "compra" in filename.lower()
        my_cnpj = "99.999.999/0001-99"

        if is_compra:
            invoice_data = InvoiceData(
                remetente_cnpj="11.222.333/0001-44",
                remetente_nome="Fornecedor Simulado LTDA",
                destinatario_cnpj=my_cnpj,
                destinatario_nome="Minha Empresa Inc",
                valor_total=Decimal("750.00"),
                data_emissao=date(2025, 10, 13),
                data_vencimento=date(2025, 11, 13),
                numero="NF-COMPRA-SIM-123"
            )
        else:
            invoice_data = InvoiceData(
                remetente_cnpj=my_cnpj,
                remetente_nome="Minha Empresa Inc",
                destinatario_cnpj="55.666.777/0001-88",
                destinatario_nome="Cliente Simulado SA",
                valor_total=Decimal("1200.50"),
                data_emissao=date(2025, 10, 13),
                data_vencimento=date(2025, 11, 13),
                numero="NF-VENDA-SIM-456"
            )

        # Adicionar metadados indicando que é simulado
        setattr(invoice_data, 'extraction_method', 'SIMULATED')
        setattr(invoice_data, 'is_simulated', True)

        logger.info(f"SIMULATED: Dados gerados - Número: {invoice_data.numero}, Valor: R$ {invoice_data.valor_total}")
        return invoice_data