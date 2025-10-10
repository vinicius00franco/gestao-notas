#!/usr/bin/env bash
set -euo pipefail

# Script de inicialização para o projeto gestao_notas
# - carrega .env se existir
# - instala dependências opcionais (comentado)
# - aplica migrations
# - executa celery worker em background
# - inicia o servidor Django (dev)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Usando workspace: $ROOT_DIR"

# Carrega variáveis de ambiente de .env se o arquivo existir (modo seguro)
if [ -f .env ]; then
  echo "Carregando variáveis de .env"
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

# Checar python
PY=$(command -v python3 || true)
if [ -z "$PY" ]; then
  echo "Python3 não encontrado no PATH. Instale e tente novamente." >&2
  exit 1
fi

echo "Python encontrado: $PY"

# Aguarda Postgres ficar disponível antes das migrations
wait_for_postgres() {
  local host="${DB_HOST:-localhost}"
  local port="${DB_PORT:-5432}"
  local attempts="${DB_WAIT_ATTEMPTS:-60}"
  local sleep_s="${DB_WAIT_SLEEP:-1}"

  echo "Aguardando Postgres em ${host}:${port}..."
  # Tenta pg_isready se disponível
  if command -v pg_isready >/dev/null 2>&1; then
    for i in $(seq 1 "$attempts"); do
      if pg_isready -h "$host" -p "$port" >/dev/null 2>&1; then
        echo "Postgres disponível."
        return 0
      fi
      sleep "$sleep_s"
    done
    echo "pg_isready não confirmou Postgres após ${attempts}s; prosseguindo mesmo assim." >&2
    return 0
  fi

  # Fallback: tenta via TCP usando bash /dev/tcp
  for i in $(seq 1 "$attempts"); do
    if (echo > "/dev/tcp/${host}/${port}") >/dev/null 2>&1; then
      echo "Postgres disponível."
      return 0
    fi
    sleep "$sleep_s"
  done
  echo "Não foi possível confirmar Postgres em ${host}:${port} após ${attempts}s; tentando migrations mesmo assim." >&2
}

wait_for_postgres || true

echo "Aplicando migrations..."
# If a docker container named 'django_api' is running, prefer executing
# management commands inside the container. This avoids requiring Django
# installed on the host when the project is containerized.
if docker ps --format '{{.Names}}' | grep -q '^django_api$'; then
  echo "Detected 'django_api' container -> running migrations inside container"
  docker exec django_api python manage.py migrate --noinput || true

  echo "Attempting collectstatic inside container (may be skipped if not configured)..."
  docker exec django_api python manage.py collectstatic --noinput || \
    echo "collectstatic failed or STATIC_ROOT not configured inside container; continuing"

  echo "Django commands executed inside container. The container should be serving the app."
  echo
  echo "Ambiente iniciado via containers. Acesse: http://localhost/ (via nginx)"
  exit 0
fi

# If we reach here, there is no container; try to run locally but only if Django is
# available in the current Python environment. Otherwise instruct the user to use
# Docker or create a virtualenv and install requirements.
if ! "$PY" -c "import importlib, sys
try:
    importlib.import_module('django')
except Exception:
    sys.exit(1)
" >/dev/null 2>&1; then
  echo "Django não encontrado no ambiente local. Para desenvolvimento local, crie um venv e instale requirements.txt or use Docker Compose:" >&2
  echo "  python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt" >&2
  echo "Ou inicie via Docker: cd infra && docker compose up --build -d" >&2
  exit 1
fi

"$PY" manage.py migrate --noinput

echo "Coletando static files (opcional em dev)..."
"$PY" manage.py collectstatic --noinput || true

# Rodar Celery worker em background (usa módulo backend.celery)
echo "Iniciando Celery worker em background (logs: celery.log)..."
nohup "$PY" -m celery -A backend.celery:app worker -l info > celery.log 2>&1 &
CELERY_PID=$!
echo "Celery PID: $CELERY_PID"

# Iniciar servidor Django na porta 8000
echo "Iniciando Django dev server na porta 8000 (logs: django.log)..."
nohup "$PY" manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &
DJANGO_PID=$!
echo "Django PID: $DJANGO_PID"


# Aguarda readiness básico do Django antes de sair
echo "Aguardando Django responder (healthz)..."
ATTEMPTS=30
SLEEP=1
for i in $(seq 1 $ATTEMPTS); do
  if curl -sSf http://127.0.0.1:8000/healthz >/dev/null; then
    echo "Django pronto (healthz OK)"
    break
  fi
  sleep $SLEEP
done || true

echo
echo "Ambiente iniciado. Acesse: http://localhost:8000/"
echo "Para visualizar logs: tail -f django.log celery.log"
echo
echo "Para iniciar o aplicativo mobile, execute os seguintes comandos em um novo terminal:"
echo "cd mobile && npm install && npm start"
echo

exit 0
