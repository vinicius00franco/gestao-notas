from apps.notas.queries import get_top_fornecedores_pendentes as get_top_fornecedores_pendentes_query

def get_top_fornecedores_pendentes() -> list[dict]:
    return get_top_fornecedores_pendentes_query()
