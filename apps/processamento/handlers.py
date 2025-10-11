from django.utils import timezone
from .models import JobProcessamento
from apps.notas.orchestrators import NotaFiscalService
from apps.classificadores.models import get_classifier

class ProcessamentoTaskHandler:
    def __init__(self):
        self.nota_fiscal_service = NotaFiscalService()

    def handle(self, job_id: int):
        job = JobProcessamento.objects.get(pk=job_id)
        try:
            job.status = get_classifier('STATUS_JOB', 'PROCESSANDO')
            job.save(update_fields=['status'])

            self.nota_fiscal_service.processar_nota_fiscal_do_job(job)

            job.status = get_classifier('STATUS_JOB', 'CONCLUIDO')
        except Exception as e:
            job.status = get_classifier('STATUS_JOB', 'FALHA')
            job.mensagem_erro = str(e)
        finally:
            job.dt_conclusao = timezone.now()
            job.save()