from django.db import transaction
from apps.parceiros.models import Parceiro
from apps.empresa.models import MinhaEmpresa
from apps.processamento.models import JobProcessamento
from apps.notas.models import NotaFiscal
from apps.financeiro.models import LancamentoFinanceiro
from apps.notas.extractors import ExtractorInterface, InvoiceData

class NotaFiscalService:
    def __init__(self, extractor: ExtractorInterface):
        self.extractor = extractor

    @transaction.atomic
    def processar_nota_fiscal_do_job(self, job: JobProcessamento) -> LancamentoFinanceiro:
        minha_empresa = MinhaEmpresa.objects.get(cnpj=job.meu_cnpj)
        
        file_content = job.arquivo_original.read()
        dados_extraidos = self.extractor.extract(file_content, job.arquivo_original.name)

        if dados_extraidos.destinatario_cnpj == minha_empresa.cnpj:
            tipo_lancamento = LancamentoFinanceiro.Tipo.PAGAR
            parceiro_data = {"cnpj": dados_extraidos.remetente_cnpj, "nome": dados_extraidos.remetente_nome, "tipo": Parceiro.Tipo.FORNECEDOR}
        elif dados_extraidos.remetente_cnpj == minha_empresa.cnpj:
            tipo_lancamento = LancamentoFinanceiro.Tipo.RECEBER
            parceiro_data = {"cnpj": dados_extraidos.destinatario_cnpj, "nome": dados_extraidos.destinatario_nome, "tipo": Parceiro.Tipo.CLIENTE}
        else:
            raise ValueError("Nota fiscal não pertence à sua empresa (CNPJ não corresponde).")

        parceiro = self._get_or_create_parceiro(**parceiro_data)
        
        nota_fiscal = NotaFiscal.objects.create(
            job_origem=job, parceiro=parceiro, numero=dados_extraidos.numero,
            data_emissao=dados_extraidos.data_emissao, valor_total=dados_extraidos.valor_total
        )
        
        return LancamentoFinanceiro.objects.create(
            nota_fiscal=nota_fiscal, descricao=f"NF {nota_fiscal.numero} - {parceiro.nome}",
            valor=nota_fiscal.valor_total, tipo=tipo_lancamento, data_vencimento=dados_extraidos.data_vencimento
        )

    def _get_or_create_parceiro(self, cnpj: str, nome: str, tipo: str) -> Parceiro:
        parceiro, _ = Parceiro.objects.get_or_create(cnpj=cnpj, defaults={'nome': nome, 'tipo': tipo})
        return parceiro
