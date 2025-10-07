-- Esta migração não altera os PKs numéricos (arriscado em produção).
-- Em vez disso, apenas garante que as colunas UUID existem e são únicas (já feitas em 0002).
-- Se for necessário ajustar metadados do campo id no Django, criar migration Python.

-- Verificar se existe índice para id (pk) - geralmente não é necessário alterar.

SELECT 1; -- noop
