from django.db import connection
from apps.financeiro.models import LancamentoFinanceiro

def get_top_fornecedores_pendentes() -> list[dict]:
    query = """
        SELECT p.nome, p.cnpj, SUM(l.valor) as total_a_pagar
        FROM parceiros_parceiro p
        JOIN notas_notafiscal nf ON nf.parceiro_id = p.id
        JOIN financeiro_lancamentofinanceiro l ON l.nota_fiscal_id = nf.id
        WHERE l.tipo = %s AND l.status = %s
        GROUP BY p.id, p.nome, p.cnpj ORDER BY total_a_pagar DESC LIMIT 5;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [LancamentoFinanceiro.Tipo.PAGAR, LancamentoFinanceiro.Status.PENDENTE])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
