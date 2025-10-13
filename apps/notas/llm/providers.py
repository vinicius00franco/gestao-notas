"""
Provedor Gemini para análise multimodal de documentos.
Implementa interface BaseLLMProvider usando Google Generative AI.
"""
import json
import base64
from typing import List, Optional
from pydantic import BaseModel

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    genai = None

from .base import BaseLLMProvider, LLMMessage, LLMResponse
from .config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GEMINI_MAX_TOKENS,
    LLM_TIMEOUT,
)


class GeminiProvider(BaseLLMProvider):
    """Provedor Google Gemini (Flash/Pro) com suporte multimodal."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        if genai is None:
            raise ImportError(
                "google-generativeai não instalado. "
                "Instale com: pip install google-generativeai"
            )
        
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name or GEMINI_MODEL
        self.default_temperature = temperature or GEMINI_TEMPERATURE
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY não configurada. "
                "Defina a variável de ambiente ou passe api_key no construtor."
            )
        
        genai.configure(api_key=self.api_key)
        
        # Configurações de segurança (permissivo para documentos fiscais)
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    
    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> LLMResponse:
        """Gera resposta do Gemini."""
        temp = temperature if temperature is not None else self.default_temperature
        max_tok = max_tokens or GEMINI_MAX_TOKENS
        
        model = genai.GenerativeModel(
            model_name=self.model_name,
            safety_settings=self.safety_settings,
        )
        
        # Converte mensagens para formato Gemini
        gemini_parts = self._convert_messages_to_parts(messages)
        
        generation_config = genai.GenerationConfig(
            temperature=temp,
            max_output_tokens=max_tok,
            candidate_count=1,
        )
        
        response = model.generate_content(
            gemini_parts,
            generation_config=generation_config,
        )
        
        return LLMResponse(
            content=response.text,
            raw_response=response,
            model=self.model_name,
            tokens_used=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else None,
        )
    
    def generate_with_schema(
        self,
        messages: List[LLMMessage],
        schema: type[BaseModel],
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> BaseModel:
        """Gera resposta estruturada conforme schema Pydantic."""
        # Adiciona instrução para retornar JSON
        schema_json = schema.model_json_schema()
        system_msg = LLMMessage(
            role='system',
            content=(
                f"Você DEVE responder APENAS com um objeto JSON válido "
                f"seguindo EXATAMENTE este schema:\n\n"
                f"```json\n{json.dumps(schema_json, indent=2, ensure_ascii=False)}\n```\n\n"
                f"NÃO inclua texto adicional, markdown ou explicações. "
                f"APENAS o JSON puro."
            )
        )
        
        # Insere mensagem de sistema no início
        all_messages = [system_msg] + messages
        
        response = self.generate(
            messages=all_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Parse JSON da resposta
        try:
            # Remove markdown code blocks se presentes
            content = response.content.strip()
            if content.startswith('```'):
                # Remove ```json e ``` do início/fim
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()
            
            data = json.loads(content)
            return schema.model_validate(data)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"Falha ao parsear resposta do LLM como JSON: {e}\n"
                f"Resposta: {response.content[:500]}"
            )
    
    def supports_vision(self) -> bool:
        """Gemini Flash/Pro suportam visão."""
        return 'flash' in self.model_name.lower() or 'pro' in self.model_name.lower()
    
    def _convert_messages_to_parts(self, messages: List[LLMMessage]) -> List:
        """Converte mensagens LLM para formato Gemini parts."""
        parts = []
        
        for msg in messages:
            # Adiciona texto
            if msg.content:
                parts.append(msg.content)
            
            # Adiciona imagens se presentes
            if msg.images:
                for img_bytes in msg.images:
                    try:
                        # Gemini aceita bytes diretamente ou PIL Image
                        parts.append({'mime_type': 'image/jpeg', 'data': img_bytes})
                    except Exception:
                        # Fallback: converte para base64
                        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                        parts.append({'mime_type': 'image/jpeg', 'data': img_b64})
        
        return parts
