"""
Schemas Pydantic para extração estruturada de dados.
Define modelos para Nota Fiscal de Produto, Serviço e Extrato Financeiro.
"""
from decimal import Decimal
from datetime import date
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class ItemNota(BaseModel):
    """Item de nota fiscal."""
    codigo: Optional[str] = Field(None, description="Código/SKU do produto/serviço")
    descricao: str = Field(..., description="Descrição do item")
    quantidade: Decimal = Field(..., description="Quantidade", gt=0)
    unidade: Optional[str] = Field(None, description="Unidade (UN, KG, L, etc)")
    valor_unitario: Decimal = Field(..., description="Valor unitário", ge=0)
    valor_total: Decimal = Field(..., description="Valor total do item", ge=0)
    ncm: Optional[str] = Field(None, description="Código NCM (produtos)")
    
    @field_validator('valor_total')
    @classmethod
    def validar_valor_total(cls, v, info):
        """Valida consistência do valor total."""
        if 'quantidade' in info.data and 'valor_unitario' in info.data:
            esperado = info.data['quantidade'] * info.data['valor_unitario']
            # Tolera pequenas diferenças por arredondamento
            if abs(v - esperado) > Decimal('0.02'):
                raise ValueError(
                    f"Valor total inconsistente: {v} != "
                    f"{info.data['quantidade']} x {info.data['valor_unitario']}"
                )
        return v


class EmissorDestinatario(BaseModel):
    """Dados de emissor ou destinatário."""
    nome: str = Field(..., description="Razão social ou nome")
    cnpj_cpf: str = Field(..., description="CNPJ ou CPF")
    endereco: Optional[str] = Field(None, description="Endereço completo")
    cidade: Optional[str] = Field(None, description="Cidade")
    uf: Optional[str] = Field(None, max_length=2, description="UF (sigla estado)")
    cep: Optional[str] = Field(None, description="CEP")
    inscricao_estadual: Optional[str] = Field(None, description="Inscrição Estadual")


class NotaFiscalProduto(BaseModel):
    """Nota Fiscal de Produto (NFe)."""
    tipo_documento: Literal['nf_produto'] = 'nf_produto'
    numero: str = Field(..., description="Número da nota fiscal")
    serie: Optional[str] = Field(None, description="Série da nota")
    chave_acesso: Optional[str] = Field(None, description="Chave de acesso de 44 dígitos")
    
    data_emissao: date = Field(..., description="Data de emissão")
    data_saida_entrada: Optional[date] = Field(None, description="Data de saída/entrada")
    
    emissor: EmissorDestinatario = Field(..., description="Dados do emissor")
    destinatario: EmissorDestinatario = Field(..., description="Dados do destinatário")
    
    itens: List[ItemNota] = Field(..., min_length=1, description="Itens da nota")
    
    valor_produtos: Decimal = Field(..., description="Valor total dos produtos", ge=0)
    valor_frete: Optional[Decimal] = Field(None, description="Valor do frete", ge=0)
    valor_seguro: Optional[Decimal] = Field(None, description="Valor do seguro", ge=0)
    valor_desconto: Optional[Decimal] = Field(None, description="Valor de desconto", ge=0)
    valor_outras_despesas: Optional[Decimal] = Field(None, description="Outras despesas", ge=0)
    valor_total: Decimal = Field(..., description="Valor total da nota", ge=0)
    
    natureza_operacao: Optional[str] = Field(None, description="Natureza da operação")
    cfop: Optional[str] = Field(None, description="CFOP principal")
    
    informacoes_adicionais: Optional[str] = Field(None, description="Informações complementares")
    
    @field_validator('valor_total')
    @classmethod
    def validar_valor_total_nota(cls, v, info):
        """Valida que valor total é consistente."""
        if 'valor_produtos' in info.data:
            base = info.data['valor_produtos']
            base += info.data.get('valor_frete') or Decimal('0')
            base += info.data.get('valor_seguro') or Decimal('0')
            base += info.data.get('valor_outras_despesas') or Decimal('0')
            base -= info.data.get('valor_desconto') or Decimal('0')
            
            if abs(v - base) > Decimal('0.10'):
                raise ValueError(
                    f"Valor total inconsistente: {v} != calculado {base}"
                )
        return v


