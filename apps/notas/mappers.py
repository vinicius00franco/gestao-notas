"""
Mapping utilities to convert LLM schemas to the canonical InvoiceData used by legacy strategies.
"""
from typing import Optional
from datetime import date as _date

from apps.notas.extractors import InvoiceData
from apps.notas.llm.schemas import NotaFiscalProduto, NotaFiscalServico, TipoDocumento


def llm_to_invoice(doc, tipo_documento: TipoDocumento) -> Optional[InvoiceData]:
    """Convert LLM schema object to InvoiceData."""
    if tipo_documento == TipoDocumento.NF_PRODUTO and isinstance(doc, NotaFiscalProduto):
        numero = getattr(doc, 'numero_nota', None) or getattr(doc, 'chave_acesso', 'S/NUM')
        data_emissao = getattr(doc, 'data_emissao', None) or _date.today()
        data_vencimento = getattr(doc, 'data_vencimento', None) or data_emissao
        emissor = getattr(doc, 'emissor', None)
        destinatario = getattr(doc, 'destinatario', None)

        inv = InvoiceData(
            numero=str(numero),
            remetente_cnpj=(getattr(emissor, 'cnpj', None) or ""),
            remetente_nome=(getattr(emissor, 'nome', None) or ""),
            destinatario_cnpj=(getattr(destinatario, 'cnpj', None) or getattr(destinatario, 'cpf', None) or ""),
            destinatario_nome=(getattr(destinatario, 'nome', None) or ""),
            valor_total=getattr(doc, 'valor_total', None) or getattr(doc, 'valor_produtos', None),
            data_emissao=data_emissao,
            data_vencimento=data_vencimento,
        )
        setattr(inv, 'produtos', getattr(doc, 'produtos', None))
        setattr(inv, 'chave_acesso', getattr(doc, 'chave_acesso', None))
        return inv

    if tipo_documento == TipoDocumento.NF_SERVICO and isinstance(doc, NotaFiscalServico):
        numero = getattr(doc, 'numero_nota', None) or 'S/NUM'
        data_emissao = getattr(doc, 'data_emissao', None) or _date.today()
        data_vencimento = getattr(doc, 'data_vencimento', None) or data_emissao
        prestador = getattr(doc, 'prestador', None)
        tomador = getattr(doc, 'tomador', None)
        valor_total = getattr(doc, 'valor_liquido', None) or getattr(doc, 'valor_servico', None)

        inv = InvoiceData(
            numero=str(numero),
            remetente_cnpj=(getattr(prestador, 'cnpj', None) or ""),
            remetente_nome=(getattr(prestador, 'nome', None) or ""),
            destinatario_cnpj=(getattr(tomador, 'cnpj', None) or getattr(tomador, 'cpf', None) or ""),
            destinatario_nome=(getattr(tomador, 'nome', None) or ""),
            valor_total=valor_total,
            data_emissao=data_emissao,
            data_vencimento=data_vencimento,
        )
        setattr(inv, 'produtos', None)
        return inv

    return None
