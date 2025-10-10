"""
Módulo de integração com LLMs para extração de dados de notas fiscais.
Arquitetura plugável que permite trocar facilmente entre diferentes provedores.
"""

from .base import BaseLLMProvider, LLMMessage, LLMResponse
from .providers import GeminiProvider
from .orchestrator import DocumentProcessor, ProcessingResult
from .schemas import (
    TipoDocumento,
    DocumentoClassificado,
    NotaFiscalProduto,
    NotaFiscalServico,
    ExtratoFinanceiro,
    ResultadoValidacao
)

__all__ = [
    # Base
    'BaseLLMProvider',
    'LLMMessage',
    'LLMResponse',
    
    # Providers
    'GeminiProvider',
    
    # Orchestrator
    'DocumentProcessor',
    'ProcessingResult',
    
    # Schemas
    'TipoDocumento',
    'DocumentoClassificado',
    'NotaFiscalProduto',
    'NotaFiscalServico',
    'ExtratoFinanceiro',
    'ResultadoValidacao',
]

