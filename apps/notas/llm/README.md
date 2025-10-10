# Módulo LLM para Extração de Notas Fiscais

Sistema completo de extração de dados de documentos fiscais usando **Large Language Models (LLM)** com suporte multimodal.

## 🎯 Funcionalidades

- ✅ **Extração multimodal**: PDFs (texto + imagens) e imagens diretas
- ✅ **Classificação automática**: Identifica NF Produto, NF Serviço ou Extrato
- ✅ **Extração especializada**: Templates otimizados para cada tipo de documento
- ✅ **Validação inteligente**: Verifica consistência e completude dos dados
- ✅ **Paginação automática**: PDFs grandes divididos em batches sem perda de dados
- ✅ **Arquitetura plugável**: Troque facilmente entre Gemini, OpenAI, Anthropic

## 📋 Tipos de Documentos Suportados

### 1. NF Produto (NFe)
- Chave de acesso 44 dígitos
- Lista completa de produtos (código, NCM, CFOP, valores)
- Totais com ICMS, IPI, frete, seguro
- Validação: `quantidade × valor_unitario = valor_total`

### 2. NF Serviço (NFSe)
- Código de verificação
- Discriminação detalhada do serviço
- Tributos: ISS, PIS, COFINS, CSLL, IR, INSS
- Valores bruto e líquido

### 3. Extrato Financeiro
- Lançamentos completos (data, descrição, tipo, valor)
- Tipo automático (CREDITO/DEBITO)
- Saldos inicial e final
- Validação: `saldo_final = saldo_inicial + créditos - débitos`

## 🚀 Guia Rápido

### Instalação

```bash
pip install -r requirements.txt
```

**Dependências principais:**
- `langchain` - Orquestração de LLM
- `google-generativeai` - Gemini API
- `pypdf` - Extração de texto de PDF
- `pdf2image` - Conversão PDF→imagens
- `Pillow` - Processamento de imagens
- `pydantic` - Validação de schemas

### Configuração

```bash
# .env
GEMINI_API_KEY=sua_chave_aqui
```

### Uso Básico

```python
from apps.notas.llm import GeminiProvider, DocumentProcessor

# 1. Inicializa provider
llm = GeminiProvider()

# 2. Cria processor
processor = DocumentProcessor(llm_provider=llm)

# 3. Processa arquivo
with open("nota.pdf", "rb") as f:
    result = processor.process_file(f.read(), "nota.pdf")

# 4. Verifica resultado
if result.success:
    print(f"Tipo: {result.tipo_documento}")
    print(f"Dados: {result.dados_extraidos}")
    print(f"Validação: {result.validacao}")
```

## 📖 Exemplos Completos

### Processar PDF

```python
from pathlib import Path
from apps.notas.llm import GeminiProvider, DocumentProcessor

llm = GeminiProvider()
processor = DocumentProcessor(llm)

pdf_path = Path("media/notas_fiscais_uploads/nfe_12345.pdf")
with open(pdf_path, 'rb') as f:
    result = processor.process_file(f.read(), pdf_path.name)

if result.success:
    nf = result.dados_extraidos
    print(f"Emissor: {nf.emissor.nome}")
    print(f"Valor: R$ {nf.valor_total}")
```

### Processar Batch

```python
arquivos = [
    (open("nf1.pdf", "rb").read(), "nf1.pdf"),
    (open("nf2.pdf", "rb").read(), "nf2.pdf"),
    (open("extrato.jpg", "rb").read(), "extrato.jpg"),
]

results = processor.process_batch(arquivos)

for r in results:
    if r.success:
        print(f"✅ {r.filename}: {r.tipo_documento}")
    else:
        print(f"❌ {r.filename}: {r.error}")
```

### PDF Grande (Paginação Automática)

```python
# PDF com 50 páginas será dividido em batches de 10
# Todos os dados são preservados (sem resumo)

with open("extrato_completo.pdf", "rb") as f:
    result = processor.process_pdf_with_pagination(f.read(), "extrato.pdf")

if result.success:
    extrato = result.dados_extraidos
    print(f"Total de lançamentos: {len(extrato.lancamentos)}")  # Todos preservados!
```

