from celery import shared_task
from django.utils import timezone
from apps.processamento.models import JobProcessamento
from apps.notas.services import NotaFiscalService
from apps.notas.extractors import SimulatedExtractor

@shared_task
def processar_nota_fiscal_task(job_id: int):
    job = JobProcessamento.objects.get(pk=job_id)
    try:
        job.status = JobProcessamento.Status.PROCESSANDO
        job.save()

        extractor = SimulatedExtractor()
        service = NotaFiscalService(extractor=extractor)
        service.processar_nota_fiscal_do_job(job)

        job.status = JobProcessamento.Status.CONCLUIDO
    except Exception as e:
        job.status = JobProcessamento.Status.FALHA
        job.mensagem_erro = str(e)
    finally:
        job.dt_conclusao = timezone.now()
        job.save()
    return f"Job {job_id} finalizado com status: {job.status}"
