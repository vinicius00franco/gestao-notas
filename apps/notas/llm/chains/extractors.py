"""
Chains especializadas para extração de cada tipo de documento.
"""
import logging
from typing import List, Optional, Union

from ..base import BaseLLMProvider, LLMMessage
from ..schemas import (
    NotaFiscalProduto,
    NotaFiscalServico,
    ExtratoFinanceiro,
    TipoDocumento
)

logger = logging.getLogger(__name__)


# ============================================================================
# PROMPTS DE EXTRAÇÃO
# ============================================================================

PROMPT_NF_PRODUTO = """Você é um especialista em extração de dados de Notas Fiscais Eletrônicas (NFe) de produto.

Extraia as seguintes informações do documento:

**IDENTIFICAÇÃO:**
- chave_acesso: 44 dígitos (obrigatório)
- numero_nota: Número da NF
- serie: Série da NF
- data_emissao: Data no formato YYYY-MM-DD

**EMISSOR:**
- nome, cnpj, inscricao_estadual
- logradouro, numero, bairro, municipio, uf, cep

**DESTINATÁRIO:**
- nome, cnpj/cpf
- logradouro, numero, bairro, municipio, uf, cep

**PRODUTOS (lista):**
Para cada item:
- codigo: Código do produto
- descricao: Descrição
- ncm: Código NCM (8 dígitos)
- cfop: CFOP (4 dígitos)
- unidade: Unidade de medida
- quantidade: Quantidade numérica
- valor_unitario: Valor unitário
- valor_total: Valor total do item
- icms: Alíquota ICMS (%)
- ipi: Alíquota IPI (%)

**TOTAIS:**
- valor_produtos: Soma dos produtos
- valor_frete: Frete
- valor_seguro: Seguro
- valor_desconto: Desconto
- valor_icms: Total ICMS
- valor_ipi: Total IPI
- valor_total: Valor total da nota

**INSTRUÇÕES:**
1. Extraia todos os campos com precisão
2. Use None se campo não encontrado
3. Valores numéricos como float/Decimal
4. Datas no formato YYYY-MM-DD
5. Valide: quantidade × valor_unitario = valor_total (por item)
6. Valide: valor_total = produtos + frete + seguro - desconto
7. Se o documento NÃO contiver dados de nota fiscal válida, retorne dados vazios/nulos
8. Não invente dados - apenas extraia informações realmente presentes no documento

Retorne JSON seguindo o schema especificado.
"""

PROMPT_NF_SERVICO = """Você é um especialista em extração de dados de Notas Fiscais de Serviço (NFSe).

Extraia as seguintes informações do documento:

**IDENTIFICAÇÃO:**
- numero_nota: Número da NFS
- codigo_verificacao: Código de verificação (obrigatório)
- data_emissao: Data no formato YYYY-MM-DD

**PRESTADOR:**
- nome, cnpj, inscricao_municipal
- logradouro, numero, bairro, municipio, uf, cep

**TOMADOR:**
- nome, cnpj/cpf
- logradouro, numero, bairro, municipio, uf, cep

**SERVIÇO:**
- discriminacao: Descrição detalhada do serviço prestado
- codigo_servico: Código do serviço
- aliquota_iss: Alíquota ISS (%)

**VALORES:**
- valor_servico: Valor bruto do serviço
- valor_deducoes: Deduções
- valor_iss: ISS destacado
- valor_pis: PIS retido
- valor_cofins: COFINS retido
- valor_csll: CSLL retido
- valor_ir: IR retido
- valor_inss: INSS retido
- valor_liquido: Valor líquido

**INSTRUÇÕES:**
1. Extraia todos os campos com precisão
2. Use None se campo não encontrado
3. Valores numéricos como float/Decimal
4. Datas no formato YYYY-MM-DD
5. Discriminação completa (texto longo permitido)
6. Todos os tributos detalhados
7. Se o documento NÃO contiver dados de nota fiscal de serviço válida, retorne dados vazios/nulos
8. Não invente dados - apenas extraia informações realmente presentes no documento

Retorne JSON seguindo o schema especificado.
"""

PROMPT_EXTRATO = """Você é um especialista em extração de dados de extratos financeiros.

Extraia as seguintes informações do documento:

**IDENTIFICAÇÃO:**
- tipo_extrato: "VENDAS" ou "COMPRAS" (inferir do contexto)
- periodo_inicio: Data inicial (YYYY-MM-DD)
- periodo_fim: Data final (YYYY-MM-DD)

**TITULAR (se aplicável):**
- nome, cpf/cnpj
- Se não identificável, use None

**LANÇAMENTOS (lista):**
Para cada lançamento:
- data: Data do lançamento (YYYY-MM-DD)
- descricao: Descrição da operação
- tipo: "CREDITO" ou "DEBITO" (inferir: valor positivo=crédito, negativo=débito)
- valor: Valor absoluto (sempre positivo)
- saldo: Saldo após lançamento (se disponível)

**TOTAIS:**
- saldo_inicial: Saldo inicial do período
- saldo_final: Saldo final do período
- total_creditos: Soma de todos os créditos
- total_debitos: Soma de todos os débitos

**INSTRUÇÕES:**
1. Extraia TODOS os lançamentos (não resuma!)
2. Se extrato tiver mais de 50 lançamentos, extraia todos mesmo assim
3. Infira tipo (CREDITO/DEBITO) automaticamente do valor
4. Valores sempre positivos (tipo indica direção)
5. Ordem cronológica
6. Valide: saldo_final = saldo_inicial + total_creditos - total_debitos
7. Se o documento NÃO contiver dados de extrato financeiro válido, retorne dados vazios/nulos
8. Não invente dados - apenas extraia informações realmente presentes no documento

Retorne JSON seguindo o schema especificado.
"""