### Customizar Configurações

```python
from apps.notas.llm import GeminiProvider, DocumentProcessor

# Provider customizado
llm = GeminiProvider(
    model="gemini-1.5-pro",  # Maior precisão
    temperature=0.0          # Determinístico
)

# Processor customizado
processor = DocumentProcessor(
    llm_provider=llm,
    max_pages_per_batch=15,      # Páginas por batch
    max_images_per_batch=8,      # Imagens por chamada LLM
    min_confidence_score=0.8,    # Mínimo de confiança
    validate_results=True        # Habilita validação
)
```

## 🔧 Arquitetura

### Pipeline de Processamento

```
Arquivo (PDF/Imagem)
    ↓
[1] EXTRAÇÃO MULTIMODAL
    - PDF → Texto (pypdf)
    - PDF → Imagens (pdf2image) [fallback]
    - Imagem → Otimização (Pillow)
    ↓
[2] CLASSIFICAÇÃO
    - Identifica: NF_PRODUTO | NF_SERVICO | EXTRATO_FINANCEIRO
    - Confiança: 0.0 - 1.0
    ↓
[3] EXTRAÇÃO ESPECIALIZADA
    - Template específico por tipo
    - Pydantic schema validation
    ↓
[4] VALIDAÇÃO
    - Campos obrigatórios
    - Consistência de valores
    - Score de qualidade
    ↓
Resultado (dados estruturados)
```

### Estrutura de Módulos

```
apps/notas/llm/
├── __init__.py           # Exports públicos
├── config.py             # Configurações (API keys, limites)
├── base.py               # BaseLLMProvider (interface abstrata)
├── providers.py          # GeminiProvider, OpenAIProvider (futuro)
├── schemas.py            # Pydantic models (NotaFiscalProduto, etc)
├── extractors.py         # Extratores multimodais (PDF, Image)
├── orchestrator.py       # DocumentProcessor (pipeline completo)
├── examples.py           # Exemplos de uso
└── chains/
    ├── classifier.py     # Classificação de documentos
    ├── extractors.py     # Extração por tipo
    └── validator.py      # Validação de dados
```

## 🔌 Como Trocar de Provider

### Implementar Novo Provider

```python
from apps.notas.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from pydantic import BaseModel

class MeuProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Inicializa seu cliente
    
    def generate(self, messages: list[LLMMessage]) -> LLMResponse:
        # Implementa chamada ao LLM
        pass
    
    def generate_with_schema(
        self,
        messages: list[LLMMessage],
        schema: type[BaseModel]
    ) -> BaseModel:
        # Implementa extração estruturada
        pass
    
    def supports_vision(self) -> bool:
        return True  # Se suporta imagens
```

### Usar Novo Provider

```python
from apps.notas.llm import DocumentProcessor
from meu_modulo import MeuProvider

llm = MeuProvider(api_key="...")
processor = DocumentProcessor(llm_provider=llm)

# Todo o resto do código funciona igual!
```

## 📊 Schemas de Dados

### NotaFiscalProduto

```python
{
    "chave_acesso": "12345678901234567890123456789012345678901234",
    "numero_nota": "12345",
    "data_emissao": "2024-01-15",
    "emissor": {
        "nome": "Empresa LTDA",
        "cnpj": "12345678000190",
        "municipio": "São Paulo",
        "uf": "SP"
    },
    "produtos": [
        {
            "codigo": "PROD001",
            "descricao": "Produto Exemplo",
            "ncm": "12345678",
            "quantidade": 10.0,
            "valor_unitario": 50.00,
            "valor_total": 500.00
        }
    ],
    "valor_total": 500.00
}
```

### NotaFiscalServico

```python
{
    "codigo_verificacao": "ABC123XYZ",
    "numero_nota": "9876",
    "discriminacao": "Serviços de consultoria...",
    "prestador": {
        "nome": "Consultoria ABC",
        "cnpj": "98765432000100"
    },
    "valor_servico": 1000.00,
    "valor_iss": 50.00,
    "valor_liquido": 950.00
}
```

### ExtratoFinanceiro

