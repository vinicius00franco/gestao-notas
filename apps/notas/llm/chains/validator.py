"""
Chain de validação de dados extraídos.
Verifica completude, consistência e qualidade dos dados.
"""
from typing import Union, List
from decimal import Decimal

from ..schemas import (
    NotaFiscalProduto,
    NotaFiscalServico,
    ExtratoFinanceiro,
    ResultadoValidacao,
    ItemNota,
    LancamentoExtrato
)


class DataValidator:
    """Valida dados extraídos de documentos."""
    
    def __init__(
        self,
        min_confidence_score: float = 0.7,
        strict_mode: bool = False
    ):
        self.min_confidence = min_confidence_score
        self.strict_mode = strict_mode
    
    def validate_nf_produto(self, nf: NotaFiscalProduto) -> ResultadoValidacao:
        """Valida NF Produto."""
        erros_criticos = []
        avisos = []
        campos_faltantes = []
        sugestoes = []
        
        # Campos obrigatórios
        if not nf.chave_acesso:
            erros_criticos.append("Chave de acesso ausente (obrigatória)")
        elif len(nf.chave_acesso) != 44:
            erros_criticos.append(f"Chave de acesso inválida: {len(nf.chave_acesso)} dígitos (esperado 44)")
        
        if not nf.emissor:
            erros_criticos.append("Dados do emissor ausentes")
        elif not nf.emissor.cnpj:
            avisos.append("CNPJ do emissor ausente")
        
        if not nf.destinatario:
            avisos.append("Dados do destinatário ausentes")
        
        if not nf.produtos or len(nf.produtos) == 0:
            erros_criticos.append("Nenhum produto encontrado")
        
        # Validação de produtos
        if nf.produtos:
            for i, produto in enumerate(nf.produtos):
                erros_produto = self._validate_item(produto, i)
                avisos.extend(erros_produto)
        
        # Validação de totais
        if nf.valor_total is not None:
            valor_calculado = (
                (nf.valor_produtos or Decimal(0)) +
                (nf.valor_frete or Decimal(0)) +
                (nf.valor_seguro or Decimal(0)) -
                (nf.valor_desconto or Decimal(0))
            )
            
            diff = abs(nf.valor_total - valor_calculado)
            if diff > Decimal("0.05"):  # Tolerância de 5 centavos
                avisos.append(
                    f"Valor total inconsistente: declarado {nf.valor_total}, "
                    f"calculado {valor_calculado} (diferença: {diff})"
                )
        
        # Campos opcionais faltantes
        if not nf.data_emissao:
            campos_faltantes.append("data_emissao")
        if not nf.numero_nota:
            campos_faltantes.append("numero_nota")
        if nf.valor_icms is None:
            campos_faltantes.append("valor_icms")
        
        # Sugestões
        if nf.emissor and not nf.emissor.inscricao_estadual:
            sugestoes.append("Incluir inscrição estadual do emissor se disponível")
        
        # Score de confiança
        score = self._calculate_score(
            total_campos=15,  # Aproximado
            campos_preenchidos=self._count_filled_fields_nf_produto(nf),
            erros_criticos=len(erros_criticos),
            avisos=len(avisos)
        )
        
        return ResultadoValidacao(
            valido=len(erros_criticos) == 0,
            score_confianca=score,
            erros_criticos=erros_criticos,
            avisos=avisos,
            campos_faltantes=campos_faltantes,
            sugestoes=sugestoes
        )
    
    def validate_nf_servico(self, nf: NotaFiscalServico) -> ResultadoValidacao:
        """Valida NF Serviço."""
        erros_criticos = []
        avisos = []
        campos_faltantes = []
        sugestoes = []
        
        # Campos obrigatórios
        if not nf.codigo_verificacao:
            erros_criticos.append("Código de verificação ausente (obrigatório)")
        
        if not nf.discriminacao:
            erros_criticos.append("Discriminação do serviço ausente")
        elif len(nf.discriminacao) < 10:
            avisos.append("Discriminação muito curta (pode estar incompleta)")
        
        if not nf.prestador:
            erros_criticos.append("Dados do prestador ausentes")
        
        if not nf.tomador:
            avisos.append("Dados do tomador ausentes")
        
        # Validação de valores
        if nf.valor_servico is None:
            erros_criticos.append("Valor do serviço ausente")
        
        if nf.valor_liquido is not None and nf.valor_servico is not None:
            valor_calculado = (
                nf.valor_servico -
                (nf.valor_deducoes or Decimal(0)) -
                (nf.valor_pis or Decimal(0)) -
                (nf.valor_cofins or Decimal(0)) -
                (nf.valor_csll or Decimal(0)) -
                (nf.valor_ir or Decimal(0)) -
                (nf.valor_inss or Decimal(0))
            )
            
            diff = abs(nf.valor_liquido - valor_calculado)
            if diff > Decimal("0.05"):
                avisos.append(
                    f"Valor líquido inconsistente: declarado {nf.valor_liquido}, "
                    f"calculado {valor_calculado}"
                )
        
        # Campos opcionais
        if not nf.data_emissao:
            campos_faltantes.append("data_emissao")
        if nf.valor_iss is None:
            campos_faltantes.append("valor_iss")
        if nf.aliquota_iss is None:
            campos_faltantes.append("aliquota_iss")
        
        # Score
        score = self._calculate_score(
            total_campos=20,
            campos_preenchidos=self._count_filled_fields_nf_servico(nf),
            erros_criticos=len(erros_criticos),
            avisos=len(avisos)
        )
        
        return ResultadoValidacao(
            valido=len(erros_criticos) == 0,
            score_confianca=score,
            erros_criticos=erros_criticos,
            avisos=avisos,
            campos_faltantes=campos_faltantes,
            sugestoes=sugestoes
        )
    
    def validate_extrato(self, extrato: ExtratoFinanceiro) -> ResultadoValidacao:
        """Valida Extrato Financeiro."""
        erros_criticos = []
        avisos = []
        campos_faltantes = []
        sugestoes = []
        
        # Campos obrigatórios
        if not extrato.lancamentos or len(extrato.lancamentos) == 0:
            erros_criticos.append("Nenhum lançamento encontrado")
        
        # Validação de lançamentos
        if extrato.lancamentos:
            for i, lanc in enumerate(extrato.lancamentos):
                if not lanc.data:
                    avisos.append(f"Lançamento {i+1}: data ausente")
                if not lanc.descricao:
                    avisos.append(f"Lançamento {i+1}: descrição ausente")
                if lanc.valor is None or lanc.valor <= 0:
                    avisos.append(f"Lançamento {i+1}: valor inválido ou ausente")
        
        # Validação de totais
        if extrato.saldo_final is not None and extrato.saldo_inicial is not None:
            total_cred = extrato.total_creditos or Decimal(0)
            total_deb = extrato.total_debitos or Decimal(0)
            
            saldo_calculado = extrato.saldo_inicial + total_cred - total_deb
            diff = abs(extrato.saldo_final - saldo_calculado)
            
            if diff > Decimal("0.05"):
                avisos.append(
                    f"Saldo final inconsistente: declarado {extrato.saldo_final}, "
                    f"calculado {saldo_calculado}"
                )
        
        # Campos opcionais
        if not extrato.periodo_inicio:
            campos_faltantes.append("periodo_inicio")
        if not extrato.periodo_fim:
            campos_faltantes.append("periodo_fim")
        if extrato.saldo_inicial is None:
            campos_faltantes.append("saldo_inicial")
        
        # Sugestões
        if len(extrato.lancamentos) > 100:
            sugestoes.append(
                "Extrato com muitos lançamentos - considere dividir por período"
            )
        
        # Score
        score = self._calculate_score(
            total_campos=8 + len(extrato.lancamentos) * 4,
            campos_preenchidos=self._count_filled_fields_extrato(extrato),
            erros_criticos=len(erros_criticos),
            avisos=len(avisos)
        )
        
        return ResultadoValidacao(
            valido=len(erros_criticos) == 0,
            score_confianca=score,
            erros_criticos=erros_criticos,
            avisos=avisos,
            campos_faltantes=campos_faltantes,
            sugestoes=sugestoes
        )
    
    def validate(
        self,
        documento: Union[NotaFiscalProduto, NotaFiscalServico, ExtratoFinanceiro]
    ) -> ResultadoValidacao:
        """
        Valida documento automaticamente baseado no tipo.
        
        Args:
            documento: Documento extraído
            
        Returns:
            ResultadoValidacao
        """
        if isinstance(documento, NotaFiscalProduto):
            return self.validate_nf_produto(documento)
        elif isinstance(documento, NotaFiscalServico):
            return self.validate_nf_servico(documento)
        elif isinstance(documento, ExtratoFinanceiro):
            return self.validate_extrato(documento)
        else:
            raise TypeError(f"Tipo de documento não suportado: {type(documento)}")
    
    # ========================================================================
    # HELPERS
    # ========================================================================
    
    def _validate_item(self, item: ItemNota, index: int) -> List[str]:
        """Valida item de nota fiscal."""
        erros = []
        
        if not item.descricao:
            erros.append(f"Item {index+1}: descrição ausente")
        
        if item.quantidade is None or item.quantidade <= 0:
            erros.append(f"Item {index+1}: quantidade inválida")
        
        if item.valor_unitario is None or item.valor_unitario <= 0:
            erros.append(f"Item {index+1}: valor unitário inválido")
        
        if item.valor_total is None or item.valor_total <= 0:
            erros.append(f"Item {index+1}: valor total inválido")
        
        # Validação já feita no schema, mas verificamos novamente
        if all([item.quantidade, item.valor_unitario, item.valor_total]):
            calculado = item.quantidade * item.valor_unitario
            diff = abs(item.valor_total - calculado)
            if diff > Decimal("0.05"):
                erros.append(
                    f"Item {index+1}: valor total inconsistente "
                    f"({item.quantidade} × {item.valor_unitario} ≠ {item.valor_total})"
                )
        
        return erros
    
    def _calculate_score(
        self,
        total_campos: int,
        campos_preenchidos: int,
        erros_criticos: int,
        avisos: int
    ) -> float:
        """Calcula score de confiança."""
        # Base: % de campos preenchidos
        base_score = campos_preenchidos / total_campos if total_campos > 0 else 0.0
        
        # Penalidades
        penalidade_erros = erros_criticos * 0.2
        penalidade_avisos = avisos * 0.05
        
        score = max(0.0, base_score - penalidade_erros - penalidade_avisos)
        return min(1.0, score)
    
    def _count_filled_fields_nf_produto(self, nf: NotaFiscalProduto) -> int:
        """Conta campos preenchidos em NF Produto."""
        count = 0
        
        if nf.chave_acesso: count += 1
        if nf.numero_nota: count += 1
        if nf.serie: count += 1
        if nf.data_emissao: count += 1
        if nf.emissor and nf.emissor.nome: count += 1
        if nf.emissor and nf.emissor.cnpj: count += 1
        if nf.destinatario and nf.destinatario.nome: count += 1
        if nf.produtos: count += len(nf.produtos)
        if nf.valor_produtos is not None: count += 1
        if nf.valor_total is not None: count += 1
        if nf.valor_icms is not None: count += 1
        
        return count
    
    def _count_filled_fields_nf_servico(self, nf: NotaFiscalServico) -> int:
        """Conta campos preenchidos em NF Serviço."""
        count = 0
        
        if nf.numero_nota: count += 1
        if nf.codigo_verificacao: count += 1
        if nf.data_emissao: count += 1
        if nf.prestador and nf.prestador.nome: count += 1
        if nf.tomador and nf.tomador.nome: count += 1
        if nf.discriminacao: count += 1
        if nf.valor_servico is not None: count += 1
        if nf.valor_iss is not None: count += 1
        if nf.valor_liquido is not None: count += 1
        if nf.aliquota_iss is not None: count += 1
        
        return count
    
    def _count_filled_fields_extrato(self, extrato: ExtratoFinanceiro) -> int:
        """Conta campos preenchidos em Extrato."""
        count = 0
        
        if extrato.periodo_inicio: count += 1
        if extrato.periodo_fim: count += 1
        if extrato.saldo_inicial is not None: count += 1
        if extrato.saldo_final is not None: count += 1
        if extrato.lancamentos:
            count += len(extrato.lancamentos) * 3  # data, descricao, valor
        
        return count
