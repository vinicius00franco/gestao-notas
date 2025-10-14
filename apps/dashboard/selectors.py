from datetime import date, timedelta
from django.db import connection
from django.db.models import Sum, Count
from apps.classificadores.models import Classificador, get_classifier
from apps.financeiro.models import LancamentoFinanceiro
from apps.notas.models import NotaFiscal
from apps.parceiros.models import Parceiro


def get_period_dates(period: str) -> tuple[date, date]:
    today = date.today()
    if period == 'last_7_days':
        start_date = today - timedelta(days=7)
    elif period == 'last_month':
        start_date = today - timedelta(days=30)
    elif period == 'last_3_months':
        start_date = today - timedelta(days=90)
    elif period == 'last_year':
        start_date = today - timedelta(days=365)
    else: # Default to last 30 days
        start_date = today - timedelta(days=30)
    return start_date, today

def get_total_revenue(start_date: date, end_date: date) -> float:
    """Calcula a receita total no período."""
    tipo_receita = get_classifier('TIPO_LANCAMENTO', 'RECEITA')
    total = LancamentoFinanceiro.objects.filter(
        clf_tipo=tipo_receita,
        data_pagamento__range=(start_date, end_date)
    ).aggregate(total=Sum('valor'))['total']
    return total or 0.0

def get_pending_payments(start_date: date, end_date: date) -> float:
    """Soma o valor das contas a pagar pendentes."""
    tipo_pagar = get_classifier('TIPO_LANCAMENTO', 'PAGAR')
    status_pendente = get_classifier('STATUS_LANCAMENTO', 'PENDENTE')
    total = LancamentoFinanceiro.objects.filter(
        clf_tipo=tipo_pagar,
        clf_status=status_pendente,
        data_vencimento__range=(start_date, end_date)
    ).aggregate(total=Sum('valor'))['total']
    return total or 0.0

def get_processed_invoices_count(start_date: date, end_date: date) -> int:
    """Conta o número de notas fiscais processadas."""
    return NotaFiscal.objects.filter(data_emissao__range=(start_date, end_date)).count()

def get_active_suppliers_count(start_date: date, end_date: date) -> int:
    """Conta o número de fornecedores ativos."""
    return Parceiro.objects.filter(
        notas_fiscais__data_emissao__range=(start_date, end_date)
    ).distinct().count()

def get_revenue_evolution() -> list[dict]:
    """Retorna a evolução da receita nos últimos 6 meses."""
    query = """
        SELECT
            to_char(DATE_TRUNC('month', l.lcf_data_pagamento), 'YYYY-MM') as month,
            SUM(l.lcf_valor) as total
        FROM
            movimento_lancamentos_financeiros l
        JOIN
            geral_classificadores c ON l.clf_id_tipo = c.clf_id
        WHERE
            c.clf_tipo = 'TIPO_LANCAMENTO' AND c.clf_codigo = 'RECEITA' AND
            l.lcf_data_pagamento >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '6 months')
        GROUP BY
            month
        ORDER BY
            month;
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_top_suppliers(start_date: date, end_date: date) -> list[dict]:
    """Retorna o top 5 fornecedores por valor."""
    query = """
        SELECT
            p.pcr_nome as nome,
            SUM(nf.ntf_valor_total) as total
        FROM
            cadastro_parceiros p
        JOIN
            movimento_notas_fiscais nf ON p.pcr_id = nf.pcr_id
        WHERE
            nf.ntf_data_emissao BETWEEN %s AND %s
        GROUP BY
            p.pcr_nome
        ORDER BY
            total DESC
        LIMIT 5;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_financial_entry_distribution(start_date: date, end_date: date) -> list[dict]:
    """Retorna a distribuição entre receita e despesa."""
    query = """
        SELECT
            c.clf_descricao as tipo,
            SUM(l.lcf_valor) as total
        FROM
            movimento_lancamentos_financeiros l
        JOIN
            geral_classificadores c ON l.clf_id_tipo = c.clf_id
        WHERE
            c.clf_tipo = 'TIPO_LANCAMENTO' AND
            l.lcf_data_pagamento BETWEEN %s AND %s
        GROUP BY
            c.clf_descricao;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_financial_status_distribution(start_date: date, end_date: date) -> list[dict]:
    """Retorna a distribuição por status (pago, pendente, vencido)."""
    query = """
        SELECT
            c.clf_descricao as status,
            COUNT(l.lcf_id) as count
        FROM
            movimento_lancamentos_financeiros l
        JOIN
            geral_classificadores c ON l.clf_id_status = c.clf_id
        WHERE
            c.clf_tipo = 'STATUS_LANCAMENTO' AND
            l.lcf_data_vencimento BETWEEN %s AND %s
        GROUP BY
            c.clf_descricao;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
