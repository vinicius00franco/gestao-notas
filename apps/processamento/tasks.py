from celery import shared_task
from .handlers import ProcessamentoTaskHandler

@shared_task(autoretry_for=(Exception,), retry_backoff=True, retry_backoff_max=300, retry_jitter=True)
def processar_nota_fiscal_task(job_id: int):
    handler = ProcessamentoTaskHandler()
    handler.handle(job_id)
    return f"Job {job_id} finalizado."