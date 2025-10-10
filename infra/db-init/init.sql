-- Usar `\c` para conectar a um banco de dados específico, como 'postgres' ou 'template1'
-- A criação de usuários e bancos de dados geralmente é feita no nível do cluster,
-- não em um banco de dados específico, então este script pode ser executado
-- pelo usuário `postgres` padrão.

-- Criar o usuário (role) se ele ainda não existir.
-- A senha será definida a partir da variável de ambiente POSTGRES_PASSWORD.
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = '${POSTGRES_USER}') THEN

      CREATE ROLE "${POSTGRES_USER}" WITH LOGIN PASSWORD '${POSTGRES_PASSWORD}';
   END IF;
END
$do$;

-- Criar o banco de dados se ele ainda não existir, com o usuário criado como owner.
-- A variável :db_name é uma forma de passar o nome do banco para o script.
-- O comando `psql` pode passar variáveis com a opção -v.
-- No entanto, para o entrypoint do Docker, é mais seguro usar as variáveis de ambiente.
-- O script será executado em um contexto onde POSTGRES_DB está disponível.
-- A verificação da existência do banco é feita consultando `pg_database`.
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_database
      WHERE  datname = '${POSTGRES_DB}') THEN

      CREATE DATABASE "${POSTGRES_DB}"
      OWNER "${POSTGRES_USER}";
   END IF;
END
$do$;

-- Conceder todos os privilégios no banco de dados ao usuário.
-- Isso é redundante se o usuário for o `OWNER`, mas não causa problemas.
GRANT ALL PRIVILEGES ON DATABASE "${POSTGRES_DB}" TO "${POSTGRES_USER}";