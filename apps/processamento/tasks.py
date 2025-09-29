from celery import shared_task
from django.utils import timezone
from apps.processamento.models import JobProcessamento
from apps.notas.services import NotaFiscalService
from apps.classificadores.models import get_classifier

@shared_task
def processar_nota_fiscal_task(job_id: int):
    job = JobProcessamento.objects.get(pk=job_id)
    try:
        job.status = get_classifier('STATUS_JOB', 'PROCESSANDO')
        job.save()

        # Service agora usa factory automaticamente
        service = NotaFiscalService()
        service.processar_nota_fiscal_do_job(job)

        job.status = get_classifier('STATUS_JOB', 'CONCLUIDO')
    except Exception as e:
        job.status = get_classifier('STATUS_JOB', 'FALHA')
        job.mensagem_erro = str(e)
    finally:
        job.dt_conclusao = timezone.now()
        job.save()
    return f"Job {job_id} finalizado com status: {job.status.codigo}"
