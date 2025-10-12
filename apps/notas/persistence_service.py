import logging
from decimal import Decimal, InvalidOperation
from apps.notas.models import NotaFiscal, NotaFiscalItem
from apps.financeiro.models import LancamentoFinanceiro
from apps.classificadores.models import get_classifier

logger = logging.getLogger(__name__)

class NotaFiscalPersistenceService:
    def persist_nota_e_lancamento(self, job, dados_extraidos, parceiro, tipo_lancamento) -> LancamentoFinanceiro:
        nota_fiscal = NotaFiscal.objects.create(
            job_origem=job,
            parceiro=parceiro,
            chave_acesso=getattr(dados_extraidos, 'chave_acesso', None),
            numero=dados_extraidos.numero,
            data_emissao=dados_extraidos.data_emissao,
            valor_total=dados_extraidos.valor_total,
        )
        self._persistir_itens_da_nota(nota_fiscal, dados_extraidos)

        status_pendente = get_classifier('STATUS_LANCAMENTO', 'PENDENTE')
        lancamento = LancamentoFinanceiro.objects.create(
            nota_fiscal=nota_fiscal,
            descricao=f"NF {nota_fiscal.numero} - {parceiro.nome}",
            valor=nota_fiscal.valor_total,
            clf_tipo=tipo_lancamento,
            clf_status=status_pendente,
            data_vencimento=dados_extraidos.data_vencimento,
        )
        return lancamento

    def _persistir_itens_da_nota(self, nota_fiscal, dados_extraidos):
        itens = getattr(dados_extraidos, 'produtos', []) or getattr(dados_extraidos, 'itens', [])
        if not itens:
            return

        for item_data in itens:
            try:
                quantidade = Decimal(str(item_data.get('quantidade', 0)))
                valor_unitario = Decimal(str(item_data.get('valor_unitario', 0)))
                valor_total = Decimal(str(item_data.get('valor_total', 0)))

                NotaFiscalItem.objects.create(
                    nota_fiscal=nota_fiscal,
                    descricao=item_data.get('descricao', 'Item')[:255],
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    valor_total=valor_total,
                )
            except (InvalidOperation, TypeError, ValueError) as e:
                logger.warning("Item da nota fiscal inválido: %s", e)
                continue