# ============================================================================
# EXTRACTORS
# ============================================================================

class NotaFiscalProdutoExtractor:
    """Extrai dados de NF Produto (NFe)."""
    
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider
    
    def extract(
        self,
        text: Optional[str] = None,
        images: Optional[List[bytes]] = None
    ) -> NotaFiscalProduto:
        """
        Extrai dados de NFe.
        
        Args:
            text: Texto da nota
            images: Imagens da nota
            
        Returns:
            NotaFiscalProduto validado
        """
        if not text and not images:
            raise ValueError("Forneça texto ou imagens")
        
        messages = [
            LLMMessage(role="system", content=PROMPT_NF_PRODUTO),
            LLMMessage(
                role="user",
                content=text or "Extraia dados da NFe nas imagens.",
                images=images
            )
        ]
        
        result = self.llm.generate_with_schema(
            messages=messages,
            schema=NotaFiscalProduto
        )
        
        # Validação básica: verificar se dados essenciais estão presentes
        if not result or not hasattr(result, 'numero') or not result.numero:
            logger.warning("Nenhum dado válido de NF Produto extraído")
            return None
        
        return result


class NotaFiscalServicoExtractor:
    """Extrai dados de NF Serviço (NFSe)."""
    
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider
    
    def extract(
        self,
        text: Optional[str] = None,
        images: Optional[List[bytes]] = None
    ) -> NotaFiscalServico:
        """
        Extrai dados de NFSe.
        
        Args:
            text: Texto da nota
            images: Imagens da nota
            
        Returns:
            NotaFiscalServico validado
        """
        if not text and not images:
            raise ValueError("Forneça texto ou imagens")
        
        messages = [
            LLMMessage(role="system", content=PROMPT_NF_SERVICO),
            LLMMessage(
                role="user",
                content=text or "Extraia dados da NFSe nas imagens.",
                images=images
            )
        ]
        
        result = self.llm.generate_with_schema(
            messages=messages,
            schema=NotaFiscalServico
        )
        
        # Validação básica: verificar se dados essenciais estão presentes
        if not result or not hasattr(result, 'numero') or not result.numero:
            logger.warning("Nenhum dado válido de NF Serviço extraído")
            return None
        
        return result


class ExtratoFinanceiroExtractor:
    """Extrai dados de Extrato Financeiro."""
    
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider
    
    def extract(
        self,
        text: Optional[str] = None,
        images: Optional[List[bytes]] = None
    ) -> ExtratoFinanceiro:
        """
        Extrai dados de extrato.
        
        Args:
            text: Texto do extrato
            images: Imagens do extrato
            
        Returns:
            ExtratoFinanceiro validado
        """
        if not text and not images:
            raise ValueError("Forneça texto ou imagens")
        
        messages = [
            LLMMessage(role="system", content=PROMPT_EXTRATO),
            LLMMessage(
                role="user",
                content=text or "Extraia dados do extrato nas imagens.",
                images=images
            )
        ]
        
        result = self.llm.generate_with_schema(
            messages=messages,
            schema=ExtratoFinanceiro
        )
        
        # Validação básica: verificar se dados essenciais estão presentes
        if not result or not hasattr(result, 'lancamentos') or not result.lancamentos:
            logger.warning("Nenhum dado válido de extrato financeiro extraído")
            return None
        
        return result


# ============================================================================
# FACTORY
# ============================================================================

class ExtractorFactory:
    """Factory para obter extractor apropriado baseado no tipo de documento."""
    
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider
        self._extractors = {
            TipoDocumento.NF_PRODUTO: NotaFiscalProdutoExtractor(llm_provider),
            TipoDocumento.NF_SERVICO: NotaFiscalServicoExtractor(llm_provider),
            TipoDocumento.EXTRATO_FINANCEIRO: ExtratoFinanceiroExtractor(llm_provider),
        }
    
    def get_extractor(
        self,
        tipo: TipoDocumento
    ) -> Union[NotaFiscalProdutoExtractor, NotaFiscalServicoExtractor, ExtratoFinanceiroExtractor]:
        """Retorna extractor apropriado para o tipo de documento."""
        return self._extractors[tipo]
    
    def extract(
        self,
        tipo: TipoDocumento,
        text: Optional[str] = None,
        images: Optional[List[bytes]] = None
    ) -> Union[NotaFiscalProduto, NotaFiscalServico, ExtratoFinanceiro]:
        """
        Extrai dados usando extractor apropriado.
        
        Args:
            tipo: Tipo do documento
            text: Texto do documento
            images: Imagens do documento
            
        Returns:
            Dados extraídos (tipo depende do documento)
        """
        extractor = self.get_extractor(tipo)
        return extractor.extract(text, images)
