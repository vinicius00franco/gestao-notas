from django.db import connection

def get_top_fornecedores_pendentes() -> list[dict]:
    # Busca por fornecedores com lançamentos pendentes, usando db_table novas
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
