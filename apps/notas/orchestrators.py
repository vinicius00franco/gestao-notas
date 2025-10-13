import logging
from django.db import transaction
from apps.core.observers import Subject
from apps.financeiro.models import LancamentoFinanceiro
from apps.financeiro.strategies import TipoLancamentoContext
from apps.parceiros.repositories import ParceiroRepository
from apps.empresa.models import MinhaEmpresa, EmpresaNaoClassificada
from apps.empresa.repositories import EmpresaRepository
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
        logger.info(f"ORCHESTRATOR: Iniciando processamento da nota fiscal - Job ID: {job.id}, UUID: {job.uuid}")

        # 1. Extração de dados
        logger.debug(f"ORCHESTRATOR: Iniciando extração de dados do job {job.id}")
        dados_extraidos = self.extraction_service.extract_data_from_job(job)
        logger.info(f"ORCHESTRATOR: Extração concluída - Tipo: {type(dados_extraidos)}")

        # Validação: verificar se dados foram extraídos
        if not dados_extraidos:
            logger.error(f"ORCHESTRATOR: Nenhum dado extraído do job {job.id}")
            raise ValueError("Não foi possível extrair dados válidos do documento. O arquivo pode não conter uma nota fiscal ou estar corrompido.")

        logger.debug(f"ORCHESTRATOR: Dados extraídos: numero={dados_extraidos.numero}, valor={dados_extraidos.valor_total}, remetente_cnpj={dados_extraidos.remetente_cnpj}, destinatario_cnpj={dados_extraidos.destinatario_cnpj}")

        # 2. Se empresa não foi informada, tentar identificar ou criar
        empresa = None
        if job.empresa is None:
            logger.info(f"ORCHESTRATOR: Empresa não informada no job {job.id} - tentando identificar automaticamente")
            from apps.empresa.models import MinhaEmpresa, EmpresaNaoClassificada
            from apps.processamento.services import cnpj_para_numero

            cnpj_encontrado = dados_extraidos.destinatario_cnpj or dados_extraidos.remetente_cnpj
            logger.debug(f"ORCHESTRATOR: CNPJ encontrado nos dados: {cnpj_encontrado}")

            if cnpj_encontrado:
                cnpj_numero = cnpj_para_numero(cnpj_encontrado)
                logger.debug(f"ORCHESTRATOR: CNPJ convertido para número: {cnpj_numero}")
                if cnpj_numero:
                    # Primeiro tenta encontrar na MinhaEmpresa
                    try:
                        empresa = MinhaEmpresa.get_by_cnpj(cnpj_numero)
                        logger.info(f"ORCHESTRATOR: Empresa encontrada em MinhaEmpresa: {empresa} (CNPJ: {empresa.cnpj})")
                    except MinhaEmpresa.DoesNotExist:
                        logger.debug(f"ORCHESTRATOR: Empresa não encontrada em MinhaEmpresa - verificando empresas não classificadas")
                        # Se não encontrou, verifica se já existe como não classificada
                        try:
                            empresa_nao_classificada = EmpresaRepository.find_nao_classificada_by_cnpj(cnpj_numero)
                            if empresa_nao_classificada:
                                logger.info(f"ORCHESTRATOR: Empresa já existe como não classificada: {empresa_nao_classificada}")
                                # Não define empresa aqui - deixa como None para forçar criação posterior
                            else:
                                raise EmpresaNaoClassificada.DoesNotExist()
                        except EmpresaNaoClassificada.DoesNotExist:
                            logger.info(f"ORCHESTRATOR: Criando empresa como não classificada")
                            # Criar empresa como não classificada (FORA da transação)
                            nome_empresa = dados_extraidos.destinatario_nome if dados_extraidos.destinatario_cnpj == cnpj_encontrado else dados_extraidos.remetente_nome
                            nome_empresa = nome_empresa or f"Empresa {cnpj_encontrado}"

                            empresa_nao_classificada = EmpresaRepository.create_nao_classificada(
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
                            logger.info(f"ORCHESTRATOR: Empresa criada como não classificada: {empresa_nao_classificada} (CNPJ: {empresa_nao_classificada.cnpj})")
                            logger.info(f"ORCHESTRATOR: Usuário deve classificar esta empresa posteriormente através da interface administrativa")

            if empresa:
                job.empresa = empresa
                # Não salvar aqui - deixar o handler salvar no final
                logger.info(f"ORCHESTRATOR: Job associado à empresa: {empresa} (CNPJ: {empresa.cnpj})")
            else:
                logger.warning("ORCHESTRATOR: Nenhuma empresa MinhaEmpresa encontrada para o CNPJ. Empresa criada como não classificada - usuário deve classificar posteriormente.")
                # Não lança erro - permite processamento continuar sem empresa associada

        # Usar transação apenas para as operações críticas
        logger.debug(f"ORCHESTRATOR: Iniciando transação para operações críticas")
        with transaction.atomic():
            # 3. Validação
            logger.debug(f"ORCHESTRATOR: Iniciando validação CNPJ")
            self.validator.validate_cnpj_match(dados_extraidos, job.empresa or empresa)
            logger.info(f"ORCHESTRATOR: Validação CNPJ concluída")

            # 4. Determinar tipo de lançamento e dados do parceiro
            logger.debug(f"ORCHESTRATOR: Determinando tipo de lançamento e parceiro")
            resultado_strategy = self.tipo_lancamento_context.determinar_tipo_e_parceiro(
                dados_extraidos, job.empresa or empresa
            )
            logger.info(f"ORCHESTRATOR: Tipo de lançamento determinado: {resultado_strategy.get('tipo_lancamento')}")

            # 5. Criar ou atualizar parceiro
            logger.debug(f"ORCHESTRATOR: Criando/atualizando parceiro")
            parceiro = self.parceiro_repository.get_or_create(
                **resultado_strategy['parceiro_data']
            )
            logger.info(f"ORCHESTRATOR: Parceiro criado/atualizado: {parceiro}")
            self.notify('parceiro_created_or_updated', parceiro=parceiro)

            # 6. Persistir nota fiscal e lançamento financeiro
            logger.debug(f"ORCHESTRATOR: Iniciando persistência da nota fiscal e lançamento")
            lancamento = self.persistence_service.persist_nota_e_lancamento(
                job=job,
                dados_extraidos=dados_extraidos,
                parceiro=parceiro,
                tipo_lancamento=resultado_strategy['tipo_lancamento'],
            )
            logger.info(f"ORCHESTRATOR: Nota fiscal e lançamento persistidos - Lançamento ID: {lancamento.id}")

            # 7. Notificar observers sobre o novo lançamento
            logger.debug(f"ORCHESTRATOR: Notificando observers sobre novo lançamento")
            self.notify('lancamento_created', lancamento=lancamento)
            logger.info(f"ORCHESTRATOR: Observers notificados - processamento concluído com sucesso")

            return lancamento