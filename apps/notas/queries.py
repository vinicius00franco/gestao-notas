from django.db import connection

def get_notas_fiscais_por_parceiro(parceiro_id: int) -> list[dict]:
    """
    Busca todas as notas fiscais de um parceiro.
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

def create_nota_fiscal(job_id: int, parceiro_id: int, chave_acesso: str, numero: str, data_emissao: str, valor_total: float) -> int:
    """
    Cria uma nova nota fiscal e retorna o ID.
    """
    query = """
        INSERT INTO movimento_notas_fiscais
            (jbp_id, pcr_id, ntf_chave_acesso, ntf_numero, ntf_data_emissao, ntf_valor_total)
        VALUES
            (%s, %s, %s, %s, %s, %s)
        RETURNING ntf_id;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [job_id, parceiro_id, chave_acesso, numero, data_emissao, valor_total])
        return cursor.fetchone()[0]

def create_nota_fiscal_item(nota_fiscal_id: int, descricao: str, quantidade: float, valor_unitario: float, valor_total: float):
    """
    Cria um novo item de nota fiscal.
    """
    query = """
        INSERT INTO movimento_nota_fiscal_itens
            (ntf_id, nfi_descricao, nfi_quantidade, nfi_valor_unitario, nfi_valor_total)
        VALUES
            (%s, %s, %s, %s, %s);
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [nota_fiscal_id, descricao, quantidade, valor_unitario, valor_total])