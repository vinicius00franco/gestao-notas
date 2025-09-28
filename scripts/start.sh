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

# Carrega variáveis de ambiente de .env se o arquivo existir
if [ -f .env ]; then
  echo "Carregando variáveis de .env"
  # shellcheck disable=SC1091
  export $(grep -v '^#' .env | xargs)
fi

# Checar python
PY=$(command -v python3 || true)
if [ -z "$PY" ]; then
  echo "Python3 não encontrado no PATH. Instale e tente novamente." >&2
  exit 1
fi

echo "Python encontrado: $PY"

echo "Aplicando migrations..."
"$PY" manage.py migrate --noinput

echo "Coletando static files (opcional em dev)..."
"$PY" manage.py collectstatic --noinput || true

# Rodar Celery worker em background
echo "Iniciando Celery worker em background (logs: celery.log)..."
nohup "$PY" -m celery -A backend worker -l info > celery.log 2>&1 &
CELERY_PID=$!
echo "Celery PID: $CELERY_PID"

# Iniciar servidor Django na porta 8000
echo "Iniciando Django dev server na porta 8000 (logs: django.log)..."
nohup "$PY" manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &
DJANGO_PID=$!
echo "Django PID: $DJANGO_PID"

echo
echo "Ambiente iniciado. Acesse: http://localhost:8000/"
echo "Para visualizar logs: tail -f django.log celery.log"

exit 0
