"""
Factory para criação de estratégias de extração.
Implementa o padrão Factory para centralizar a criação de estratégias.
"""

import logging
from typing import Dict, Type

from apps.notas.extraction_service import ExtractionMethod
from .base import ExtractionStrategy
from .llm_strategy import LLMExtractionStrategy
from .pdf_strategy import PDFExtractionStrategy
from .xml_strategy import XMLExtractionStrategy
from .image_strategy import ImageExtractionStrategy
from .simulated_strategy import SimulatedExtractionStrategy

logger = logging.getLogger(__name__)


class ExtractionStrategyFactory:
    """Factory para criação de estratégias de extração."""

    # Mapeamento de métodos para classes de estratégia
    _strategies: Dict[ExtractionMethod, Type[ExtractionStrategy]] = {
        ExtractionMethod.LLM: LLMExtractionStrategy,
        ExtractionMethod.PDF: PDFExtractionStrategy,
        ExtractionMethod.XML: XMLExtractionStrategy,
        ExtractionMethod.IMAGE: ImageExtractionStrategy,
        ExtractionMethod.SIMULATED: SimulatedExtractionStrategy,
    }

    @classmethod
    def create_strategy(cls, method: ExtractionMethod) -> ExtractionStrategy:
        """
        Cria uma instância da estratégia para o método especificado.

        Args:
            method: Método de extração desejado

        Returns:
            Instância da estratégia apropriada

        Raises:
            ValueError: Se o método não for suportado
        """
        strategy_class = cls._strategies.get(method)
        if not strategy_class:
            available_methods = [m.value for m in cls._strategies.keys()]
            raise ValueError(
                f"Método de extração '{method.value}' não suportado. "
                f"Métodos disponíveis: {available_methods}"
            )

        logger.debug(f"Factory: Criando estratégia {strategy_class.__name__} para método {method.value}")
        return strategy_class()

    @classmethod
    def get_available_strategies(cls) -> Dict[ExtractionMethod, str]:
        """
        Retorna todas as estratégias disponíveis com suas descrições.

        Returns:
            Dicionário com método -> descrição
        """
        strategies_info = {}
        for method, strategy_class in cls._strategies.items():
            # Criar instância temporária apenas para obter informações
            temp_instance = strategy_class()
            strategies_info[method] = {
                'name': temp_instance.name,
                'description': temp_instance.description
            }

        return strategies_info

    @classmethod
    def get_strategy_for_file(cls, filename: str) -> ExtractionMethod:
        """
        Sugere o método de extração mais apropriado baseado na extensão do arquivo.

        Args:
            filename: Nome do arquivo

        Returns:
            Método de extração sugerido
        """
        ext = filename.lower().split('.')[-1]

        # Mapeamento de extensões para métodos
        extension_mapping = {
            'pdf': ExtractionMethod.PDF,
            'xml': ExtractionMethod.XML,
            'jpg': ExtractionMethod.IMAGE,
            'jpeg': ExtractionMethod.IMAGE,
            'png': ExtractionMethod.IMAGE,
            'tiff': ExtractionMethod.IMAGE,
            'bmp': ExtractionMethod.IMAGE,
        }

        suggested_method = extension_mapping.get(ext, ExtractionMethod.LLM)
        logger.debug(f"Factory: Método sugerido para .{ext}: {suggested_method.value}")

        return suggested_method