"""
Repository for Empresa operations.
"""

from typing import Optional
from apps.empresa.models import EmpresaNaoClassificada


class EmpresaRepository:
    """
    Repository for Empresa operations.
    """

    @staticmethod
    def find_nao_classificada_by_cnpj(cnpj_numero: int) -> Optional[EmpresaNaoClassificada]:
        """Find non-classified company by CNPJ number."""
        try:
            return EmpresaNaoClassificada.objects.get(cnpj_numero=cnpj_numero)
        except EmpresaNaoClassificada.DoesNotExist:
            return None

    @staticmethod
    def create_nao_classificada(
        cnpj_numero: int,
        cnpj: str,
        nome_fantasia: str,
        razao_social: str,
        uf: str = '',
        cidade: str = '',
        logradouro: str = '',
        numero: str = '',
        bairro: str = '',
        cep: str = '',
        telefone: str = '',
        email: str = ''
    ) -> EmpresaNaoClassificada:
        """Create a new non-classified company."""
        return EmpresaNaoClassificada.objects.create(
            cnpj_numero=cnpj_numero,
            cnpj=cnpj,
            nome_fantasia=nome_fantasia,
            razao_social=razao_social,
            uf=uf,
            cidade=cidade,
            logradouro=logradouro,
            numero=numero,
            bairro=bairro,
            cep=cep,
            telefone=telefone,
            email=email
        )