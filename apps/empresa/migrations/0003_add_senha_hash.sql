-- Adiciona coluna senha_hash à tabela cadastro_empresas se não existir
ALTER TABLE IF EXISTS cadastro_empresas
  ADD COLUMN IF NOT EXISTS emp_senha_hash varchar(128);

-- Inicializa com string vazia para evitar nulls
UPDATE cadastro_empresas SET emp_senha_hash = '' WHERE emp_senha_hash IS NULL;

-- Se quiser tornar NOT NULL no futuro, remover o comentário abaixo após assegurar dados
-- ALTER TABLE cadastro_empresas ALTER COLUMN emp_senha_hash SET NOT NULL;