```python
{
    "tipo_extrato": "VENDAS",
    "periodo_inicio": "2024-01-01",
    "periodo_fim": "2024-01-31",
    "lancamentos": [
        {
            "data": "2024-01-05",
            "descricao": "Venda NFe 12345",
            "tipo": "CREDITO",
            "valor": 500.00
        }
    ],
    "saldo_inicial": 0.00,
    "saldo_final": 500.00
}
```

## ⚙️ Configurações Avançadas

### Variáveis de Ambiente

```bash
# .env
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-1.5-flash  # ou gemini-1.5-pro
GEMINI_TEMPERATURE=0.1
MAX_PDF_PAGES_PER_BATCH=10
MAX_IMAGES_PER_BATCH=5
MIN_CONFIDENCE_SCORE=0.7
```

### Ajustar em Código

```python
from apps.notas.llm import config

# Modificar limites
config.MAX_PDF_PAGES_PER_BATCH = 20
config.MAX_IMAGES_PER_BATCH = 10
config.MIN_CONFIDENCE_SCORE = 0.85
```

## 🧪 Validação

### Campos Obrigatórios

**NF Produto:**
- `chave_acesso` (44 dígitos)
- `emissor` (pelo menos nome e CNPJ)
- `produtos` (lista não vazia)

**NF Serviço:**
- `codigo_verificacao`
- `discriminacao`
- `prestador`
- `valor_servico`

**Extrato:**
- `lancamentos` (lista não vazia)

### Validações Automáticas

```python
# Item de produto
quantidade × valor_unitario = valor_total (±0.05)

# Nota fiscal produto
valor_total = produtos + frete + seguro - desconto (±0.05)

# Nota fiscal serviço
valor_liquido = valor_servico - deduções - tributos (±0.05)

# Extrato
saldo_final = saldo_inicial + créditos - débitos (±0.05)
```

### Score de Confiança

```python
result.validacao.score_confianca  # 0.0 - 1.0

# Calculado com:
# - % de campos preenchidos
# - Penalidades: erros críticos (-20% cada)
# - Penalidades: avisos (-5% cada)
```

## 📝 Logging

```python
import logging

# Habilita logs detalhados
logging.basicConfig(level=logging.INFO)

# Logs gerados:
# - Extração multimodal (texto/imagens)
# - Classificação (tipo + confiança)
# - Extração especializada
# - Validação (erros/avisos)
# - Batches (progresso)
```

## 🤝 Integração com Sistema Existente

```python
# apps/notas/services.py

from apps.notas.llm import GeminiProvider, DocumentProcessor

class NotaFiscalService:
    def __init__(self):
        # Inicializa LLM processor
        self.llm = GeminiProvider()
        self.processor = DocumentProcessor(self.llm)
    
    def processar_nota(self, arquivo_path: str):
        # Processa com LLM
        with open(arquivo_path, 'rb') as f:
            result = self.processor.process_file(
                f.read(),
                Path(arquivo_path).name
            )
        
        if not result.success:
            raise Exception(result.error)
        
        # Salva no banco (código existente)
        nota = self._criar_nota_fiscal(result.dados_extraidos)
        
        # Notifica observers (padrão existente)
        self._notificar_observers(nota)
        
        return nota
```

## 🐛 Troubleshooting

### Erro: "pypdf não instalado"
```bash
pip install pypdf
```

### Erro: "pdf2image requires poppler"
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Windows
# Baixe poppler-utils e adicione ao PATH
```

### Erro: "GEMINI_API_KEY não configurada"
```bash
export GEMINI_API_KEY="sua_chave_aqui"
# ou adicione ao .env
```

### PDF não extrai texto
- Sistema tenta automaticamente converter para imagens
- Verifique logs para confirmar fallback

### Validação falha
- Verifique `result.validacao.erros_criticos`
- Ajuste `min_confidence_score` se necessário
- Revise qualidade do documento original

## 📚 Referências

- [Google Gemini API](https://ai.google.dev/)
- [LangChain Documentation](https://python.langchain.com/)
- [Pydantic Validation](https://docs.pydantic.dev/)

## 📄 Licença

Mesmo licenciamento do projeto principal.
