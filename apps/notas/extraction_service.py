import logging
from abc import ABC, abstractmethod
from enum import Enum
from apps.notas.extractors import InvoiceData

logger = logging.getLogger(__name__)

class ExtractionMethod(Enum):
    """Métodos de extração disponíveis."""
    LLM = "llm"  # IA (Gemini)
    PDF = "pdf"  # Extração direta de PDF
    XML = "xml"  # Parsing XML NFe
    IMAGE = "image"  # OCR para imagens
    SIMULATED = "simulated"  # Dados simulados (desenvolvimento)

# Configuração do método de extração ativo
# Para alterar o método de extração, mude esta constante:
# - LLM: IA (Gemini) - método principal atual
# - PDF: Extração direta de PDF com regex
# - XML: Parsing XML NFe
# - IMAGE: OCR para imagens
# - SIMULATED: Dados simulados (desenvolvimento/teste)
ACTIVE_EXTRACTION_METHOD = ExtractionMethod.LLM

def set_extraction_method(method: ExtractionMethod):
    """Função utilitária para alterar dinamicamente o método de extração."""
    import apps.notas.extraction_service as es_module
    es_module.ACTIVE_EXTRACTION_METHOD = method
    logger.info(f"Método de extração alterado para: {method.value}")

class ExtractionStrategy(ABC):
    """Interface para estratégias de extração de dados de notas fiscais."""

    @abstractmethod
    def extract(self, file_content: bytes, filename: str) -> InvoiceData:
        """Extrai dados da nota fiscal do arquivo."""
        pass

    @property
    @abstractmethod
    def method(self) -> ExtractionMethod:
        """Retorna o método de extração desta estratégia."""
        pass

class NotaFiscalExtractionService:
    def __init__(self):
        self._strategy_factory = None

    @property
    def strategy_factory(self):
        """Lazy loading do factory."""
        if self._strategy_factory is None:
            from .strategies.factory import ExtractionStrategyFactory
            self._strategy_factory = ExtractionStrategyFactory
        return self._strategy_factory

    def extract_data_from_job(self, job) -> InvoiceData:
        filename = job.arquivo_original.name
        file_content = job.arquivo_original.read()

        logger.info(f"Iniciando extração usando método: {ACTIVE_EXTRACTION_METHOD.value}")

        # Usar padrão Strategy: criar estratégia e executar
        strategy = self.strategy_factory.create_strategy(ACTIVE_EXTRACTION_METHOD)
        logger.debug(f"Estratégia criada: {strategy.name} - {strategy.description}")

        return strategy.extract(file_content, filename)