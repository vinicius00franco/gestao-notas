"""
Repository for JobProcessamento operations.
"""

from typing import Optional
from apps.processamento.models import JobProcessamento
from apps.empresa.models import MinhaEmpresa
from apps.classificadores.models import Classificador


class JobProcessamentoRepository:
    """
    Repository for JobProcessamento CRUD operations.
    """

    @staticmethod
    def find_by_hash(hash_arquivo: str) -> Optional[JobProcessamento]:
        """Find job by file hash."""
        return JobProcessamento.objects.filter(hash_arquivo=hash_arquivo).first()

    @staticmethod
    def create_job(
        arquivo_original,
        hash_arquivo: str,
        empresa: Optional[MinhaEmpresa],
        status: Classificador
    ) -> JobProcessamento:
        """Create a new job processing."""
        return JobProcessamento.objects.create(
            arquivo_original=arquivo_original,
            hash_arquivo=hash_arquivo,
            empresa=empresa,
            status=status,
        )

    @staticmethod
    def get_by_id(job_id: int) -> JobProcessamento:
        """Get job by ID."""
        return JobProcessamento.objects.get(id=job_id)