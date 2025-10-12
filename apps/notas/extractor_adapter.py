from abc import ABC, abstractmethod
from typing import Optional
import logging

from apps.notas.extractors import InvoiceData

logger = logging.getLogger(__name__)


class DocumentExtractor(ABC):
    """Interface for document extraction strategies."""

    @abstractmethod
    def extract(self, file_bytes: bytes, filename: str) -> Optional[InvoiceData]:
        """
        Extract invoice data from file bytes.

        Args:
            file_bytes: Raw file content
            filename: Original filename for format detection

        Returns:
            InvoiceData if extraction successful, None otherwise
        """
        pass


class LlmDocumentExtractor(DocumentExtractor):
    """Extractor using LLM pipeline (Gemini + LangChain)."""

    def __init__(self):
        self._processor = None

    def extract(self, file_bytes: bytes, filename: str) -> Optional[InvoiceData]:
        """
        Extract using LLM pipeline.
        Supports PDF (text extraction or image conversion) and images.
        """
        # Lazy import to avoid circular dependencies and missing LLM deps
        try:
            from apps.notas.llm import DocumentProcessor, TipoDocumento
        except ImportError as e:
            logger.debug("LLM modules not available: %s", e)
            return None

        # Initialize processor if not done
        if self._processor is None:
            try:
                from apps.notas.llm import GeminiProvider
                llm = GeminiProvider()
                self._processor = DocumentProcessor(llm_provider=llm)
            except Exception as e:
                logger.debug("Failed to initialize LLM processor: %s", e)
                return None

        # Process file
        result = self._processor.process_file(file_bytes, filename)
        if not result.success:
            logger.info("LLM processing failed for %s: %s", filename, result.error)
            return None

        # Skip extrato financeiro (not invoice)
        if result.tipo_documento == TipoDocumento.EXTRATO_FINANCEIRO:
            logger.info("Document %s classified as financial statement - skipping", filename)
            return None

        # Convert to InvoiceData
        from apps.notas.mappers import llm_to_invoice
        return llm_to_invoice(result.dados_extraidos, result.tipo_documento)


class LegacyDocumentExtractor(DocumentExtractor):
    """Extractor using existing legacy extractors (PDF/XML/Image/Simulated)."""

    def extract(self, file_bytes: bytes, filename: str) -> Optional[InvoiceData]:
        """
        Extract using legacy ExtractorFactory.
        Supports PDF, XML, image formats, and simulated data.
        """
        try:
            from apps.notas.extractors import ExtractorFactory
            extractor = ExtractorFactory.get_extractor(filename)
            return extractor.extract(file_bytes, filename)
        except Exception as e:
            logger.exception("Legacy extraction failed for %s", filename)
            return None


class FallbackExtractorAdapter(DocumentExtractor):
    """
    Tries LLM extraction first, falls back to legacy extractors.
    Implements the strategy pattern for resilient document processing.
    """

    def __init__(self):
        self.llm_extractor = LlmDocumentExtractor()
        self.legacy_extractor = LegacyDocumentExtractor()

    def extract(self, file_bytes: bytes, filename: str) -> Optional[InvoiceData]:
        """
        Try LLM first, then legacy.
        Logs which strategy succeeded for monitoring.
        """
        # Try LLM
        result = self.llm_extractor.extract(file_bytes, filename)
        if result is not None:
            logger.info("LLM extraction succeeded for %s", filename)
            return result

        # Fallback to legacy
        logger.info("LLM extraction failed or unavailable for %s, trying legacy", filename)
        result = self.legacy_extractor.extract(file_bytes, filename)
        if result is not None:
            logger.info("Legacy extraction succeeded for %s", filename)
            return result

        logger.warning("All extraction strategies failed for %s", filename)
        return None