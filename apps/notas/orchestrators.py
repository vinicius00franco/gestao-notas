import logging
from django.db import transaction
from apps.core.observers import Subject
from apps.financeiro.models import LancamentoFinanceiro
from apps.financeiro.strategies import TipoLancamentoContext
from apps.parceiros.repositories import ParceiroRepository
from .services.extraction import NotaFiscalExtractionService
from .services.persistence import NotaFiscalPersistenceService
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

    @transaction.atomic
    def processar_nota_fiscal_do_job(self, job) -> LancamentoFinanceiro:
        # 1. Extração de dados
        dados_extraidos = self.extraction_service.extract_data_from_job(job)

        # 2. Validação
        self.validator.validate_cnpj_match(dados_extraidos, job.empresa)

        # 3. Determinar tipo de lançamento e dados do parceiro
        resultado_strategy = self.tipo_lancamento_context.determinar_tipo_e_parceiro(
            dados_extraidos, job.empresa
        )

        # 3. Criar ou atualizar parceiro
        parceiro = self.parceiro_repository.get_or_create(
            **resultado_strategy['parceiro_data']
        )
        self.notify('parceiro_created_or_updated', parceiro=parceiro)

        # 4. Persistir nota fiscal e lançamento financeiro
        lancamento = self.persistence_service.persist_nota_e_lancamento(
            job=job,
            dados_extraidos=dados_extraidos,
            parceiro=parceiro,
            tipo_lancamento=resultado_strategy['tipo_lancamento'],
        )

        # 5. Notificar observers sobre o novo lançamento
        self.notify('lancamento_created', lancamento=lancamento)

        return lancamento