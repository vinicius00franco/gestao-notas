"""
Estratégias de extração de dados de notas fiscais.
Cada estratégia implementa uma forma diferente de extrair dados dos documentos.
"""

from .base import ExtractionStrategy
from .llm_strategy import LLMExtractionStrategy
from .pdf_strategy import PDFExtractionStrategy
from .xml_strategy import XMLExtractionStrategy
from .image_strategy import ImageExtractionStrategy
from .simulated_strategy import SimulatedExtractionStrategy
from .factory import ExtractionStrategyFactory

__all__ = [
    'ExtractionStrategy',
    'LLMExtractionStrategy',
    'PDFExtractionStrategy',
    'XMLExtractionStrategy',
    'ImageExtractionStrategy',
    'SimulatedExtractionStrategy',
    'ExtractionStrategyFactory',
]