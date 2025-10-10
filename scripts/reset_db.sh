#!/usr/bin/env bash
set -euo pipefail

# Carrega variáveis de ambiente para acesso ao banco
# Ordem de prioridade:
# 1. Argumentos de linha de comando: -U <user> -D <db>
# 2. Variáveis de ambiente já exportadas (ex: via `export`)
# 3. Arquivo .env no root do projeto
# 4. Arquivo .env.db no root do projeto

# --- Default values ---
# Valores padrão se nenhuma fonte (env/args) os definir
DB_USER_DEFAULT="test_user"
DB_NAME_DEFAULT="test_db"
DB_HOST_DEFAULT="localhost"
DB_PORT_DEFAULT="15432"
# Senha não tem padrão; deve ser definida em .env.db ou exportada
# Acessa o banco 'postgres' para tarefas administrativas
DB_MAINTENANCE_DB="postgres"

# --- Argument parsing ---
# Processa argumentos -U (user) e -D (database)
while getopts "U:D:" opt; do
  case "$opt" in
    U)
      DB_USER_OVERRIDE="$OPTARG"
      ;;
    D)
      DB_NAME_OVERRIDE="$OPTARG"
      ;;
    \?)
      echo "Uso: $0 [-U <user>] [-D <database>]" >&2
      exit 1
      ;;
  esac
done

# --- Environment loading ---
# Carrega .env e .env.db do diretório root do projeto
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -f "$ROOT_DIR/.env" ]; then
  echo "Carregando .env..."
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

if [ -f "$ROOT_DIR/.env.db" ]; then
  echo "Carregando .env.db..."
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env.db"
  set +a
fi

# --- Variable resolution ---
# Define as variáveis finais com base na prioridade
# POSTGRES_USER e POSTGRES_DB são as vars de .env.db
TARGET_DB_USER="${DB_USER_OVERRIDE:-${POSTGRES_USER:-$DB_USER_DEFAULT}}"
TARGET_DB_NAME="${DB_NAME_OVERRIDE:-${POSTGRES_DB:-$DB_NAME_DEFAULT}}"
TARGET_DB_HOST="${DB_HOST:-$DB_HOST_DEFAULT}"
TARGET_DB_PORT="${DB_PORT:-$DB_PORT_DEFAULT}"

# A senha deve ser definida em .env.db (POSTGRES_PASSWORD) ou exportada (PGPASSWORD)
# Se PGPASSWORD não estiver setada, psql pode falhar se o BD exigir senha
if [ -z "${POSTGRES_PASSWORD:-}" ] && [ -z "${PGPASSWORD:-}" ]; then
  echo "Aviso: POSTGRES_PASSWORD não está definido em .env.db nem PGPASSWORD exportado." >&2
  echo "A conexão pode falhar se o banco de dados exigir uma senha." >&2
else
  # Exporta PGPASSWORD para que psql a use automaticamente
  export PGPASSWORD="${POSTGRES_PASSWORD:-${PGPASSWORD:-}}"
fi

# --- Confirmation ---
# Pede confirmação ao usuário antes de apagar o banco
echo
echo "Você está prestes a apagar e recriar o banco de dados:"
echo "  Host:     $TARGET_DB_HOST:$TARGET_DB_PORT"
echo "  Database: $TARGET_DB_NAME"
echo "  Usuário:  $TARGET_DB_USER"
echo
read -p "Tem certeza que deseja continuar? (s/N): " -r CONFIRM
if [[ ! "$CONFIRM" =~ ^[sS]$ ]]; then
  echo "Operação cancelada."
  exit 0
fi

# --- Database reset logic ---
# Comandos SQL para dropar e recriar o banco e permissões
TERMINATE_CONNECTIONS_SQL="SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${TARGET_DB_NAME}';"
DROP_DB_SQL="DROP DATABASE IF EXISTS \"${TARGET_DB_NAME}\";"
CREATE_DB_SQL="CREATE DATABASE \"${TARGET_DB_NAME}\";"
GRANT_PRIVS_SQL="GRANT ALL PRIVILEGES ON DATABASE \"${TARGET_DB_NAME}\" TO \"${TARGET_DB_USER}\";"

# --- Execution ---
# Executa os comandos SQL no banco de manutenção (postgres)
echo
echo "Executando reset do banco de dados..."

CONTAINER_NAME="postgres_db"
# Verifica se o container do banco de dados está em execução
if ! sudo docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Erro: O container do banco de dados ('${CONTAINER_NAME}') não está em execução." >&2
    echo "Por favor, inicie o container com 'cd infra && sudo docker compose up -d db' e tente novamente." >&2
    exit 1
fi

# Executa o psql dentro do container para cada comando.
# A variável PGPASSWORD é passada para o container para autenticação.
# Não é necessário -h ou -p, pois o comando roda dentro do container.
sudo docker exec -e PGPASSWORD="${PGPASSWORD:-}" "${CONTAINER_NAME}" psql -U "$TARGET_DB_USER" -d "$DB_MAINTENANCE_DB" -c "$TERMINATE_CONNECTIONS_SQL"
sudo docker exec -e PGPASSWORD="${PGPASSWORD:-}" "${CONTAINER_NAME}" psql -U "$TARGET_DB_USER" -d "$DB_MAINTENANCE_DB" -c "$DROP_DB_SQL"
sudo docker exec -e PGPASSWORD="${PGPASSWORD:-}" "${CONTAINER_NAME}" psql -U "$TARGET_DB_USER" -d "$DB_MAINTENANCE_DB" -c "$CREATE_DB_SQL"
sudo docker exec -e PGPASSWORD="${PGPASSWORD:-}" "${CONTAINER_NAME}" psql -U "$TARGET_DB_USER" -d "$DB_MAINTENANCE_DB" -c "$GRANT_PRIVS_SQL"

# --- Post-reset instructions ---
# Informa o usuário sobre os próximos passos
echo
echo "Banco de dados '$TARGET_DB_NAME' foi recriado com sucesso."
echo "Agora você precisa rodar as migrations para recriar as tabelas:"
echo
echo "  # Se estiver usando Docker:"
echo "  docker exec django_api python manage.py migrate"
echo
echo "  # Se estiver rodando localmente:"
echo "  python manage.py migrate"
echo