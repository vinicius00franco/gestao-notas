from django.utils import timezone
import logging
from .models import JobProcessamento
from apps.notas.orchestrators import NotaFiscalService
from apps.classificadores.models import get_classifier

logger = logging.getLogger(__name__)

class ProcessamentoTaskHandler:
    def __init__(self):
        self.nota_fiscal_service = NotaFiscalService()

    def handle(self, job_id: int):
        logger.info(f"CELERY: Iniciando processamento do job {job_id}")

        try:
            job = JobProcessamento.objects.get(pk=job_id)
            logger.info(f"CELERY: Job encontrado - UUID: {job.uuid}, Arquivo: {job.arquivo_original.name if job.arquivo_original else 'None'}")
        except JobProcessamento.DoesNotExist:
            logger.error(f"CELERY: Job {job_id} não encontrado")
            raise

        try:
            logger.debug(f"CELERY: Atualizando status para PROCESSANDO")
            job.status = get_classifier('STATUS_JOB', 'PROCESSANDO')
            job.save(update_fields=['status'])
            logger.info(f"CELERY: Status atualizado para PROCESSANDO")

            logger.info(f"CELERY: Chamando serviço de processamento de nota fiscal")
            self.nota_fiscal_service.processar_nota_fiscal_do_job(job)
            logger.info(f"CELERY: Processamento concluído com sucesso")

            logger.debug(f"CELERY: Atualizando status para CONCLUIDO")
            job.status = get_classifier('STATUS_JOB', 'CONCLUIDO')
            logger.info(f"CELERY: Job {job_id} finalizado com sucesso")

        except Exception as e:
            logger.error(f"CELERY: Erro no processamento do job {job_id}: {str(e)}", exc_info=True)
            logger.debug(f"CELERY: Atualizando status para ERRO")
            job.status = get_classifier('STATUS_JOB', 'ERRO')
            job.mensagem_erro = str(e)
        finally:
            job.dt_conclusao = timezone.now()
            job.save()
            logger.info(f"CELERY: Job {job_id} finalizado - Status: {job.status.descricao}")