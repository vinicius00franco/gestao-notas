"""
Estratégia de extração direta de PDFs usando regex e parsing de texto.
"""

import logging
import re
from decimal import Decimal
from datetime import date, datetime
from pypdf import PdfReader
import io

from apps.notas.extractors import InvoiceData
from apps.notas.extraction_service import ExtractionMethod
from .base import ExtractionStrategy

logger = logging.getLogger(__name__)


class PDFExtractionStrategy(ExtractionStrategy):
    """Estratégia de extração direta de PDFs."""

    @property
    def method(self) -> ExtractionMethod:
        return ExtractionMethod.PDF

    @property
    def name(self) -> str:
        return "PDF Direct"

    @property
    def description(self) -> str:
        return "Extração direta de PDFs usando regex patterns para identificar dados fiscais"

    def extract(self, file_content: bytes, filename: str) -> InvoiceData:
        """Extrai dados diretamente do PDF."""
        logger.info(f"PDF: Iniciando extração direta para {filename}")

        try:
            # Extrair texto do PDF
            text = self._extract_text_from_pdf(file_content)
            logger.debug(f"PDF: Texto extraído ({len(text)} caracteres)")

            # Tentar extrair dados usando padrões de NFe
            dados = self._parse_nfe_data(text)
            logger.debug(f"PDF: Dados extraídos: {dados}")

            invoice_data = InvoiceData(
                numero=dados.get('numero', 'PDF-001'),
                remetente_cnpj=dados.get('remetente_cnpj', ''),
                remetente_nome=dados.get('remetente_nome', ''),
                destinatario_cnpj=dados.get('destinatario_cnpj', ''),
                destinatario_nome=dados.get('destinatario_nome', ''),
                valor_total=dados.get('valor_total', Decimal('0.00')),
                data_emissao=dados.get('data_emissao', date.today()),
                data_vencimento=dados.get('data_vencimento', date.today())
            )

            logger.info(f"PDF: Extração concluída - Número: {invoice_data.numero}, Valor: R$ {invoice_data.valor_total}")
            return invoice_data

        except Exception as e:
            logger.error(f"PDF: Erro na extração para {filename}: {e}")
            # Fallback para dados básicos se a extração falhar
            return InvoiceData(
                numero="PDF-ERRO",
                remetente_cnpj="",
                remetente_nome="Erro na extração",
                destinatario_cnpj="",
                destinatario_nome="",
                valor_total=Decimal("0.00"),
                data_emissao=date.today(),
                data_vencimento=date.today()
            )

    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extrai texto de um PDF usando PyPDF."""
        try:
            reader = PdfReader(io.BytesIO(file_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF: {e}")
            return ""

    def _parse_nfe_data(self, text: str) -> dict:
        """Parse dados de uma NFe do texto extraído."""
        dados = {}

        # Padrões comuns em NFe brasileiras
        patterns = {
            'numero': [
                r'N[oº°]?\s*(\d{1,9})',  # N° 123456789
                r'NF-e?\s*N[oº°]?\s*(\d{1,9})',  # NFe N° 123456789
                r'Número\s*(\d{1,9})',  # Número 123456789
            ],
            'cnpj': [
                r'CNPJ\s*[:\-]?\s*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})',  # CNPJ: 12.345.678/0001-90
                r'CNPJ\s*[:\-]?\s*(\d{14})',  # CNPJ: 12345678000190
            ],
            'valor_total': [
                r'Valor\s+total\s*[:\-]?\s*R?\$\s*([\d.,]+)',  # Valor total: R$ 1.234,56
                r'Total\s+NF-e?\s*[:\-]?\s*R?\$\s*([\d.,]+)',  # Total NFe: R$ 1.234,56
                r'Valor\s+total\s+da\s+nota\s*[:\-]?\s*R?\$\s*([\d.,]+)',  # Valor total da nota: R$ 1.234,56
            ],
            'data_emissao': [
                r'Data\s+(?:de\s+)?emiss[aã]o\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})',  # Data de emissão: 01/01/2024
                r'Data\s+(?:de\s+)?sa[ií]da\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})',  # Data de saída: 01/01/2024
            ],
        }

        # Extrair dados usando regex
        for campo, padroes in patterns.items():
            for padrao in padroes:
                match = re.search(padrao, text, re.IGNORECASE)
                if match:
                    valor = match.group(1).strip()
                    if campo == 'numero':
                        dados[campo] = valor
                    elif campo == 'cnpj':
                        # Tentar identificar se é CNPJ do remetente ou destinatário
                        # Por simplicidade, assume o primeiro CNPJ encontrado
                        if 'remetente_cnpj' not in dados:
                            dados['remetente_cnpj'] = valor
                        else:
                            dados['destinatario_cnpj'] = valor
                    elif campo == 'valor_total':
                        # Converter para Decimal
                        valor_limpo = valor.replace('R$', '').replace('.', '').replace(',', '.').strip()
                        try:
                            dados[campo] = Decimal(valor_limpo)
                        except:
                            dados[campo] = Decimal('0.00')
                    elif campo == 'data_emissao':
                        # Converter para date
                        try:
                            dados[campo] = datetime.strptime(valor, '%d/%m/%Y').date()
                        except:
                            dados[campo] = date.today()
                    break

        # Tentar extrair nomes das empresas (mais complexo)
        # Procurar por padrões como "Emitente:" ou "Destinatário:"
        emitente_match = re.search(r'Emitente\s*[:\-]?\s*([^\n\r]+)', text, re.IGNORECASE)
        if emitente_match:
            dados['remetente_nome'] = emitente_match.group(1).strip()

        destinatario_match = re.search(r'Destinat[aá]rio\s*[:\-]?\s*([^\n\r]+)', text, re.IGNORECASE)
        if destinatario_match:
            dados['destinatario_nome'] = destinatario_match.group(1).strip()

        return dados