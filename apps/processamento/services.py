from .models import JobProcessamento
from .publishers import CeleryTaskPublisher
from apps.empresa.models import MinhaEmpresa
from apps.classificadores.models import get_classifier

class ProcessamentoService:
    def criar_job_processamento(self, cnpj: str, arquivo) -> JobProcessamento:
        try:
            empresa = MinhaEmpresa.objects.get(cnpj=cnpj)
        except MinhaEmpresa.DoesNotExist:
            raise ValueError("Empresa com CNPJ informado não encontrada")

        status_pendente = get_classifier('STATUS_JOB', 'PENDENTE')
        job = JobProcessamento.objects.create(
            arquivo_original=arquivo,
            empresa=empresa,
            status=status_pendente,
        )
        CeleryTaskPublisher().publish_processamento_nota(job_id=job.id)
        return job