"""
Configurações para LLMs.
Centraliza settings e permite troca fácil de modelo/provedor.
"""
from decouple import config
from typing import Literal

# Configurações Gemini
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')
GEMINI_MODEL = config('GEMINI_MODEL', default='gemini-1.5-flash')  # Flash Lite para custo-efetividade
GEMINI_TEMPERATURE = float(config('GEMINI_TEMPERATURE', default='0.1'))  # Baixa para consistência
GEMINI_MAX_TOKENS = int(config('GEMINI_MAX_TOKENS', default='8192'))

# Configurações gerais
LLM_PROVIDER: Literal['gemini', 'openai', 'anthropic'] = config('LLM_PROVIDER', default='gemini')
LLM_TIMEOUT = int(config('LLM_TIMEOUT', default='120'))  # segundos

# Limites de processamento
MAX_PDF_PAGES_PER_BATCH = int(config('MAX_PDF_PAGES_PER_BATCH', default='10'))
MAX_IMAGES_PER_BATCH = int(config('MAX_IMAGES_PER_BATCH', default='5'))
MAX_RETRIES = int(config('MAX_RETRIES', default='3'))

# Configurações de qualidade
MIN_CONFIDENCE_SCORE = float(config('MIN_CONFIDENCE_SCORE', default='0.7'))
ENABLE_VALIDATION_CHAIN = config('ENABLE_VALIDATION_CHAIN', default=True, cast=bool)
