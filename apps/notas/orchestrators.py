import logging
from django.db import transaction
from apps.core.observers import Subject
from apps.financeiro.models import LancamentoFinanceiro
from apps.financeiro.strategies import TipoLancamentoContext
from apps.parceiros.repositories import ParceiroRepository
from .extraction_service import NotaFiscalExtractionService
from .persistence_service import NotaFiscalPersistenceService
from .validators import NotaFiscalValidator
from apps.financeiro.observers import AlertaVencimentoObserver
from apps.dashboard.observers import MetricasFinanceirasObserver
from apps.parceiros.observers import ValidacaoCNPJObserver
from apps.notifications.observers import PushStoreObserver

logger = logging.getLogger(__name__)

class NotaFiscalService(Subject):
    def __init__(self):
        super().__init__()
        self.extraction_service = NotaFiscalExtractionService()
        self.persistence_service = NotaFiscalPersistenceService()
        self.parceiro_repository = ParceiroRepository()
        self.tipo_lancamento_context = TipoLancamentoContext()
        self.validator = NotaFiscalValidator()
        self._register_observers()

    def _register_observers(self):
        self.attach(AlertaVencimentoObserver())
        self.attach(MetricasFinanceirasObserver())
        self.attach(ValidacaoCNPJObserver())
        try:
            self.attach(PushStoreObserver())
        except Exception:
            logger.warning("PushStoreObserver não pôde ser registrado.")

    def processar_nota_fiscal_do_job(self, job) -> LancamentoFinanceiro:
        # 1. Extração de dados
        dados_extraidos = self.extraction_service.extract_data_from_job(job)

        # 2. Se empresa não foi informada, tentar identificar ou criar
        empresa = None
        if job.empresa is None:
            from apps.empresa.models import MinhaEmpresa, EmpresaNaoClassificada
            from apps.processamento.services import cnpj_para_numero
            
            cnpj_encontrado = dados_extraidos.destinatario_cnpj or dados_extraidos.remetente_cnpj
            
            if cnpj_encontrado:
                cnpj_numero = cnpj_para_numero(cnpj_encontrado)
                if cnpj_numero:
                    # Primeiro tenta encontrar na MinhaEmpresa
                    try:
                        empresa = MinhaEmpresa.get_by_cnpj(cnpj_numero)
                        logger.info(f"Empresa encontrada em MinhaEmpresa: {empresa} (CNPJ: {empresa.cnpj})")
                    except MinhaEmpresa.DoesNotExist:
                        # Se não encontrou, verifica se já existe como não classificada
                        try:
                            empresa_nao_classificada = EmpresaNaoClassificada.objects.get(cnpj_numero=cnpj_numero)
                            logger.info(f"Empresa já existe como não classificada: {empresa_nao_classificada}")
                            # Não define empresa aqui - deixa como None para forçar criação posterior
                        except EmpresaNaoClassificada.DoesNotExist:
                            # Criar empresa como não classificada (FORA da transação)
                            nome_empresa = dados_extraidos.destinatario_nome if dados_extraidos.destinatario_cnpj == cnpj_encontrado else dados_extraidos.remetente_nome
                            nome_empresa = nome_empresa or f"Empresa {cnpj_encontrado}"
                            
                            empresa_nao_classificada = EmpresaNaoClassificada(
                                cnpj_numero=cnpj_numero,
                                cnpj=cnpj_encontrado,
                                nome_fantasia=nome_empresa,
                                razao_social=nome_empresa,  # Usar mesmo nome por enquanto
                                uf='',  # Campos vazios - usuário preencherá depois
                                cidade='',
                                logradouro='',
                                numero='',
                                bairro='',
                                cep='',
                                telefone='',
                                email=''
                            )
                            empresa_nao_classificada.save()  # Salvar FORA da transação
                            logger.info(f"Empresa criada como não classificada: {empresa_nao_classificada} (CNPJ: {empresa_nao_classificada.cnpj})")
                            logger.info(f"Usuário deve classificar esta empresa posteriormente através da interface administrativa")
            
            if empresa:
                job.empresa = empresa
                # Não salvar aqui - deixar o handler salvar no final
                logger.info(f"Job associado à empresa: {empresa} (CNPJ: {empresa.cnpj})")
            else:
                logger.warning("Nenhuma empresa MinhaEmpresa encontrada para o CNPJ. Empresa criada como não classificada - usuário deve classificar posteriormente.")
                # Não lança erro - permite processamento continuar sem empresa associada

        # Usar transação apenas para as operações críticas
        with transaction.atomic():
            # 3. Validação
            self.validator.validate_cnpj_match(dados_extraidos, job.empresa or empresa)

            # 4. Determinar tipo de lançamento e dados do parceiro
            resultado_strategy = self.tipo_lancamento_context.determinar_tipo_e_parceiro(
                dados_extraidos, job.empresa or empresa
            )

            # 5. Criar ou atualizar parceiro
            parceiro = self.parceiro_repository.get_or_create(
                **resultado_strategy['parceiro_data']
            )
            self.notify('parceiro_created_or_updated', parceiro=parceiro)

            # 6. Persistir nota fiscal e lançamento financeiro
            lancamento = self.persistence_service.persist_nota_e_lancamento(
                job=job,
                dados_extraidos=dados_extraidos,
                parceiro=parceiro,
                tipo_lancamento=resultado_strategy['tipo_lancamento'],
            )

            # 7. Notificar observers sobre o novo lançamento
            self.notify('lancamento_created', lancamento=lancamento)

            return lancamento