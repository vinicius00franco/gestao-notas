"""
Orquestrador principal do pipeline de extração LLM.
Coordena: extração multimodal → classificação → extração especializada → validação.
"""
import logging
from typing import List, Tuple, Optional, Union
from dataclasses import dataclass

from .base import BaseLLMProvider
from .config import (
    MAX_PDF_PAGES_PER_BATCH,
    MAX_IMAGES_PER_BATCH,
    MIN_CONFIDENCE_SCORE
)
from .extractors import MultimodalExtractor
from .chains.classifier import DocumentClassifier
from .chains.extractors import ExtractorFactory
from .chains.validator import DataValidator
from .schemas import (
    DocumentoClassificado,
    NotaFiscalProduto,
    NotaFiscalServico,
    ExtratoFinanceiro,
    ResultadoValidacao,
    TipoDocumento
)


logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Resultado do processamento de um documento."""
    success: bool
    tipo_documento: Optional[TipoDocumento]
    classificacao: Optional[DocumentoClassificado]
    dados_extraidos: Optional[Union[NotaFiscalProduto, NotaFiscalServico, ExtratoFinanceiro]]
    validacao: Optional[ResultadoValidacao]
    error: Optional[str] = None
    filename: Optional[str] = None


class DocumentProcessor:
    """
    Orquestrador principal para processamento de documentos com LLM.
    
    Pipeline:
    1. Extração multimodal (PDF→texto ou imagens, imagens diretas)
    2. Classificação do documento
    3. Extração especializada baseada no tipo
    4. Validação dos dados extraídos
    """
    
    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        max_pages_per_batch: int = MAX_PDF_PAGES_PER_BATCH,
        max_images_per_batch: int = MAX_IMAGES_PER_BATCH,
        min_confidence_score: float = MIN_CONFIDENCE_SCORE,
        validate_results: bool = True
    ):
        self.llm = llm_provider
        self.validate_results = validate_results
        
        # Componentes do pipeline
        self.multimodal_extractor = MultimodalExtractor(
            max_pages_per_batch=max_pages_per_batch,
            min_text_chars=100
        )
        self.classifier = DocumentClassifier(llm_provider)
        self.extractor_factory = ExtractorFactory(llm_provider)
        self.validator = DataValidator(min_confidence_score=min_confidence_score)
    
    def process_file(
        self,
        file_bytes: bytes,
        filename: str
    ) -> ProcessingResult:
        """
        Processa um único arquivo.
        
        Args:
            file_bytes: Bytes do arquivo
            filename: Nome do arquivo (para inferir tipo)
            
        Returns:
            ProcessingResult com dados extraídos e validados
        """
        try:
            # Etapa 1: Extração multimodal
            logger.info(f"LLM: Processando arquivo: {filename}")
            text, images, num_pages = self._extract_multimodal(file_bytes, filename)
            
            if not text and not images:
                logger.warning(f"LLM: Não foi possível extrair texto ou imagens de {filename}")
                return ProcessingResult(
                    success=False,
                    tipo_documento=None,
                    classificacao=None,
                    dados_extraidos=None,
                    validacao=None,
                    error="Não foi possível extrair texto ou imagens",
                    filename=filename
                )
            
            logger.info(
                f"LLM: Extração multimodal concluída para {filename}: "
                f"texto={'sim' if text else 'não'} ({len(text) if text else 0} chars), "
                f"imagens={len(images) if images else 0}, "
                f"páginas={num_pages}"
            )
            
            # Etapa 2: Classificação
            logger.debug(f"LLM: Iniciando classificação para {filename}")
            classificacao = self.classifier.classify(text=text, images=images)
            logger.info(
                f"LLM: Documento {filename} classificado como {classificacao.tipo} "
                f"(confiança: {classificacao.confianca:.2f})"
            )
            
            # Validação: Verificar se é um tipo suportado
            tipos_suportados = [TipoDocumento.NF_PRODUTO, TipoDocumento.NF_SERVICO, TipoDocumento.EXTRATO_FINANCEIRO]
            if classificacao.tipo not in tipos_suportados:
                logger.warning(
                    f"LLM: Documento {filename} classificado como '{classificacao.tipo}' não é suportado. "
                    f"Tipos suportados: {[t.value for t in tipos_suportados]}. "
                    f"Interrompendo processamento da cadeia LLM."
                )
                return ProcessingResult(
                    success=False,
                    tipo_documento=None,
                    classificacao=classificacao,
                    dados_extraidos=None,
                    validacao=None,
                    error=f"Tipo de documento '{classificacao.tipo}' não suportado pela cadeia LLM",
                    filename=filename
                )
            
            if classificacao.confianca < MIN_CONFIDENCE_SCORE:
                logger.warning(
                    f"LLM: Confiança da classificação baixa para {filename}: {classificacao.confianca:.2f} "
                    f"(mínimo: {MIN_CONFIDENCE_SCORE})"
                )
            
            # Etapa 3: Extração especializada
            logger.debug(f"LLM: Iniciando extração especializada para {filename} (tipo: {classificacao.tipo})")
            dados_extraidos = self.extractor_factory.extract(
                tipo=classificacao.tipo,
                text=text,
                images=images
            )
            
            # Validação: Verificar se dados foram extraídos
            if not dados_extraidos:
                logger.warning(
                    f"LLM: Nenhum dado extraído para {filename} do tipo {classificacao.tipo}. "
                    f"Interrompendo processamento da cadeia LLM."
                )
                return ProcessingResult(
                    success=False,
                    tipo_documento=classificacao.tipo,
                    classificacao=classificacao,
                    dados_extraidos=None,
                    validacao=None,
                    error="Nenhum dado válido extraído do documento",
                    filename=filename
                )
            
            logger.info(f"LLM: Dados extraídos com sucesso para {filename}")
            
            # Etapa 4: Validação (opcional)
            validacao = None
            if self.validate_results:
                logger.debug(f"LLM: Iniciando validação para {filename}")
                validacao = self.validator.validate(dados_extraidos)
                logger.info(
                    f"LLM: Validação para {filename}: {'OK' if validacao.valido else 'FALHOU'} "
                    f"(score: {validacao.score_qualidade:.2f})"
                )
                
                if not validacao.valido:
                    logger.error(
                        f"LLM: Erros críticos na validação para {filename}: {validacao.erros_criticos}"
                    )
            
            logger.info(f"LLM: Processamento concluído com sucesso para {filename}")
            return ProcessingResult(
                success=True,
                tipo_documento=classificacao.tipo,
                classificacao=classificacao,
                dados_extraidos=dados_extraidos,
                validacao=validacao,
                filename=filename
            )
        
        except Exception as e:
            logger.exception(f"Erro ao processar arquivo {filename}")
            return ProcessingResult(
                success=False,
                tipo_documento=None,
                classificacao=None,
                dados_extraidos=None,
                validacao=None,
                error=str(e),
                filename=filename
            )
    
    def process_batch(
        self,
        files: List[Tuple[bytes, str]]
    ) -> List[ProcessingResult]:
        """
        Processa múltiplos arquivos.
        
        Args:
            files: Lista de (file_bytes, filename)
            
        Returns:
            Lista de ProcessingResult
        """
        results = []
        
        for file_bytes, filename in files:
            result = self.process_file(file_bytes, filename)
            results.append(result)
        
        # Log resumo
        success_count = sum(1 for r in results if r.success)
        logger.info(
            f"Batch processado: {success_count}/{len(results)} arquivos com sucesso"
        )
        
        return results
    
    def process_pdf_with_pagination(
        self,
        pdf_bytes: bytes,
        filename: str
    ) -> ProcessingResult:
        """
        Processa PDF grande dividindo em batches se necessário.
        
        Se PDF exceder MAX_PDF_PAGES_PER_BATCH, divide e processa em partes,
        depois mescla os resultados SEM RESUMIR (preservando todos os dados).
        
        Args:
            pdf_bytes: Bytes do PDF
            filename: Nome do arquivo
            
        Returns:
            ProcessingResult com dados mesclados
        """
        # Verifica se precisa paginar
        from pypdf import PdfReader
        import io
        
        reader = PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(reader.pages)
        
        if num_pages <= MAX_PDF_PAGES_PER_BATCH:
            # Não precisa paginar
            return self.process_file(pdf_bytes, filename)
        
        logger.info(
            f"PDF com {num_pages} páginas excede limite de {MAX_PDF_PAGES_PER_BATCH}. "
            "Processando em batches..."
        )
        
        # Converte para imagens e divide em batches
        images = self.multimodal_extractor.pdf_processor.convert_to_images(pdf_bytes)
        
        batches = []
        for i in range(0, len(images), MAX_IMAGES_PER_BATCH):
            batch_images = images[i:i + MAX_IMAGES_PER_BATCH]
            batches.append(batch_images)
        
        logger.info(f"PDF dividido em {len(batches)} batches")
        
        # Processa primeiro batch para determinar tipo
        first_result = self._process_images_batch(batches[0], f"{filename}_batch_1")
        
        if not first_result.success:
            return first_result
        
        tipo_documento = first_result.tipo_documento
        
        # Processa demais batches
        all_results = [first_result]
        for i, batch in enumerate(batches[1:], start=2):
            result = self._process_images_batch(
                batch,
                f"{filename}_batch_{i}",
                tipo_conhecido=tipo_documento
            )
            if result.success:
                all_results.append(result)
        
        # Mescla resultados (SEM RESUMIR)
        merged = self._merge_results(all_results, filename)
        
        return merged
    
    # ========================================================================
    # MÉTODOS AUXILIARES
    # ========================================================================
    
    def _extract_multimodal(
        self,
        file_bytes: bytes,
        filename: str
    ) -> Tuple[Optional[str], Optional[List[bytes]], int]:
        """Extrai texto e/ou imagens do arquivo."""
        ext = filename.lower().split('.')[-1]
        
        if ext == 'pdf':
            return self.multimodal_extractor.extract_from_pdf(file_bytes)
        elif ext in ['jpg', 'jpeg', 'png', 'tiff', 'bmp']:
            img = self.multimodal_extractor.extract_from_image(file_bytes)
            return None, [img], 1
        else:
            return None, None, 0
    
    def _process_images_batch(
        self,
        images: List[bytes],
        batch_name: str,
        tipo_conhecido: Optional[TipoDocumento] = None
    ) -> ProcessingResult:
        """Processa batch de imagens."""
        try:
            # Classifica se tipo não conhecido
            if tipo_conhecido is None:
                classificacao = self.classifier.classify(images=images)
                tipo_documento = classificacao.tipo
            else:
                tipo_documento = tipo_conhecido
                classificacao = None  # Não reclassifica
            
            # Validação: Verificar se é um tipo suportado
            tipos_suportados = [TipoDocumento.NF_PRODUTO, TipoDocumento.NF_SERVICO, TipoDocumento.EXTRATO_FINANCEIRO]
            if tipo_documento not in tipos_suportados:
                logger.warning(
                    f"LLM: Documento {batch_name} classificado como '{tipo_documento}' não é suportado. "
                    f"Interrompendo processamento da cadeia LLM."
                )
                return ProcessingResult(
                    success=False,
                    tipo_documento=None,
                    classificacao=classificacao,
                    dados_extraidos=None,
                    validacao=None,
                    error=f"Tipo de documento '{tipo_documento}' não suportado pela cadeia LLM",
                    filename=batch_name
                )
            
            # Extrai
            dados = self.extractor_factory.extract(
                tipo=tipo_documento,
                images=images
            )
            
            # Validação: Verificar se dados foram extraídos
            if not dados:
                logger.warning(
                    f"LLM: Nenhum dado extraído para {batch_name} do tipo {tipo_documento}. "
                    f"Interrompendo processamento da cadeia LLM."
                )
                return ProcessingResult(
                    success=False,
                    tipo_documento=tipo_documento,
                    classificacao=classificacao,
                    dados_extraidos=None,
                    validacao=None,
                    error="Nenhum dado válido extraído do documento",
                    filename=batch_name
                )
            
            # Valida
            validacao = None
            if self.validate_results:
                validacao = self.validator.validate(dados)
            
            return ProcessingResult(
                success=True,
                tipo_documento=tipo_documento,
                classificacao=classificacao,
                dados_extraidos=dados,
                validacao=validacao,
                filename=batch_name
            )
        
        except Exception as e:
            logger.exception(f"Erro ao processar batch {batch_name}")
            return ProcessingResult(
                success=False,
                tipo_documento=None,
                classificacao=None,
                dados_extraidos=None,
                validacao=None,
                error=str(e),
                filename=batch_name
            )
    
    def _merge_results(
        self,
        results: List[ProcessingResult],
        filename: str
    ) -> ProcessingResult:
        """
        Mescla resultados de múltiplos batches SEM RESUMIR.
        
        Para NotaFiscalProduto: combina listas de produtos
        Para NotaFiscalServico: concatena discriminação
        Para ExtratoFinanceiro: combina lançamentos
        """
        if not results:
            return ProcessingResult(
                success=False,
                tipo_documento=None,
                classificacao=None,
                dados_extraidos=None,
                validacao=None,
                error="Nenhum resultado para mesclar",
                filename=filename
            )
        
        tipo = results[0].tipo_documento
        
        # Mescla baseado no tipo
        if tipo == TipoDocumento.NF_PRODUTO:
            merged_data = self._merge_nf_produto([r.dados_extraidos for r in results])
        elif tipo == TipoDocumento.NF_SERVICO:
            merged_data = self._merge_nf_servico([r.dados_extraidos for r in results])
        elif tipo == TipoDocumento.EXTRATO_FINANCEIRO:
            merged_data = self._merge_extrato([r.dados_extraidos for r in results])
        else:
            merged_data = results[0].dados_extraidos
        
        # Valida resultado mesclado
        validacao = None
        if self.validate_results:
            validacao = self.validator.validate(merged_data)
        
        return ProcessingResult(
            success=True,
            tipo_documento=tipo,
            classificacao=results[0].classificacao,
            dados_extraidos=merged_data,
            validacao=validacao,
            filename=filename
        )
    
    def _merge_nf_produto(self, nfs: List[NotaFiscalProduto]) -> NotaFiscalProduto:
        """Mescla múltiplas NFe mantendo todos os produtos."""
        base = nfs[0]
        
        # Combina produtos de todos os batches
        all_produtos = []
        for nf in nfs:
            if nf.produtos:
                all_produtos.extend(nf.produtos)
        
        base.produtos = all_produtos
        return base
    
    def _merge_nf_servico(self, nfs: List[NotaFiscalServico]) -> NotaFiscalServico:
        """Mescla múltiplas NFSe concatenando discriminação."""
        base = nfs[0]
        
        # Concatena discriminação de todos os batches
        all_discriminacao = []
        for nf in nfs:
            if nf.discriminacao:
                all_discriminacao.append(nf.discriminacao)
        
        base.discriminacao = '\n\n'.join(all_discriminacao)
        return base
    
    def _merge_extrato(self, extratos: List[ExtratoFinanceiro]) -> ExtratoFinanceiro:
        """Mescla múltiplos extratos mantendo todos os lançamentos."""
        base = extratos[0]
        
        # Combina lançamentos de todos os batches
        all_lancamentos = []
        for extrato in extratos:
            if extrato.lancamentos:
                all_lancamentos.extend(extrato.lancamentos)
        
        base.lancamentos = all_lancamentos
        
        # Recalcula totais
        from decimal import Decimal
        base.total_creditos = sum(
            (l.valor for l in all_lancamentos if l.tipo == 'CREDITO'),
            Decimal(0)
        )
        base.total_debitos = sum(
            (l.valor for l in all_lancamentos if l.tipo == 'DEBITO'),
            Decimal(0)
        )
        
        if base.saldo_inicial is not None:
            base.saldo_final = (
                base.saldo_inicial +
                base.total_creditos -
                base.total_debitos
            )
        
        return base
