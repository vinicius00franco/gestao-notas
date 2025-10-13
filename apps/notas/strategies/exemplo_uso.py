"""
Exemplo de uso das Estratégias de Extração

Este arquivo demonstra como usar as diferentes estratégias de extração
implementadas seguindo o padrão Strategy e princípios SOLID.
"""

from apps.notas.strategies.factory import ExtractionStrategyFactory, ExtractionMethod
from apps.notas.strategies.base import ExtractionStrategy
from apps.notas.extraction_service import NotaFiscalExtractionService, set_extraction_method


def exemplo_uso_basico():
    """Exemplo básico de uso das estratégias"""
    print("=== Exemplo Básico ===")

    factory = ExtractionStrategyFactory()

    # Listar estratégias disponíveis
    strategies = factory.get_available_strategies()
    print("Estratégias disponíveis:")
    for method, info in strategies.items():
        print(f"  {method.value}: {info['name']} - {info['description']}")

    # Criar estratégia específica
    pdf_strategy = factory.create_strategy(ExtractionMethod.PDF)
    print(f"\nEstratégia criada: {pdf_strategy.name}")
    print(f"Método: {pdf_strategy.method.value}")
    print(f"Descrição: {pdf_strategy.description}")


def exemplo_sugestoes_por_extensao():
    """Exemplo de sugestões baseadas na extensão do arquivo"""
    print("\n=== Sugestões por Extensão ===")

    factory = ExtractionStrategyFactory()

    arquivos = [
        'nota-fiscal.pdf',
        'nfe.xml',
        'imagem-nota.jpg',
        'nota-texto.txt',
        'documento.docx'
    ]

    for arquivo in arquivos:
        suggested = factory.get_strategy_for_file(arquivo)
        print(f"{arquivo} -> {suggested.value}")


def exemplo_alteracao_dinamica():
    """Exemplo de alteração dinâmica do método de extração"""
    print("\n=== Alteração Dinâmica ===")

    # Configurar método inicial
    set_extraction_method(ExtractionMethod.LLM)
    service = NotaFiscalExtractionService()
    print(f"Método inicial: {service._extraction_method}")

    # Alterar para PDF
    set_extraction_method(ExtractionMethod.PDF)
    print(f"Método alterado: {service._extraction_method}")

    # Alterar para XML
    set_extraction_method(ExtractionMethod.XML)
    print(f"Método alterado: {service._extraction_method}")


def exemplo_extensibilidade():
    """Exemplo de como adicionar uma nova estratégia"""
    print("\n=== Extensibilidade ===")

    # Simular adição de nova estratégia
    class NovaEstrategia(ExtractionStrategy):
        @property
        def method(self):
            return ExtractionMethod.LLM  # Reutilizando enum existente

        @property
        def name(self):
            return "Nova Estratégia"

        @property
        def description(self):
            return "Exemplo de nova estratégia de extração"

        def extract(self, file_content, filename):
            # Implementação da nova estratégia
            return {"nova_estrategia": True}

    # Registrar no factory (simulado)
    print("Nova estratégia poderia ser registrada:")
    print("ExtractionStrategyFactory._strategies[ExtractionMethod.NEW_METHOD] = NovaEstrategia")
    print("Sem modificar código existente!")


def exemplo_restricoes_llm():
    """Exemplo das restrições específicas do método LLM"""
    print("\n=== Restrições do Método LLM ===")
    
    from apps.notas.llm import TipoDocumento
    
    print("📁 Formatos suportados:")
    formatos_suportados = ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp']
    formatos_nao_suportados = ['txt', 'xml', 'docx', 'xlsx', 'csv']
    
    print("  ✅ Suportados:", ', '.join(formatos_suportados))
    print("  ❌ Não suportados:", ', '.join(formatos_nao_suportados))
    
    print("\n📋 Tipos de documento:")
    print(f"  ✅ {TipoDocumento.NF_PRODUTO.value} - Nota Fiscal de Produto")
    print(f"  ✅ {TipoDocumento.NF_SERVICO.value} - Nota Fiscal de Serviço")
    print(f"  ⚠️  {TipoDocumento.EXTRATO_FINANCEIRO.value} - IGNORADO (retorna None)")
    
    print("\n🔄 Comportamento:")
    print("  - Sem fallbacks automáticos")
    print("  - Lança ValueError se falhar")
    print("  - Requer documentos fiscais brasileiros válidos")


def exemplo_testabilidade():
    """Exemplo de como testar estratégias isoladamente"""
    print("\n=== Testabilidade ===")

    factory = ExtractionStrategyFactory()

    # Testar cada estratégia isoladamente
    for method in ExtractionMethod:
        try:
            strategy = factory.create_strategy(method)
            print(f"✅ {method.value}: {strategy.name} - OK")
        except Exception as e:
            print(f"❌ {method.value}: Erro - {e}")


if __name__ == "__main__":
    exemplo_uso_basico()
    exemplo_sugestoes_por_extensao()
    exemplo_alteracao_dinamica()
    exemplo_extensibilidade()
    exemplo_restricoes_llm()
    exemplo_testabilidade()

    print("\n=== Resumo ===")
    print("✅ Princípios SOLID implementados")
    print("✅ Padrão Strategy aplicado")
    print("✅ Código mais manutenível e extensível")
    print("✅ Sem if/else chains")
    print("✅ Sem fallbacks automáticos")