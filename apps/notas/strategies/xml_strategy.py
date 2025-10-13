"""
Estratégia de extração de arquivos XML NFe.
"""

import logging
import xml.etree.ElementTree as ET
from decimal import Decimal
from datetime import date

from apps.notas.extractors import InvoiceData
from apps.notas.extraction_service import ExtractionMethod
from .base import ExtractionStrategy

logger = logging.getLogger(__name__)


class XMLExtractionStrategy(ExtractionStrategy):
    """Estratégia de extração de XML NFe."""

    @property
    def method(self) -> ExtractionMethod:
        return ExtractionMethod.XML

    @property
    def name(self) -> str:
        return "XML NFe"

    @property
    def description(self) -> str:
        return "Parsing estruturado de arquivos XML de Notas Fiscais Eletrônicas (NFe)"

    def extract(self, file_content: bytes, filename: str) -> InvoiceData:
        """Extrai dados de um arquivo XML NFe."""
        logger.info(f"XML: Iniciando extração para {filename}")

        try:
            # Parse do XML
            root = ET.fromstring(file_content.decode('utf-8'))
            logger.debug("XML: Arquivo XML parseado com sucesso")

            # Extrair dados usando namespaces da NFe
            dados = self._parse_nfe_xml(root)

            invoice_data = InvoiceData(
                numero=dados.get('numero', 'XML-001'),
                remetente_cnpj=dados.get('remetente_cnpj', ''),
                remetente_nome=dados.get('remetente_nome', ''),
                destinatario_cnpj=dados.get('destinatario_cnpj', ''),
                destinatario_nome=dados.get('destinatario_nome', ''),
                valor_total=dados.get('valor_total', Decimal('0.00')),
                data_emissao=dados.get('data_emissao', date.today()),
                data_vencimento=dados.get('data_vencimento', date.today())
            )

            logger.info(f"XML: Extração concluída - Número: {invoice_data.numero}, Valor: R$ {invoice_data.valor_total}")
            return invoice_data

        except ET.ParseError as e:
            logger.error(f"XML: Erro de parsing XML para {filename}: {e}")
            raise ValueError(f"Arquivo XML inválido: {filename}")
        except Exception as e:
            logger.error(f"XML: Erro na extração para {filename}: {e}")
            raise ValueError(f"Falha na extração XML: {filename}")

    def _parse_nfe_xml(self, root) -> dict:
        """Parse dados específicos da estrutura XML da NFe."""
        dados = {}

        # Namespace da NFe
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

        # Número da NFe
        numero_elem = root.find('.//nfe:nNF', ns)
        if numero_elem is not None:
            dados['numero'] = numero_elem.text

        # Data de emissão
        dt_emissao_elem = root.find('.//nfe:dhEmi', ns)
        if dt_emissao_elem is not None:
            # Formato: 2024-01-15T10:30:00-03:00
            dt_str = dt_emissao_elem.text
            if dt_str:
                try:
                    # Extrair apenas a data (YYYY-MM-DD)
                    dados['data_emissao'] = date.fromisoformat(dt_str[:10])
                except:
                    dados['data_emissao'] = date.today()

        # Valor total
        valor_elem = root.find('.//nfe:vNF', ns)
        if valor_elem is not None:
            try:
                dados['valor_total'] = Decimal(valor_elem.text)
            except:
                dados['valor_total'] = Decimal('0.00')

        # Emitente (remetente)
        emitente = root.find('.//nfe:emit', ns)
        if emitente is not None:
            cnpj_elem = emitente.find('.//nfe:CNPJ', ns)
            if cnpj_elem is not None:
                dados['remetente_cnpj'] = cnpj_elem.text

            nome_elem = emitente.find('.//nfe:xNome', ns)
            if nome_elem is not None:
                dados['remetente_nome'] = nome_elem.text

        # Destinatário
        destinatario = root.find('.//nfe:dest', ns)
        if destinatario is not None:
            cnpj_elem = destinatario.find('.//nfe:CNPJ', ns)
            if cnpj_elem is not None:
                dados['destinatario_cnpj'] = cnpj_elem.text

            nome_elem = destinatario.find('.//nfe:xNome', ns)
            if nome_elem is not None:
                dados['destinatario_nome'] = nome_elem.text

        # Data de vencimento (se existir)
        # Nota: NFe normalmente não tem data de vencimento, mas NFSe pode ter
        dados['data_vencimento'] = dados.get('data_emissao', date.today())

        logger.debug(f"XML: Dados extraídos: {dados}")
        return dados