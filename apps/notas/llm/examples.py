"""
Exemplo de uso do módulo LLM para extração de dados de notas fiscais.

Este exemplo mostra como usar o DocumentProcessor para processar PDFs e imagens
de documentos fiscais (NFe, NFSe, Extratos).
"""

import os
from pathlib import Path

# Certifique-se de que GEMINI_API_KEY está configurada
# export GEMINI_API_KEY="sua-chave-aqui"

from apps.notas.llm import (
    GeminiProvider,
    DocumentProcessor,
    TipoDocumento
)


def exemplo_basico():
    """Exemplo básico: processar um único PDF."""
    
    # 1. Inicializa o provider LLM
    llm = GeminiProvider()
    
    # 2. Cria o processador de documentos
    processor = DocumentProcessor(
        llm_provider=llm,
        validate_results=True  # Habilita validação automática
    )
    
    # 3. Lê arquivo
    pdf_path = Path("media/notas_fiscais_uploads/exemplo.pdf")
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # 4. Processa
    result = processor.process_file(pdf_bytes, pdf_path.name)
    
    # 5. Verifica resultado
    if result.success:
        print(f"✅ Sucesso!")
        print(f"Tipo: {result.tipo_documento}")
        print(f"Confiança: {result.classificacao.confianca:.2f}")
        
        if result.validacao:
            print(f"Validação: {'OK' if result.validacao.valido else 'FALHOU'}")
            print(f"Score: {result.validacao.score_qualidade:.2f}")
            
            if result.validacao.erros_criticos:
                print(f"Erros: {result.validacao.erros_criticos}")
        
        # Acessa dados extraídos
        dados = result.dados_extraidos
        
        if result.tipo_documento == TipoDocumento.NF_PRODUTO:
            print(f"\n📄 NF Produto:")
            print(f"  Chave: {dados.chave_acesso}")
            print(f"  Emissor: {dados.emissor.nome if dados.emissor else 'N/A'}")
            print(f"  Produtos: {len(dados.produtos)}")
            print(f"  Valor Total: R$ {dados.valor_total}")
        
        elif result.tipo_documento == TipoDocumento.NF_SERVICO:
            print(f"\n📄 NF Serviço:")
            print(f"  Código: {dados.codigo_verificacao}")
            print(f"  Prestador: {dados.prestador.nome if dados.prestador else 'N/A'}")
            print(f"  Valor: R$ {dados.valor_servico}")
        
        elif result.tipo_documento == TipoDocumento.EXTRATO_FINANCEIRO:
            print(f"\n📄 Extrato:")
            print(f"  Período: {dados.periodo_inicio} a {dados.periodo_fim}")
            print(f"  Lançamentos: {len(dados.lancamentos)}")
            print(f"  Saldo: R$ {dados.saldo_final}")
    
    else:
        print(f"❌ Erro: {result.error}")


def exemplo_batch():
    """Exemplo: processar múltiplos arquivos em lote."""
    
    llm = GeminiProvider()
    processor = DocumentProcessor(llm)
    
    # Lista arquivos
    upload_dir = Path("media/notas_fiscais_uploads")
    arquivos = []
    
    for file_path in upload_dir.glob("*.pdf"):
        with open(file_path, 'rb') as f:
            arquivos.append((f.read(), file_path.name))
    
    for file_path in upload_dir.glob("*.jpg"):
        with open(file_path, 'rb') as f:
            arquivos.append((f.read(), file_path.name))
    
    # Processa batch
    results = processor.process_batch(arquivos)
    
    # Resumo
    print(f"📊 Processados: {len(results)} arquivos")
    
    success_count = sum(1 for r in results if r.success)
    print(f"✅ Sucesso: {success_count}")
    print(f"❌ Erros: {len(results) - success_count}")
    
    # Detalhes por tipo
    from collections import Counter
    tipos = Counter(r.tipo_documento for r in results if r.success)
    
    print("\nDistribuição por tipo:")
    for tipo, count in tipos.items():
        print(f"  {tipo}: {count}")


