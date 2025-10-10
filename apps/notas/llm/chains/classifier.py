"""
Chain de classificação de documentos.
Identifica tipo de documento: NF Produto, NF Serviço ou Extrato Financeiro.
"""
from typing import List, Optional

from ..base import BaseLLMProvider, LLMMessage
from ..schemas import DocumentoClassificado


CLASSIFICATION_PROMPT = """Você é um especialista em análise de documentos fiscais brasileiros.

Analise o documento fornecido e classifique-o em uma das seguintes categorias:

1. **NF_PRODUTO** (Nota Fiscal Eletrônica de Produto - NFe):
   - Documento fiscal de venda de mercadorias
   - Possui chave de acesso de 44 dígitos
   - Contém lista de produtos com CFOP, NCM, CST
   - Totais: valor produtos, frete, seguro, desconto, ICMS, IPI
   - Exemplo: vendas de loja, distribuidora, indústria

2. **NF_SERVICO** (Nota Fiscal de Serviços Eletrônica - NFSe):
   - Documento fiscal de prestação de serviços
   - Possui código de verificação
   - Discriminação do serviço prestado
   - Tributos: ISS, PIS, COFINS, CSLL, IR, INSS
   - Exemplo: consultoria, manutenção, software, advocacia

3. **EXTRATO_FINANCEIRO**:
   - Extrato bancário ou relatório financeiro
   - Lista de lançamentos (débitos/créditos) com datas
   - Pode ser extrato de vendas ou compras
   - Contém saldo inicial/final
   - Exemplo: extrato conta corrente, relatório de vendas

**CRITÉRIOS DE DECISÃO:**
- Se encontrar "CHAVE DE ACESSO" com 44 dígitos → NF_PRODUTO
- Se encontrar "CÓDIGO DE VERIFICAÇÃO" e discriminação de serviço → NF_SERVICO
- Se encontrar múltiplos lançamentos com data/valor/descrição → EXTRATO_FINANCEIRO
- Se tiver CFOP ou NCM → NF_PRODUTO
- Se tiver ISS destacado → NF_SERVICO

**INSTRUÇÕES:**
1. Analise o documento cuidadosamente
2. Identifique palavras-chave e estrutura
3. Classifique com confiança (0.0 a 1.0)
4. Explique as razões da classificação

Retorne a classificação no formato JSON especificado.
"""


class DocumentClassifier:
    """Classifica documentos usando LLM."""
    
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider
    
    def classify(
        self,
        text: Optional[str] = None,
        images: Optional[List[bytes]] = None
    ) -> DocumentoClassificado:
        """
        Classifica documento.
        
        Args:
            text: Texto extraído do documento (se disponível)
            images: Imagens do documento (se disponível)
            
        Returns:
            DocumentoClassificado com tipo e confiança
        """
        if not text and not images:
            raise ValueError("Forneça texto ou imagens")
        
        # Prepara mensagens
        messages = [
            LLMMessage(
                role="system",
                content=CLASSIFICATION_PROMPT
            ),
            LLMMessage(
                role="user",
                content=text or "Analise as imagens do documento.",
                images=images
            )
        ]
        
        # Gera classificação estruturada
        result = self.llm.generate_with_schema(
            messages=messages,
            schema=DocumentoClassificado
        )
        
        return result
    
    def classify_batch(
        self,
        documents: List[tuple[Optional[str], Optional[List[bytes]]]]
    ) -> List[DocumentoClassificado]:
        """
        Classifica múltiplos documentos.
        
        Args:
            documents: Lista de (texto, imagens)
            
        Returns:
            Lista de DocumentoClassificado
        """
        results = []
        for text, images in documents:
            classified = self.classify(text, images)
            results.append(classified)
        
        return results
