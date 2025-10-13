# Estratégias de Extração - Arquitetura Refatorada

## Visão Geral

A arquitetura de extração foi refatorada seguindo os princípios SOLID, utilizando o padrão **Strategy** para implementar diferentes métodos de extração de dados de notas fiscais.

## Estrutura

```
apps/notas/strategies/
├── __init__.py              # Exports
├── base.py                  # Interface ExtractionStrategy
├── factory.py               # ExtractionStrategyFactory
├── llm_strategy.py          # LLMExtractionStrategy
├── pdf_strategy.py          # PDFExtractionStrategy
├── xml_strategy.py          # XMLExtractionStrategy
├── image_strategy.py        # ImageExtractionStrategy
└── simulated_strategy.py    # SimulatedExtractionStrategy
```

## Princípios SOLID Implementados

### 1. Single Responsibility Principle (SRP)
Cada classe de estratégia tem uma única responsabilidade:
- `LLMExtractionStrategy`: Extração usando IA
- `PDFExtractionStrategy`: Extração direta de PDFs
- `XMLExtractionStrategy`: Parsing de XML NFe
- `ImageExtractionStrategy`: OCR para imagens
- `SimulatedExtractionStrategy`: Dados simulados

### 2. Open/Closed Principle (OCP)
Novos métodos de extração podem ser adicionados sem modificar código existente:
```python
# Adicionar nova estratégia
class NewExtractionStrategy(ExtractionStrategy):
    @property
    def method(self) -> ExtractionMethod:
        return ExtractionMethod.NEW_METHOD

# Registrar no factory
ExtractionStrategyFactory._strategies[ExtractionMethod.NEW_METHOD] = NewExtractionStrategy
```

### 3. Liskov Substitution Principle (LSP)
Todas as estratégias implementam a mesma interface e podem ser usadas intercambiavelmente:
```python
def process_with_strategy(strategy: ExtractionStrategy, file_content: bytes, filename: str):
    return strategy.extract(file_content, filename)
```

### 4. Interface Segregation Principle (ISP)
Interface específica e minimalista:
```python
class ExtractionStrategy(ABC):
    @abstractmethod
    def extract(self, file_content: bytes, filename: str) -> InvoiceData: ...
    @property
    @abstractmethod
    def method(self) -> ExtractionMethod: ...
    @property
    @abstractmethod
    def name(self) -> str: ...
    @property
    @abstractmethod
    def description(self) -> str: ...
```

### 5. Dependency Inversion Principle (DIP)
O `NotaFiscalExtractionService` depende da abstração `ExtractionStrategy`, não de implementações concretas.

## Como Usar

### Configuração Estática
```python
# No extraction_service.py
ACTIVE_EXTRACTION_METHOD = ExtractionMethod.PDF  # Altere para o método desejado
```

### Configuração Dinâmica
```python
from apps.notas.extraction_service import set_extraction_method, ExtractionMethod

set_extraction_method(ExtractionMethod.XML)  # Alterar para XML
set_extraction_method(ExtractionMethod.LLM)  # Voltar para LLM
```

### Usar Factory
```python
from apps.notas.strategies.factory import ExtractionStrategyFactory

factory = ExtractionStrategyFactory()

# Criar estratégia específica
strategy = factory.create_strategy(ExtractionMethod.PDF)

# Sugerir método baseado na extensão
suggested = factory.get_strategy_for_file('nota.pdf')  # Retorna ExtractionMethod.PDF

# Listar todas disponíveis
strategies = factory.get_available_strategies()
```

## Estratégias Disponíveis

| Método | Classe | Descrição | Restrições |
|--------|--------|-----------|------------|
| `LLM` | `LLMExtractionStrategy` | IA generativa (Gemini) para análise inteligente | Apenas PDFs e imagens (jpg, jpeg, png, tiff, bmp). Ignora extratos financeiros. |
| `PDF` | `PDFExtractionStrategy` | Extração direta usando regex patterns | Apenas arquivos PDF |
| `XML` | `XMLExtractionStrategy` | Parsing estruturado de XML NFe | Apenas arquivos XML |
| `IMAGE` | `ImageExtractionStrategy` | OCR para imagens (simulado) | Apenas imagens (jpg, jpeg, png, etc.) |
| `SIMULATED` | `SimulatedExtractionStrategy` | Dados mockados para desenvolvimento | Todos os tipos de arquivo |

### Detalhes das Restrições do Método LLM

O método LLM tem as seguintes limitações específicas:

#### 📁 **Formatos de Arquivo Suportados**
- ✅ **PDF**: Arquivos PDF (digitalizados ou nativos)
- ✅ **Imagens**: JPG, JPEG, PNG, TIFF, BMP
- ❌ **Texto/XML**: TXT, XML, DOCX, XLSX, CSV (não suportados)

#### 📋 **Tipos de Documento**
- ✅ **NF_PRODUTO**: Nota Fiscal Eletrônica de Produto
- ✅ **NF_SERVICO**: Nota Fiscal de Serviços Eletrônica  
- ⚠️ **EXTRATO_FINANCEIRO**: Classificado mas **IGNORADO** (retorna `None`)

#### 🔄 **Comportamento**
- **Sem fallbacks**: Se o LLM falhar, lança `ValueError` (não tenta outros métodos)
- **Classificação obrigatória**: Documento deve ser classificado como NF válida
- **Validação rigorosa**: Apenas documentos fiscais brasileiros válidos

## Benefícios da Refatoração

1. **Manutenibilidade**: Cada estratégia é independente e fácil de modificar
2. **Extensibilidade**: Novos métodos podem ser adicionados sem impactar existentes
3. **Testabilidade**: Cada estratégia pode ser testada isoladamente
4. **Flexibilidade**: Método de extração pode ser alterado em runtime
5. **Separação de Concerns**: Lógica de negócio separada da lógica de extração
6. **Reutilização**: Estratégias podem ser usadas em outros contextos

## Exemplo de Uso Completo

```python
from apps.notas.extraction_service import NotaFiscalExtractionService, set_extraction_method, ExtractionMethod
from apps.notas.strategies.factory import ExtractionStrategyFactory

# Alterar método de extração
set_extraction_method(ExtractionMethod.PDF)

# Usar serviço (automaticamente usa a estratégia configurada)
service = NotaFiscalExtractionService()
dados = service.extract_data_from_job(job)

# Ou usar factory diretamente
factory = ExtractionStrategyFactory()
strategy = factory.create_strategy(ExtractionMethod.XML)
dados = strategy.extract(file_content, filename)
```