def exemplo_pdf_grande():
    """Exemplo: PDF com muitas páginas (usa paginação automática)."""
    
    llm = GeminiProvider()
    processor = DocumentProcessor(
        llm_provider=llm,
        max_pages_per_batch=10,  # Processa 10 páginas por vez
        max_images_per_batch=5   # Máximo 5 imagens por chamada ao LLM
    )
    
    pdf_path = Path("media/notas_fiscais_uploads/extrato_completo.pdf")
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # Processa com paginação automática
    result = processor.process_pdf_with_pagination(pdf_bytes, pdf_path.name)
    
    if result.success:
        print(f"✅ PDF grande processado com sucesso!")
        
        if result.tipo_documento == TipoDocumento.EXTRATO_FINANCEIRO:
            extrato = result.dados_extraidos
            print(f"Total de lançamentos: {len(extrato.lancamentos)}")
            print(f"Todos os lançamentos foram preservados (sem resumo)")


def exemplo_customizado():
    """Exemplo: customizando configurações."""
    
    # Provider customizado
    llm = GeminiProvider(
        api_key=os.getenv("GEMINI_API_KEY"),
        model="gemini-1.5-flash",  # ou "gemini-1.5-pro" para maior precisão
        temperature=0.0  # Determinístico (recomendado para extração)
    )
    
    # Processor customizado
    processor = DocumentProcessor(
        llm_provider=llm,
        max_pages_per_batch=15,
        max_images_per_batch=8,
        min_confidence_score=0.8,  # Exige alta confiança
        validate_results=True
    )
    
    # Usa normalmente...
    # result = processor.process_file(...)


def exemplo_trocar_provider():
    """Exemplo: como trocar de provider (Gemini → OpenAI/Anthropic)."""
    
    # Implementação futura de outro provider:
    # from apps.notas.llm.providers import OpenAIProvider
    # llm = OpenAIProvider(api_key="...", model="gpt-4o")
    
    # Ou:
    # from apps.notas.llm.providers import AnthropicProvider
    # llm = AnthropicProvider(api_key="...", model="claude-3-5-sonnet-20241022")
    
    # O resto do código permanece IDÊNTICO:
    processor = DocumentProcessor(llm_provider=llm)  # type: ignore
    # result = processor.process_file(...)
    
    print("Para adicionar novo provider, implemente BaseLLMProvider")
    print("Ver: apps/notas/llm/base.py")


def exemplo_integracao_service():
    """Exemplo: integração com NotaFiscalService existente."""
    
    # Este código será implementado em apps/notas/services.py
    # para integrar o LLM pipeline com o sistema existente
    
    from apps.notas.llm import GeminiProvider, DocumentProcessor
    
    class NotaFiscalServiceComLLM:
        def __init__(self):
            self.llm_provider = GeminiProvider()
            self.processor = DocumentProcessor(self.llm_provider)
        
        def processar_arquivo(self, arquivo_path: str):
            """Processa arquivo usando LLM e salva no banco."""
            with open(arquivo_path, 'rb') as f:
                file_bytes = f.read()
            
            # Processa com LLM
            result = self.processor.process_file(
                file_bytes,
                Path(arquivo_path).name
            )
            
            if not result.success:
                raise Exception(f"Erro no processamento: {result.error}")
            
            # Salva no banco usando observer pattern existente
            # (código existente do NotaFiscalService)
            # ...
            
            return result.dados_extraidos


if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLOS DE USO - LLM Extraction Module")
    print("=" * 60)
    
    # Descomente o exemplo que deseja executar:
    
    # exemplo_basico()
    # exemplo_batch()
    # exemplo_pdf_grande()
    # exemplo_customizado()
    # exemplo_trocar_provider()
    # exemplo_integracao_service()
    
    print("\nDESCOMENTE um dos exemplos acima para executar!")
