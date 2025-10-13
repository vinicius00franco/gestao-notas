"""
Queries using Django ORM for basic operations and raw SQL for complex queries.
Basic CRUD operations use ORM, complex queries use raw SQL for performance.
"""

from django.db import connection
from apps.notas.models import NotaFiscal, NotaFiscalItem
from decimal import Decimal


def get_notas_fiscais_por_parceiro(parceiro_id: int) -> list[dict]:
    """
    Busca todas as notas fiscais de um parceiro.
    Mantém SQL para performance em consultas com joins.
    """
    query = """
        SELECT
            ntf.ntf_id,
            ntf.ntf_uuid,
            ntf.ntf_chave_acesso,
            ntf.ntf_numero,
            ntf.ntf_data_emissao,
            ntf.ntf_valor_total
        FROM
            movimento_notas_fiscais ntf
        WHERE
            ntf.pcr_id = %s
        ORDER BY
            ntf.ntf_data_emissao DESC;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [parceiro_id])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_top_fornecedores_pendentes() -> list[dict]:
    """
    Busca por fornecedores com lançamentos pendentes.
    Mantém SQL complexo para performance com múltiplos joins e agregações.
    """
    query = """
        SELECT p.pcr_nome as nome, p.pcr_cnpj as cnpj, SUM(l.lcf_valor) as total_a_pagar
        FROM cadastro_parceiros p
        JOIN movimento_notas_fiscais nf ON nf.pcr_id = p.pcr_id
        JOIN movimento_lancamentos_financeiros l ON l.ntf_id = nf.ntf_id
        JOIN geral_classificadores tipo ON tipo.clf_id = l.clf_id_tipo AND tipo.clf_tipo = 'TIPO_LANCAMENTO' AND tipo.clf_codigo = 'PAGAR'
        JOIN geral_classificadores status ON status.clf_id = l.clf_id_status AND status.clf_tipo = 'STATUS_LANCAMENTO' AND status.clf_codigo = 'PENDENTE'
        GROUP BY p.pcr_id, p.pcr_nome, p.pcr_cnpj
        ORDER BY total_a_pagar DESC LIMIT 5;
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def create_nota_fiscal(job_id: int, parceiro_id: int, chave_acesso: str, numero: str, data_emissao: str, valor_total: float) -> int:
    """
    Cria uma nova nota fiscal usando Django ORM.
    Operação básica de insert - usa ORM para consistência.
    """
    from apps.processamento.models import JobProcessamento
    from apps.parceiros.models import Parceiro

    job = JobProcessamento.objects.get(id=job_id)
    parceiro = Parceiro.objects.get(id=parceiro_id)

    nota_fiscal = NotaFiscal.objects.create(
        job_origem=job,
        parceiro=parceiro,
        chave_acesso=chave_acesso if chave_acesso else None,
        numero=numero,
        data_emissao=data_emissao,
        valor_total=Decimal(str(valor_total))
    )

    return nota_fiscal.id


def create_nota_fiscal_item(nota_fiscal_id: int, descricao: str, quantidade: float, valor_unitario: float, valor_total: float):
    """
    Cria um novo item de nota fiscal usando Django ORM.
    Operação básica de insert - usa ORM para consistência.
    """
    nota_fiscal = NotaFiscal.objects.get(id=nota_fiscal_id)

    NotaFiscalItem.objects.create(
        nota_fiscal=nota_fiscal,
        descricao=descricao,
        quantidade=Decimal(str(quantidade)),
        valor_unitario=Decimal(str(valor_unitario)),
        valor_total=Decimal(str(valor_total))
    )