class NotaFiscalServico(BaseModel):
    """Nota Fiscal de Serviço (NFSe)."""
    tipo_documento: Literal['nf_servico'] = 'nf_servico'
    numero: str = Field(..., description="Número da nota fiscal de serviço")
    codigo_verificacao: Optional[str] = Field(None, description="Código de verificação")
    
    data_emissao: date = Field(..., description="Data de emissão")
    data_competencia: Optional[date] = Field(None, description="Data de competência")
    
    prestador: EmissorDestinatario = Field(..., description="Dados do prestador")
    tomador: EmissorDestinatario = Field(..., description="Dados do tomador")
    
    discriminacao_servico: str = Field(..., description="Discriminação/descrição do serviço")
    codigo_servico: Optional[str] = Field(None, description="Código do serviço municipal")
    codigo_cnae: Optional[str] = Field(None, description="Código CNAE")
    
    valor_servicos: Decimal = Field(..., description="Valor dos serviços", ge=0)
    valor_deducoes: Optional[Decimal] = Field(None, description="Valor de deduções", ge=0)
    valor_pis: Optional[Decimal] = Field(None, description="Valor PIS", ge=0)
    valor_cofins: Optional[Decimal] = Field(None, description="Valor COFINS", ge=0)
    valor_inss: Optional[Decimal] = Field(None, description="Valor INSS", ge=0)
    valor_ir: Optional[Decimal] = Field(None, description="Valor IR", ge=0)
    valor_csll: Optional[Decimal] = Field(None, description="Valor CSLL", ge=0)
    valor_iss: Optional[Decimal] = Field(None, description="Valor ISS", ge=0)
    valor_outras_retencoes: Optional[Decimal] = Field(None, description="Outras retenções", ge=0)
    aliquota_iss: Optional[Decimal] = Field(None, description="Alíquota ISS (%)", ge=0, le=100)
    valor_liquido: Decimal = Field(..., description="Valor líquido", ge=0)
    
    informacoes_adicionais: Optional[str] = Field(None, description="Informações complementares")


class LancamentoExtrato(BaseModel):
    """Lançamento de extrato bancário/financeiro."""
    data: date = Field(..., description="Data do lançamento")
    descricao: str = Field(..., description="Descrição/histórico")
    documento: Optional[str] = Field(None, description="Número do documento")
    valor: Decimal = Field(..., description="Valor (positivo=crédito, negativo=débito)")
    tipo: Literal['credito', 'debito'] = Field(..., description="Tipo de lançamento")
    
    @field_validator('tipo')
    @classmethod
    def inferir_tipo_por_valor(cls, v, info):
        """Infere tipo baseado no sinal do valor."""
        if 'valor' in info.data:
            valor = info.data['valor']
            if valor > 0 and v == 'debito':
                return 'credito'
            elif valor < 0 and v == 'credito':
                return 'debito'
        return v


class ExtratoFinanceiro(BaseModel):
    """Extrato financeiro (vendas/compras)."""
    tipo_documento: Literal['extrato'] = 'extrato'
    tipo_extrato: Literal['vendas', 'compras', 'bancario'] = Field(
        ...,
        description="Tipo de extrato"
    )
    
    periodo_inicio: date = Field(..., description="Data inicial do período")
    periodo_fim: date = Field(..., description="Data final do período")
    
    empresa_nome: Optional[str] = Field(None, description="Nome da empresa")
    empresa_cnpj: Optional[str] = Field(None, description="CNPJ da empresa")
    
    lancamentos: List[LancamentoExtrato] = Field(
        ...,
        min_length=1,
        description="Lançamentos do extrato"
    )
    
    saldo_inicial: Optional[Decimal] = Field(None, description="Saldo inicial")
    saldo_final: Optional[Decimal] = Field(None, description="Saldo final")
    total_creditos: Optional[Decimal] = Field(None, description="Total de créditos", ge=0)
    total_debitos: Optional[Decimal] = Field(None, description="Total de débitos", ge=0)


class DocumentoClassificado(BaseModel):
    """Resultado da classificação de documento."""
    tipo: Literal['nf_produto', 'nf_servico', 'extrato', 'desconhecido'] = Field(
        ...,
        description="Tipo de documento identificado"
    )
    confianca: float = Field(..., ge=0, le=1, description="Nível de confiança (0-1)")
    razoes: List[str] = Field(..., description="Razões para a classificação")
    
    # Metadados úteis
    possui_chave_acesso: Optional[bool] = Field(None, description="Tem chave de acesso NFe")
    possui_codigo_verificacao: Optional[bool] = Field(None, description="Tem código verificação NFSe")
    possui_lancamentos_multiplos: Optional[bool] = Field(None, description="Múltiplos lançamentos (extrato)")
    menciona_produtos: Optional[bool] = Field(None, description="Menciona produtos")
    menciona_servicos: Optional[bool] = Field(None, description="Menciona serviços")


class ResultadoValidacao(BaseModel):
    """Resultado da validação de dados extraídos."""
    valido: bool = Field(..., description="Se os dados passaram na validação")
    score_qualidade: float = Field(..., ge=0, le=1, description="Score de qualidade (0-1)")
    
    erros_criticos: List[str] = Field(default_factory=list, description="Erros que impedem uso")
    avisos: List[str] = Field(default_factory=list, description="Avisos de qualidade")
    
    campos_faltantes: List[str] = Field(default_factory=list, description="Campos obrigatórios faltantes")
    campos_inconsistentes: List[str] = Field(default_factory=list, description="Campos com valores inconsistentes")
    
    sugestoes_correcao: List[str] = Field(default_factory=list, description="Sugestões de correção")
