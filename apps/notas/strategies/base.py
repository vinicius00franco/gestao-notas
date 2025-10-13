"""
Interface base para estratégias de extração de dados de notas fiscais.
Define o contrato que todas as estratégias devem implementar.
"""

from abc import ABC, abstractmethod
from apps.notas.extractors import InvoiceData
from apps.notas.extraction_service import ExtractionMethod


class ExtractionStrategy(ABC):
    """Interface para estratégias de extração de dados de notas fiscais."""

    @abstractmethod
    def extract(self, file_content: bytes, filename: str) -> InvoiceData:
        """
        Extrai dados da nota fiscal do arquivo.

        Args:
            file_content: Conteúdo binário do arquivo
            filename: Nome do arquivo (para determinar tipo)

        Returns:
            InvoiceData: Dados extraídos da nota fiscal

        Raises:
            ValueError: Se não conseguir extrair dados válidos
        """
        pass

    @property
    @abstractmethod
    def method(self) -> ExtractionMethod:
        """Retorna o método de extração desta estratégia."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna o nome descritivo da estratégia."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Retorna a descrição da estratégia."""
        pass