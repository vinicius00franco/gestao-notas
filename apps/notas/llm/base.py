"""
Interface abstrata para provedores de LLM.
Permite trocar facilmente entre Gemini, OpenAI, Anthropic, etc.
"""
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional
from pydantic import BaseModel


class LLMMessage(BaseModel):
    """Mensagem para o LLM."""
    role: str  # 'system', 'user', 'assistant'
    content: str
    images: Optional[List[bytes]] = None  # Para multimodal


class LLMResponse(BaseModel):
    """Resposta do LLM."""
    content: str
    raw_response: Any = None
    model: str
    tokens_used: Optional[int] = None


class BaseLLMProvider(ABC):
    """Interface base para provedores de LLM."""
    
    @abstractmethod
    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.1,
        max_tokens: int = 8192,
        **kwargs
    ) -> LLMResponse:
        """
        Gera resposta do LLM.
        
        Args:
            messages: Lista de mensagens (histórico de conversa)
            temperature: Controle de aleatoriedade (0-1)
            max_tokens: Máximo de tokens na resposta
            **kwargs: Parâmetros específicos do provedor
            
        Returns:
            LLMResponse com conteúdo gerado
        """
        pass
    
    @abstractmethod
    def generate_with_schema(
        self,
        messages: List[LLMMessage],
        schema: type[BaseModel],
        temperature: float = 0.1,
        max_tokens: int = 8192,
        **kwargs
    ) -> BaseModel:
        """
        Gera resposta estruturada conforme schema Pydantic.
        
        Args:
            messages: Lista de mensagens
            schema: Classe Pydantic para estruturar resposta
            temperature: Controle de aleatoriedade
            max_tokens: Máximo de tokens
            **kwargs: Parâmetros específicos
            
        Returns:
            Instância do schema com dados extraídos
        """
        pass
    
    @abstractmethod
    def supports_vision(self) -> bool:
        """Retorna se o modelo suporta análise de imagens."""
        pass
