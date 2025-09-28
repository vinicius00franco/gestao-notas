from django.db import transaction
from apps.parceiros.models import Parceiro
from apps.processamento.models import JobProcessamento
from apps.notas.models import NotaFiscal
from apps.financeiro.models import LancamentoFinanceiro
from apps.notas.extractors import ExtractorInterface, InvoiceData
from apps.classificadores.models import get_classifier

class NotaFiscalService:
    def __init__(self, extractor: ExtractorInterface):
        self.extractor = extractor

    @transaction.atomic
    def processar_nota_fiscal_do_job(self, job: JobProcessamento) -> LancamentoFinanceiro:
        minha_empresa = job.empresa
        
        file_content = job.arquivo_original.read()
        dados_extraidos = self.extractor.extract(file_content, job.arquivo_original.name)

        if dados_extraidos.destinatario_cnpj == minha_empresa.cnpj:
            tipo_lancamento = get_classifier('TIPO_LANCAMENTO', 'PAGAR')
            parceiro_data = {"cnpj": dados_extraidos.remetente_cnpj, "nome": dados_extraidos.remetente_nome, "clf_tipo": get_classifier('TIPO_PARCEIRO', 'FORNECEDOR')}
        elif dados_extraidos.remetente_cnpj == minha_empresa.cnpj:
            tipo_lancamento = get_classifier('TIPO_LANCAMENTO', 'RECEBER')
            parceiro_data = {"cnpj": dados_extraidos.destinatario_cnpj, "nome": dados_extraidos.destinatario_nome, "clf_tipo": get_classifier('TIPO_PARCEIRO', 'CLIENTE')}
        else:
            raise ValueError("Nota fiscal não pertence à sua empresa (CNPJ não corresponde).")

        parceiro = self._get_or_create_parceiro(**parceiro_data)

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
            clf_tipo=tipo_lancamento,
            clf_status=status_pendente,
            data_vencimento=dados_extraidos.data_vencimento,
        )

    def _get_or_create_parceiro(self, cnpj: str, nome: str, clf_tipo) -> Parceiro:
        parceiro, created = Parceiro.objects.get_or_create(cnpj=cnpj, defaults={'nome': nome, 'clf_tipo': clf_tipo})
        if not created:
            # Garante atualização do nome/tipo se mudou
            updated = False
            if parceiro.nome != nome:
                parceiro.nome = nome
                updated = True
            if parceiro.clf_tipo_id != clf_tipo.id:
                parceiro.clf_tipo = clf_tipo
                updated = True
            if updated:
                parceiro.save()
        return parceiro
