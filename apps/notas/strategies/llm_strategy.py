"""
Estratégia de extração usando IA (Gemini LLM).
"""

import logging
from apps.notas.extractors import InvoiceData
from apps.notas.extraction_service import ExtractionMethod
from apps.notas.llm import TipoDocumento
from .base import ExtractionStrategy

logger = logging.getLogger(__name__)


class LLMExtractionStrategy(ExtractionStrategy):
    """Estratégia de extração usando IA (Gemini)."""

    @property
    def method(self) -> ExtractionMethod:
        return ExtractionMethod.LLM

    @property
    def name(self) -> str:
        return "LLM (Gemini AI)"

    @property
    def description(self) -> str:
        return "Extração inteligente usando IA generativa (Gemini) para analisar documentos fiscais"

    def extract(self, file_content: bytes, filename: str) -> InvoiceData:
        """Extrai dados usando LLM (Gemini AI)."""
        logger.info(f"LLM: Iniciando extração para arquivo {filename}")

        dados_extraidos = self._try_extract_with_llm(file_content, filename)
        if dados_extraidos:
            logger.info("Extração por LLM bem-sucedida para %s", filename)
            return dados_extraidos

        # LLM falhou - erro em vez de fallback
        logger.error("LLM falhou para %s - nenhum método de extração alternativo disponível", filename)
        raise ValueError(f"Falha na extração por LLM para {filename}. Configure um método de extração alternativo se necessário.")

    def _try_extract_with_llm(self, file_content: bytes, filename: str) -> InvoiceData | None:
        """Tenta extrair dados usando LLM."""
        ext = filename.lower().split('.')[-1]
        if ext not in ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp']:
            logger.debug(f"LLM: Extensão {ext} não suportada para arquivo {filename}")
            return None

        try:
            logger.info(f"LLM: Iniciando extração para arquivo {filename}")
            from apps.notas.llm import GeminiProvider, DocumentProcessor
            llm = GeminiProvider()
            processor = DocumentProcessor(llm_provider=llm)

            logger.debug(f"LLM: Processando arquivo {filename} com {len(file_content)} bytes")
            result = processor.process_file(file_content, filename)

            logger.info(f"LLM: Processamento concluído para {filename}. Success: {result.success}, Tipo: {result.tipo_documento}")

            if not result.success:
                logger.warning(f"LLM: Processamento falhou para {filename}: {result.error}")
                return None

            if result.tipo_documento == TipoDocumento.EXTRATO_FINANCEIRO:
                logger.info(f"LLM: Documento classificado como EXTRATO_FINANCEIRO, ignorando para {filename}")
                return None

            logger.debug(f"LLM: Adaptando dados extraídos para {filename}")
            adapted_data = self._adapt_llm_output(result)
            if adapted_data:
                logger.info(f"LLM: Extração bem-sucedida para {filename}: {adapted_data.numero}, R$ {adapted_data.valor_total}")
            else:
                logger.warning(f"LLM: Adaptação falhou para {filename}")

            return adapted_data
        except Exception as e:
            logger.error(f"LLM: Erro ao processar {filename}: {str(e)}", exc_info=True)
            return None

    def _adapt_llm_output(self, result) -> InvoiceData | None:
        """Adapta a saída do LLM para o formato InvoiceData."""
        from datetime import date as _date
        doc = result.dados_extraidos

        logger.debug(f"LLM: Adaptando dados LLM - Tipo: {result.tipo_documento}, Doc type: {type(doc)}")

        if result.tipo_documento == "nf_produto":
            logger.debug(f"LLM: Adaptando NF Produto - doc: {doc}")
            numero = getattr(doc, 'numero', 'S/NUM')  # Campo correto é 'numero'
            data_emissao = getattr(doc, 'data_emissao', _date.today())
            data_vencimento = getattr(doc, 'data_vencimento', data_emissao)
            emissor = getattr(doc, 'emissor', None)
            destinatario = getattr(doc, 'destinatario', None)

            logger.debug(f"LLM: Emissor: {emissor} (type: {type(emissor)}), Destinatario: {destinatario} (type: {type(destinatario)})")

            # Acessar atributos diretamente dos objetos Pydantic
            remetente_cnpj = getattr(emissor, 'cnpj_cpf', '') if emissor else ''
            remetente_nome = getattr(emissor, 'nome', '') if emissor else ''
            destinatario_cnpj = getattr(destinatario, 'cnpj_cpf', '') if destinatario else ''
            destinatario_nome = getattr(destinatario, 'nome', '') if destinatario else ''

            logger.debug(f"LLM: CNPJs - Remetente: '{remetente_cnpj}', Destinatario: '{destinatario_cnpj}'")

            inv = InvoiceData(
                numero=str(numero),
                remetente_cnpj=remetente_cnpj,
                remetente_nome=remetente_nome,
                destinatario_cnpj=destinatario_cnpj,
                destinatario_nome=destinatario_nome,
                valor_total=getattr(doc, 'valor_total', 0),
                data_emissao=data_emissao,
                data_vencimento=data_vencimento,
            )
            setattr(inv, 'produtos', getattr(doc, 'itens', []))  # Campo correto é 'itens'
            setattr(inv, 'chave_acesso', getattr(doc, 'chave_acesso', None))
            logger.debug(f"LLM: InvoiceData criado: {inv.numero}, R$ {inv.valor_total}")
            return inv

        if result.tipo_documento == "nf_servico":
            logger.debug(f"LLM: Adaptando NF Serviço - doc: {doc}")
            numero = getattr(doc, 'numero', 'S/NUM')  # Campo correto é 'numero'
            data_emissao = getattr(doc, 'data_emissao', _date.today())
            data_vencimento = getattr(doc, 'data_vencimento', data_emissao)
            prestador = getattr(doc, 'prestador', None)
            tomador = getattr(doc, 'tomador', None)
            valor_total = getattr(doc, 'valor_liquido', getattr(doc, 'valor_servicos', 0))  # Campo correto pode ser 'valor_servicos'

            logger.debug(f"LLM: Prestador: {prestador} (type: {type(prestador)}), Tomador: {tomador} (type: {type(tomador)})")

            # Acessar atributos diretamente dos objetos Pydantic
            remetente_cnpj = getattr(prestador, 'cnpj_cpf', '') if prestador else ''
            remetente_nome = getattr(prestador, 'nome', '') if prestador else ''
            destinatario_cnpj = getattr(tomador, 'cnpj_cpf', '') if tomador else ''
            destinatario_nome = getattr(tomador, 'nome', '') if tomador else ''

            logger.debug(f"LLM: CNPJs - Prestador: '{remetente_cnpj}', Tomador: '{destinatario_cnpj}'")

            inv = InvoiceData(
                numero=str(numero),
                remetente_cnpj=remetente_cnpj,
                remetente_nome=remetente_nome,
                destinatario_cnpj=destinatario_cnpj,
                destinatario_nome=destinatario_nome,
                valor_total=valor_total,
                data_emissao=data_emissao,
                data_vencimento=data_vencimento,
            )
            setattr(inv, 'produtos', [])
            logger.debug(f"LLM: InvoiceData criado: {inv.numero}, R$ {inv.valor_total}")
            return inv

        logger.warning(f"LLM: Tipo de documento não suportado para adaptação: {result.tipo_documento}")
        return None