#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PY=$(command -v python3 || true)
if [ -z "$PY" ]; then
  echo "python3 não encontrado" >&2
  exit 1
fi

echo "Verificando processo Celery..."
if pgrep -f 'celery.*worker' >/dev/null; then
  echo "Celery worker: OK"
else
  echo "Celery worker não encontrado" >&2
fi

echo "Verificando servidor Django na porta 8000..."
if curl -sSf http://127.0.0.1:8000/ >/dev/null; then
  echo "Django (root): OK"
else
  echo "Django root não respondeu. Tente verificar logs em django.log" >&2
fi

# Verificar job status endpoint exist - usa ID 1 como exemplo
if curl -sSf http://127.0.0.1:8000/api/jobs/1/ >/dev/null; then
  echo "Endpoint /api/jobs/1/: responde (200/3xx)"
else
  echo "Endpoint /api/jobs/1/ não respondeu (pode ser 404 se não houver job com id=1)." 
fi

echo "Verificação finalizada. Para detalhes, veja django.log e celery.log"
