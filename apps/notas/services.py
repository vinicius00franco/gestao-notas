from django.db import transaction
from apps.parceiros.models import Parceiro
from apps.processamento.models import JobProcessamento
from apps.notas.models import NotaFiscal
from apps.financeiro.models import LancamentoFinanceiro
from apps.notas.extractors import ExtractorInterface, ExtractorFactory
from apps.financeiro.strategies import TipoLancamentoContext
from apps.classificadores.models import get_classifier

class NotaFiscalService:
    def __init__(self, extractor: ExtractorInterface = None, tipo_lancamento_context: TipoLancamentoContext = None):
        self.extractor = extractor
        self.tipo_lancamento_context = tipo_lancamento_context or TipoLancamentoContext()

    @transaction.atomic
    def processar_nota_fiscal_do_job(self, job: JobProcessamento) -> LancamentoFinanceiro:
        minha_empresa = job.empresa
        
        # Usa factory se extractor não foi fornecido
        extractor = self.extractor or ExtractorFactory.get_extractor(job.arquivo_original.name)
        
        file_content = job.arquivo_original.read()
        dados_extraidos = extractor.extract(file_content, job.arquivo_original.name)

        # Usa strategy para determinar tipo e parceiro
        resultado = self.tipo_lancamento_context.determinar_tipo_e_parceiro(dados_extraidos, minha_empresa)
        
        parceiro = self._get_or_create_parceiro(**resultado['parceiro_data'])

        nota_fiscal = NotaFiscal.objects.create(
            job_origem=job,
            parceiro=parceiro,
            numero=dados_extraidos.numero,
            data_emissao=dados_extraidos.data_emissao,
            valor_total=dados_extraidos.valor_total,
        )

        status_pendente = get_classifier('STATUS_LANCAMENTO', 'PENDENTE')
        return LancamentoFinanceiro.objects.create(
            nota_fiscal=nota_fiscal,
            descricao=f"NF {nota_fiscal.numero} - {parceiro.nome}",
            valor=nota_fiscal.valor_total,
            clf_tipo=resultado['tipo_lancamento'],
            clf_status=status_pendente,
            data_vencimento=dados_extraidos.data_vencimento,
        )

    def _get_or_create_parceiro(self, cnpj: str, nome: str, clf_tipo) -> Parceiro:
        parceiro, created = Parceiro.objects.get_or_create(cnpj=cnpj, defaults={'nome': nome, 'clf_tipo': clf_tipo})
        if not created:
            update_fields = []
            if parceiro.nome != nome:
                parceiro.nome = nome
                update_fields.append('nome')
            if parceiro.clf_tipo_id != clf_tipo.id:
                parceiro.clf_tipo = clf_tipo
                update_fields.append('clf_tipo')
            if update_fields:
                parceiro.save(update_fields=update_fields)
        return parceiro
