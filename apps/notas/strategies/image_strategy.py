"""
Estratégia de extração usando OCR para imagens.
"""

import logging
from decimal import Decimal
from datetime import date

from apps.notas.extractors import InvoiceData
from apps.notas.extraction_service import ExtractionMethod
from .base import ExtractionStrategy

logger = logging.getLogger(__name__)


class ImageExtractionStrategy(ExtractionStrategy):
    """Estratégia de extração usando OCR para imagens."""

    @property
    def method(self) -> ExtractionMethod:
        return ExtractionMethod.IMAGE

    @property
    def name(self) -> str:
        return "OCR Image"

    @property
    def description(self) -> str:
        return "Extração usando OCR (Optical Character Recognition) para imagens de documentos fiscais"

    def extract(self, file_content: bytes, filename: str) -> InvoiceData:
        """Extrai dados de uma imagem usando OCR."""
        logger.info(f"OCR: Iniciando extração para imagem {filename}")

        try:
            # Simulação de OCR - em produção usaria bibliotecas como Tesseract ou Google Vision API
            # Por enquanto, retorna dados mockados mas com indicação de que é OCR
            logger.warning("OCR: Funcionalidade OCR ainda não implementada - usando dados simulados")

            invoice_data = InvoiceData(
                numero=f"OCR-{hash(filename) % 10000:04d}",
                remetente_cnpj="22.222.222/0001-22",
                remetente_nome="Empresa OCR LTDA",
                destinatario_cnpj="99.999.999/0001-99",
                destinatario_nome="Minha Empresa Inc",
                valor_total=Decimal("800.00"),
                data_emissao=date.today(),
                data_vencimento=date.today()
            )

            # Adicionar metadados indicando que foi OCR
            setattr(invoice_data, 'extraction_method', 'OCR (simulado)')
            setattr(invoice_data, 'confidence_score', 0.85)  # Score de confiança do OCR

            logger.info(f"OCR: Extração simulada concluída - Número: {invoice_data.numero}")
            return invoice_data

        except Exception as e:
            logger.error(f"OCR: Erro na extração para {filename}: {e}")
            raise ValueError(f"Falha na extração OCR: {filename}")

    # Futuramente implementar:
    # def _perform_ocr(self, image_bytes: bytes) -> str:
    #     """Realiza OCR na imagem usando Tesseract ou Google Vision."""
    #     # Implementação real do OCR
    #     pass

    # def _parse_ocr_text(self, ocr_text: str) -> dict:
    #     """Parse do texto extraído por OCR usando regex patterns."""
    #     # Similar ao PDFExtractionStrategy._parse_nfe_data
    #     pass