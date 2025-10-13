import logging
from apps.notas.extractors import ExtractorFactory, InvoiceData

logger = logging.getLogger(__name__)

class NotaFiscalExtractionService:
    def extract_data_from_job(self, job) -> InvoiceData:
        filename = job.arquivo_original.name
        file_content = job.arquivo_original.read()

        try:
            dados_extraidos_llm = self._try_extract_with_llm(file_content, filename)
            if dados_extraidos_llm:
                logger.info("Extração por LLM bem-sucedida para %s", filename)
                return dados_extraidos_llm
            raise ValueError("LLM não retornou dados utilizáveis")
        except Exception as e:
            logger.info("LLM falhou (%s), usando extratores legados.", e)
            extractor = ExtractorFactory.get_extractor(filename)
            return extractor.extract(file_content, filename)

    def _try_extract_with_llm(self, file_content: bytes, filename: str) -> InvoiceData | None:
        ext = filename.lower().split('.')[-1]
        if ext not in ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp']:
            logger.debug(f"LLM: Extensão {ext} não suportada para arquivo {filename}")
            return None

        try:
            logger.info(f"LLM: Iniciando extração para arquivo {filename}")
            from apps.notas.llm import GeminiProvider, DocumentProcessor, TipoDocumento
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
        from datetime import date as _date
        doc = result.dados_extraidos

        if result.tipo_documento == result.tipo_documento.NF_PRODUTO:
            numero = getattr(doc, 'numero_nota', 'S/NUM')
            data_emissao = getattr(doc, 'data_emissao', _date.today())
            data_vencimento = getattr(doc, 'data_vencimento', data_emissao)
            emissor = getattr(doc, 'emissor', {})
            destinatario = getattr(doc, 'destinatario', {})

            inv = InvoiceData(
                numero=str(numero),
                remetente_cnpj=emissor.get('cnpj', ''),
                remetente_nome=emissor.get('nome', ''),
                destinatario_cnpj=destinatario.get('cnpj', ''),
                destinatario_nome=destinatario.get('nome', ''),
                valor_total=getattr(doc, 'valor_total', 0),
                data_emissao=data_emissao,
                data_vencimento=data_vencimento,
            )
            setattr(inv, 'produtos', getattr(doc, 'produtos', []))
            setattr(inv, 'chave_acesso', getattr(doc, 'chave_acesso', None))
            return inv

        if result.tipo_documento == result.tipo_documento.NF_SERVICO:
            numero = getattr(doc, 'numero_nota', 'S/NUM')
            data_emissao = getattr(doc, 'data_emissao', _date.today())
            data_vencimento = getattr(doc, 'data_vencimento', data_emissao)
            prestador = getattr(doc, 'prestador', {})
            tomador = getattr(doc, 'tomador', {})
            valor_total = getattr(doc, 'valor_liquido', getattr(doc, 'valor_servico', 0))

            inv = InvoiceData(
                numero=str(numero),
                remetente_cnpj=prestador.get('cnpj', ''),
                remetente_nome=prestador.get('nome', ''),
                destinatario_cnpj=tomador.get('cnpj', ''),
                destinatario_nome=tomador.get('nome', ''),
                valor_total=valor_total,
                data_emissao=data_emissao,
                data_vencimento=data_vencimento,
            )
            setattr(inv, 'produtos', [])
            return inv

        return None